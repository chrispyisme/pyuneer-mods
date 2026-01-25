#!/usr/bin/python3
import os
import sys

print("Content-Type: text/html\n")
print("<h1>Pyuneer Framework</h1>")
print("<p>Structure is set up! Next: Rewrite rules.</p>")
print(f"<pre>SCRIPT_NAME: {os.environ.get('SCRIPT_NAME', '')}</pre>")