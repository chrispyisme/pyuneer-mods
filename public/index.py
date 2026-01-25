#!/usr/bin/python3
import os

uri = os.environ.get("REQUEST_URI", "/")
method = os.environ.get("REQUEST_METHOD", "GET")
print("Content-Type: text/html\n\n")
print(f"URI: {uri}")
print(f"Method: {method}")