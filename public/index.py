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
from app.middleware.ResponseMiddleware import ResponseMiddleware
request = Request()
response = Response()
container = Container()
container.singleton("response", response)
container.singleton("request", request)
# Register response middleware in the container so routes can reference it
container.singleton('response_mw', ResponseMiddleware())

# Initialize autoloader to scan directories and build class registry
autoloader = Autoloader()
autoloader.register_paths(["app", "lib"]).load()
container.set_autoloader(autoloader)
uri = request.get_uri()
method = request.get_method()
router = Router(request=request)


def test_all(container, request,  **kwargs):
    id = kwargs.get("id", None)
    if id:
        custom_param = id
    custom_param = kwargs.get("custom_param", "no_param")
    response = container.make("response")
    response.set_status_code(200)
    response.set_content_type('text/html')
    response.set_body(f"custom_param: {custom_param}")
    response.send()
router.add_route(uri="/", method="GET", handler=test_all, middleware=['response_mw'], handler_params={"custom_param": "home"})
router.add_route(uri="/abc", method="GET", handler=test_all, middleware=['response_mw'])
router.add_route(uri="/api/example", method="GET", handler="app.controllers.TestController@index", middleware=['response_mw'], handler_params={"config": "custom_value"})
router.add_route(uri="/api/test_all/{id}", method="GET", handler=test_all, middleware=[])
router.add_route(uri="/user/*", method="GET", handler=test_all, middleware=['response_mw'], handler_params={"custom_param": "user_wildcard"})
router.dispatch(container)

