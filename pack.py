import base64
from jinja2 import Template

template = Template(open('./src/__main__.py', 'r').read())
gdb_script = base64.b64encode(open('./src/gdb_script.py', 'rb').read())
print(template.render(script=gdb_script.decode('ascii')))
