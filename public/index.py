#!/usr/bin/python3
"""
Pyuneer CGI Entry Point - STEP 4: Routing
"""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.http.request import Request
from lib.http.response import Response
from lib.routing.router import Router

# Create router
router = Router()

# Define routes using decorators
@router.get('/')
def home(request):
    return f"""
    <h1>Pyuneer Framework - Routing Working!</h1>
    <p>Request: {request.method} {request.path}</p>
    <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/hello/world">Hello World</a></li>
        <li><a href="/user/john">User Profile</a></li>
        <li><a href="/api/info">API Info</a></li>
        <li><a href="/contact">Contact Form</a></li>
    </ul>
    """

@router.get('/hello/{name}')
def hello(request):
    name = request.params.get('name', 'Guest')
    return f"""
    <h1>Hello, {name}!</h1>
    <p>Your method was: {request.method}</p>
    <p>Your URI was: {request.path}</p>
    <a href="/">Go Back</a>
    """

@router.get('/user/{username}')
def user_profile(request):
    username = request.params.get('username', 'anonymous')
    return f"""
    <h1>User Profile: {username}</h1>
    <p>This is a practical route we'll use for our website.</p>
    """

@router.get('/contact')
def contact_form(request):
    return """
    <h1>Contact Us</h1>
    <form method="POST" action="/contact">
        <input type="text" name="name" placeholder="Your Name"><br>
        <input type="email" name="email" placeholder="Your Email"><br>
        <textarea name="message" placeholder="Your Message"></textarea><br>
        <button type="submit">Send</button>
    </form>
    <a href="/">Go Back</a>
    """

@router.post('/contact')
def contact_submit(request):
    name = request.get('name', 'Anonymous')
    email = request.get('email', 'No email')
    message = request.get('message', 'No message')
    
    return f"""
    <h1>Thank You, {name}!</h1>
    <p>We received your message:</p>
    <blockquote>{message}</blockquote>
    <p>We'll respond to: {email}</p>
    <a href="/">Go Home</a>
    <a href="/contact">Send Another</a>
    """

@router.get('/api/info')
def api_info(request):
    return {
        "framework": "Pyuneer",
        "version": "0.1.0",
        "status": "running",
        "request": {
            "method": request.method,
            "path": request.path,
            "headers": dict(request.headers)
        }
    }

def main():
    # Create request from CGI environment
    request = Request()
    
    # Dispatch to router
    response = router.dispatch(request)
    
    # Render response
    response.render()

if __name__ == '__main__':
    main()
