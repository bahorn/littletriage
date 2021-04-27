#!/usr/bin/env python3
"""
Main Script
"""
import argparse
import base64
import json
import hashlib
import os
import subprocess
import time
import rpyc

# It gets imported by base64 with the packing script
PACKED = "{{ script }}"


amd64_registers = [
    'rax', 'rcx', 'rdx', 'rbx',
    'rsi', 'rdi', 'rsp', 'rbp',
    'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15'
]

class Analyzer:
    """
    Base class representing a tool to analyze a testcase.
    """
    def __init__(self):
        pass

    def analyze(self, testcase):
        """
        Check a testcase
        """

    def details(self):
        """
        Returns details about the tool
        """


class GDBAnalyzer(Analyzer):
    """
    GDB version of the analyzer.
    """
    conn = None

    def __init__(self,
                 binary,
                 binargs=[],
                 stdin=False,
                 timeout=30,
                 script_path='/tmp/.script.py',
                 wait_time=0.5,
                 memory=500000000):
        super().__init__()

        self.binary = binary
        self.binargs = binargs
        # as we use rpyc to talk to gdb we have to set these.
        self.host = '127.0.0.1'
        self.port = 1337
        self.timeout = timeout
        self.script_path = script_path
        # Essentially, how long to wait for GDB to start up and listen
        self.wait_time = wait_time
        self.stdin = stdin
        self.memory = memory

    def analyze(self, testcase):
        """
        Analyze the testcase
        """
        result = {}
        try:
            gdb = self.start_gdb()
            result = self.gdb_work(gdb, testcase)
            self.conn.close()
        except EOFError:
            # This happens in the case of timeouts.
            pass

        return result

    def _gdbcmd(self, params):
        """
        generates the args for the gdb cmd
        """
        args_s = 'py '
        args_l = [
            '{}="{}"'.format(key, value) for key, value in params.items()
        ]
        args_s += ';'.join(args_l)

        # Runs GDB by a timeout.
        # If it still hasn't finished after `timeout` time, it received a
        # SIGINT which should allow gdb to finish it's analysis so we can move
        # on.
        # Annoyingly, in somecases this timeout may cause GDB to coredump.
        gdb_cmd = [
            'timeout', '-s', 'INT', str(self.timeout),
            'gdb', '-nx', '--batch-silent',
            '-ex', args_s,
            '-x', self.script_path,
            self.binary
        ]

        return gdb_cmd

    def gdb_work(self, gdb, testcase):
        """
        this is the specific stuff we want gdb to do.
        """
        gdb.execute('set pagination off')
        # setup the crash handlers

        result = {}

        def backtracer(frame):
            """
            Gets the full stack backtrace
            """
            backtrace = []
            curr_frame = frame

            # while the api docs say gdb.Architecture should include the
            # registers, it actually doesn't at least on gdb 9.2, so we have to
            # manually handle x86s stuff here.

            registers = {}
            for register in amd64_registers:
                registers[register] = ('0x%016x' % 
                    curr_frame.read_register(register))

            while curr_frame is not None:
                backtrace.append(
                    {
                        'address': '0x%016x' % curr_frame.pc(),
                        'function': '%s' % curr_frame.name(),
                        'registers': registers
                    }
                )

                curr_frame = curr_frame.older()

            return backtrace


        def crash_handler(event):
            """
            Handles the crash handler
            """
            nonlocal result
            reason = ''
            backtrace = []
            try:
                reason = event.stop_signal
                frame = gdb.newest_frame()
                backtrace = backtracer(frame)
            except Exception as e:
                # we get a lot of non-real exceptions from rpyc, so we have to
                # skip over them like this.
                #print(e)
                pass
            
            # return the results
            result = {
                'reason': reason,
                'backtrace': backtrace
            }

        gdb.events.stop.connect(crash_handler)

        # quick way to test the timeout behavior
        # gdb.execute('!sleep 35')

        path = testcase.details()['path']

        # sort out the CLI args
        real = []
        for arg in self.binargs:
            if arg == '@@':
                real.append(path)
            else:
                real.append(arg)

        # Start the program in different ways depending on how it takes input
        # i.e, stdin or as a cli flag
        if self.stdin:
            gdb.execute(
                'starti %s < %s 2>/dev/null' % (" ".join(real), path)
            )
        else:
            gdb.execute('starti %s 2>/dev/null' % " ".join(real))

        # do stuff like setup memory limits here, before progressing past the
        # entry point.
        inferior = gdb.selected_inferior()
        # hack to limit the memory of a child process.
        # requires modern linux, greater than 2.6.36.
        prlimit = \
            '!prlimit --pid %i --core=unlimited --as=%i' % \
                (inferior.pid, self.memory)
        gdb.execute(prlimit)

        # and now start
        gdb.execute('c')

        # now we wait til an error occurs.
        while True:
            thread = gdb.selected_thread()
            if thread and thread.is_running():
                time.sleep(0.01)
            else:
                break
        return result

    @staticmethod
    def _write_script(path):
        """
        Dumps GDB script to disk, so it can be used.
        """
        file = base64.b64decode(PACKED)
        filep = open(path, 'wb')
        filep.write(file)
        filep.close()
        return path

    def start_gdb(self):
        """
        Gets are gdb object so we can start doing things with it.
        """
        # First, we need to place the gdb bootstrap script onto disk.
        GDBAnalyzer._write_script(self.script_path)
        # invoke GDB.
        cmd = self._gdbcmd({'HOSTNAME': self.host, 'PORT': self.port})
        GDBAnalyzer.execute(cmd)
        time.sleep(self.wait_time)
        # Now connect to the GDB instance.
        self.conn = rpyc.connect("localhost", 1337)
        return self.conn.root.gdb()

    @staticmethod
    def execute(cmd):
        """
        wrapper to handle run a process
        """
        return subprocess.Popen(cmd)


class MetaAnalyzer(Analyzer):
    """
    Gets metadata on the testcase.
    """

    def analyze(self, testcase):
        """
        Analyzes the testcase

        We get the following:
        * file size
        * shasum
        """
        file_path = testcase.details()['path']
        file_size = os.path.getsize(file_path)
        file_hash = MetaAnalyzer._hash(file_path)
        return {
            'path': file_path,
            'size': file_size,
            'hash': file_hash
        }

    @staticmethod
    def _hash(name):
        file = open(name, 'rb')
        fhash = hashlib.sha256()
        fhash.update(file.read())
        file.close()
        return fhash.hexdigest()


class Testcase:
    """
    Represents testcase instances
    """
    results = {}

    def __init__(self, name, testcase_path):
        self.name = name
        self.file = testcase_path

    def details(self):
        """
        Gets the details of this testcase
        """
        return {'name': self.name, 'path': self.file, 'analysis': self.results}

    def update(self, key, value):
        """
        Store results with the testcase
        """
        self.results[key] = value


class TriageTool:
    """
    The user focused tool
    """
    all_testcases = {}
    all_analyzers = {}

    def __init__(self, testcase_path, binary, binargs, stdin=False, timeout=30,
                 wait_time=0.5, memory=5000000000):
        self.testcase_path = testcase_path
        self.testcases()

        # define all supported the analyzers here
        meta = MetaAnalyzer()
        gdb = GDBAnalyzer(binary, binargs, stdin=stdin, timeout=timeout,
                          wait_time=wait_time, memory=memory)
        self.all_analyzers = {
            'meta': meta,
            'gdb': gdb
        }

    def run(self):
        """
        Runs though and analyzes all the testcases
        """
        results = []
        for _, testcase in self.all_testcases.items():
            for analyzer_name, analyzer in self.all_analyzers.items():
                testcase.update(analyzer_name, analyzer.analyze(testcase))
            results.append(testcase.details())
        
        return results

    def testcases(self):
        """
        Find all the testcases in a path
        """
        for testcase in os.scandir(self.testcase_path):
            if testcase.is_file():
                full_path = '{}/{}'.format(
                    self.testcase_path,
                    testcase.name
                )
                self.all_testcases[full_path] = Testcase(
                    testcase.name,
                    full_path
                )


def save(fname, data):
    output = open(fname, 'w')
    obj = {'crashes': tool.run()}
    output.write(json.dumps(obj))
    output.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='The Little Triage Tool That Could')
    parser.add_argument(
        '--stdin',
        help='the program takes stdin',
        action='store_const',
        const=True
    )
    parser.add_argument(
        '--timeout',
        help='time before sending a SIGINT',
        type=int,
        default=30
    )
    parser.add_argument(
        '--wait-time',
        help='time to sleep before attempting to connect to gdb',
        type=float,
        default=0.5
    )
    parser.add_argument(
        '--memory',
        help='memory limit for the child process (bytes)',
        type=int,
        default=500000000
    )
    parser.add_argument(
        '--output',
        help='file to write the results to',
        type=str,
        default='/dev/stdout'
    )
    parser.add_argument(
        'testcase_dir',
        help='path to testcases'
    )
    parser.add_argument(
        'binary',
        nargs='*',
        help='binary to triage'
    )
    args = parser.parse_args()

    tool = TriageTool(
        args.testcase_dir,
        binary=args.binary[0],
        binargs=args.binary[1:],
        stdin=args.stdin,
        timeout=args.timeout,
        wait_time=args.wait_time,
        memory=args.memory
    )

    result = tool.run()

    save(args.output, result)
    
