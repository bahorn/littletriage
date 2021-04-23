import gdb
import os
import json

data = []
gdb.execute('set pagination off')
BASE_DIR = '/fuzz/inputs/'

testcase = ""

def crash_handler(event):
    full_path = BASE_DIR + testcase
    reason = event.stop_signal
    backtrace = []
    try:
        first = gdb.newest_frame()
        while first != None:
            
            backtrace.append(
                {
                    'address': '0x%8x' % first.pc(), 
                    'function': '%s' % first.name()
                }
            )

            first = first.older()
    except gdb.error: 
        return
    
    result = {
        'testcase': testcase,
        'size': os.path.getsize(full_path),
        'reason': reason,
        'backtrace': backtrace
    }
    
    print(result)

    data.append(result)

gdb.events.stop.connect(crash_handler)

testcases = os.listdir(BASE_DIR)
for testcase in filter(lambda x: 'id' in x, testcases):
    full_path = BASE_DIR + testcase
    gdb.execute("r {} 2>/dev/null".format(full_path))

open('../out.json', 'w').write(json.dumps(data))

gdb.execute("q")
