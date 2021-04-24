"""
GDB triage script
"""
import os
import gdb

data = []


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

    data.append(result)


def main():
    """
    Entrypoint for this gdb script
    """
    # Setup communication with parent process

    # Do the work
    gdb.execute('set pagination off')
    gdb.events.stop.connect(crash_handler)
    gdb.execute("r {} 2>/dev/null".format(full_path))
    gdb.execute("q")


main()
