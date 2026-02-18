#!/usr/bin/python3
"""
Public Entry Point - CGI Router (Step 4)

This module serves as the default HTTP endpoint for the public application.
It processes all incoming requests, extracts routing information, and
validates request parameters.

Responsibilities:
    - Initialize HTTP request and response objects
    - Extract and parse URI and HTTP method from the request
    - Return request metadata for routing validation
    - Serve as the entry point for public-facing routes

Returns:
    HTTP response containing the extracted method and URI for route processing.

Note:
    This is the Pyuneer CGI Entry Point - STEP 4 in the routing pipeline.
"""
import os
import sys
# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import re
from lib.di import Autoloader, AutoloaderException
from lib.di.Container import Container
from lib.http.Request import Request
from app.App import App

def handler_mw(c,req, nxt):
    res = c.make("response")
    res.set_status_code(200)
    res.set_header("Content-Type", "text/html")
    res.set_body("content")
    nxt()


reg = '\d+'
app = App()
app.router.register_middleware('handler_mw', "DocInit")
app._GET(uri="/api/{id:\d+}", handler="Home@index", middleware=['handler_mw'])
app._GET(uri="/{reg}", handler="Home@index", middleware=['handler_mw'])
app._GET(uri="/", handler="Home@index", middleware=['handler_mw'])
#app.router.use("public.index.handler_mw")
#app.router.register_middleware('handler_mw', handler_mw)


app.run()

