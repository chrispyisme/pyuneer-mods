#!/usr/bin/python3
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from lib.http.Response import Response

response = Response(status_code=302)
response.set_header("Location", "public/index.py")
response.send()
