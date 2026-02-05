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
from lib.http.Request import Request
from lib.http.Response import Response 
from lib.routing.Router import Router
from lib.di.Container import Container
from lib.di.Autoloader import Autoloader
from app.controllers.middleware.InitView import InitView
from app.App import App

app = App(config="/usr/lib/cgi-bin/app/config/settings.json")

# Initialize autoloader to scan directories and build class registry                                                                                                                                                                                                                                                                                                                                                                                                            


app.run()

