#!/usr/bin/python3
"""
Pyuneer CGI Entry Point - STEP 2: Working Rewrite
"""
import os
import sys

def main():
    # Get the path from rewrite
    script_name = os.environ.get('SCRIPT_NAME', '')
    path_info = os.environ.get('PATH_INFO', '')
    
    # Determine actual URI
    if path_info:
        uri = path_info
    elif 'REQUEST_URI' in os.environ:
        uri = os.environ['REQUEST_URI'].split('?')[0]
    else:
        uri = '/'
    
    # Get query string
    query_string = os.environ.get('QUERY_STRING', '')
    
    print("Content-Type: text/html\n")
    print("<h1>Pyuneer Framework - Rewrite Working!</h1>")
    print(f"<h2>URI: {uri}</h2>")
    print(f"<h3>Method: {os.environ.get('REQUEST_METHOD', 'GET')}</h3>")
    
    if query_string:
        print(f"<p>Query: {query_string}</p>")
    
    # Show all environment variables (for debugging)
    print("<hr><h4>Debug Info:</h4>")
    print("<ul>")
    for key in sorted(os.environ.keys()):
        if key.startswith('HTTP_') or key in ['REQUEST_METHOD', 'PATH_INFO', 'QUERY_STRING', 'SCRIPT_NAME']:
            print(f"<li><strong>{key}:</strong> {os.environ[key]}</li>")
    print("</ul>")

if __name__ == '__main__':
    main()