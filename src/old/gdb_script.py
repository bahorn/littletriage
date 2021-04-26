"""
GDB triage script
"""
import os
import json
import gdb

def backtracer(frame):
    """
    Gets the full stack backtrace
    """
    backtrace = []
    curr_frame = frame

    while curr_frame is not None:
        backtrace.append(
            {
                'address': '0x%8x' % curr_frame.pc(),
                'function': '%s' % curr_frame.name()
            }
        )

        curr_frame = curr_frame.older()

    return backtrace


def crash_handler(event):
    """
    Handles the event
    """
    reason = event.stop_signal
    backtrace = []
    try:
        frame = gdb.newest_frame()
        backtrace = backtracer(frame)
    except gdb.error:
        return

    # testcase is defined as a global by the invoker
    result = {
        'testcase': testcase,
        'size': os.path.getsize(testcase),
        'reason': reason,
        'backtrace': backtrace
    }
    f = open('{}.analysis'.format(os.path.basename(testcase)), 'w')
    f.write(json.dumps(result))
    f.close()

def exit_handler(event):
    """
    exit handler
    """

    result = {
        'testcase': testcase,
        'size': os.path.getsize(testcase),
        'reason': reason,
    }
    f = open('{}.analysis'.format(os.path.basename(testcase)), 'w')
    f.write(json.dumps(result))
    f.close()



gdb.execute('set pagination off')
gdb.events.stop.connect(crash_handler)
gdb.events.exited.connect(exited_handler)
gdb.execute("starti {} 2>/dev/null".format(testcase))
# cap the memory usage
# gdb.execute('call setrlimit(9, {409600, -1})')
gdb.execute('c')
gdb.execute("q")
