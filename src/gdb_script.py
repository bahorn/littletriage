"""
script to be ran by GDB.

Invoke it like:
gdb --batch-silent -nx -ex "py PORT=1337" --command=gdb_script.py
"""
import rpyc
import gdb

# Default Settings
if 'HOSTNAME' not in locals():
    HOSTNAME = '127.0.0.1'

if 'PORT' not in locals():
    PORT = 18861


# The Service
class GDBService(rpyc.Service):
    def on_disconnect(self, conn):
        gdb.execute('quit')

    def exposed_gdb(self):
        return gdb


if __name__ == "__main__":
    from rpyc.utils.server import OneShotServer
    server = OneShotServer(
        GDBService,
        hostname=HOSTNAME,
        port=PORT,
        protocol_config={
            'allow_public_attrs': True,
        }
    )
    server.start()
