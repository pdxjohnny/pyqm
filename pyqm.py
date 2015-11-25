"""
File: gitlab_webhooks/app.py
Author: John Andersen
Description: A webserver to receive json web hooks from gitlab_webhooks
    The hooks are dealt with by calling the corresponding function in
    hooks.py. For example a push is received so the function push in
    hook.py is called and passed the hook data.

Crontab line to run on reboot
@reboot /usr/bin/python /path/to/gitlab_webhooks/app.py 9898
"""
import sys
import json
import thread
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn

PORT = 9898
ADDRESS = "0.0.0.0"

class Handler(BaseHTTPRequestHandler):
    """
    Handles post requests
    """

    def do_POST(self):
        """
        Sends a 200 to the client and starts a new thread to
        execute the proper hook function
        """
        # Send the client a success reponse
        self.send_response(200)
        self.end_headers()
        self.wfile.write('\n')
        # Get the length of the post data
        content_len = int(self.headers.getheader('content-length', 0))
        # Read the post data
        post_body = self.rfile.read(content_len)
        # Load the post data from its json form to a dict
        post_body = json.loads(post_body)
        # Start a thread to deal with the received hook
        thread.start_new_thread(hook_received, (post_body, ))
        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

def hook_received(hook):
    """
    Calls the hook function in the file hooks.py
    """
    # Get the hook module, _m is for module
    exec_module = __import__('scripts.' + hook["_m"], fromlist=[''])
    # Make sure its up to date
    reload(exec_module)
    # Get the hook function, _f is for function
    exec_hook = getattr(exec_module, hook["_f"])
    # Delete the info thats not needed
    del hook["_m"]
    del hook["_f"]
    # Call the function and pass it the hook
    return exec_hook(hook)

def start(port=PORT, address=ADDRESS):
    """
    Starts the webserver
    """
    server = ThreadedHTTPServer((address, port), Handler)
    server.serve_forever()

def main():
    """
    Starts the webserver, first argument is port number, default is 9898
    """
    port = PORT
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    start(port)

if __name__ == '__main__':
    main()
