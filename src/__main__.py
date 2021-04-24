#!/usr/bin/env python3
"""
aafe
"""
import base64
import os
import sys
import subprocess

PACKED = "{{ script }}"

def gdbcmd(args, script_path, binary, timeout):
    """
    generates the args for the gdb cmd
    """
    args_s = 'py '
    args_l = ['{}={}'.format(key, value) for key, value in args.items()]
    args_s += ';'.join(args_l)

    # Runs GDB by a timeout.
    # If it still hasn't finished after `timeout` time, it received a SIGINT
    # which should allow gdb to finish it's analysis so we can move on.
    gdb_cmd = [
        'timeout', '-s', 'INT', timeout,
        'gdb', '-nx', '--batch-silent',
        '-ex', args_s,
        '-x', script_path,
        binary
    ]

    return gdb_cmd


def write_script(path):
    """
    Dumps GDB script to disk, so it can be used.
    """
    file = base64.b64decode(PACKED)
    f = open(path, 'wb')
    f.write(file)
    f.close()
    return path


def execute(cmd):
    """
    wrapper to handle run a process
    """
    return subprocess.run(cmd)


def gdbexec(args, script_path, binary, timeout=35):
    """
    runs gdb with what we need
    """
    cmd = gdbcmd(args, script_path, binary, timeout=timeout)
    return execute(cmd)


def main():
    """
    Entrypoint
    """
    binary = sys.argv[1]
    testcase_dir = sys.argv[2]
    script = write_script('/tmp/script.py')

    for testcase in os.listdir(testcase_dir):
        full_path = '{}/{}'.format(
            testcase_dir,
            testcase
        )
        print(gdbcmd({'testcase': full_path}, script, binary, 30))


if __name__ == "__main__":
    main()
