
import os
import sys
import threading
import time
import psutil
import signal
from subprocess import Popen, DEVNULL
from flask import Flask, request, make_response
from flask_restx import Resource, Api
from werkzeug.serving import make_server

browser_pid = None

class MyResource(Resource):
    def __init__(self, *class_args, **kwargs):
        if 'shutdown_server' in kwargs:
            self.shutdown_server = kwargs['shutdown_server']
        super().__init__(*class_args, **kwargs)
    
    def html_response(self, html):
        response = make_response()
        response.set_data(html)
        response.status_code = 200
        response.headers['Content-Type'] = 'text/html'
        return response


class WebServer(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        assert isinstance(host, str) and not host.strip() == '', 'host param is required'
        assert isinstance(port, int), 'port param must be an integer'
        
        self.app = app = Flask(__name__)
        self.host = host
        self.port = port
        self.api = Api(self.app)
        self.srv = make_server(self.host, self.port, self.app)
        self.is_running = True

        @self.api.route('/home')
        class home(MyResource):
            def get(self):
                return self.html_response(
                    """
<input type="button" value="Click to shutdown server" 
    onclick="window.location.href='/shutdown'">
""")


        @self.api.route('/shutdown', resource_class_kwargs={'shutdown_server': self.start_shutdown})
        class my_res(MyResource):
            def get(self):
                self.shutdown_server()
                return self.html_response("Server is being shut down")

        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.srv.serve_forever()

    def _do_shutdown(self):
        self.srv.shutdown()

    def start_shutdown(self):
        global browser_pid
        if self.is_running:
            self.is_running = False
            time.sleep(0.5)
            print("Server being shut down")
            t = threading.Thread(target=self._do_shutdown)
            t.start()

        _p = psutil.Process(browser_pid)
        if _p.is_running() and not _p.status() == psutil.STATUS_ZOMBIE:
            print("Closing browser")
            kill_proc_tree(browser_pid)



def main(argv):
    global browser_pid
    host='127.0.0.1'
    port=9991
    web_server = WebServer(host, port)
    web_server.start()

    browser_proc = Popen(f'google-chrome http://{host}:{port}/home', shell=True, stdin=None, stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
    browser_pid = browser_proc.pid

    # Watch for browser being closed
    while web_server.is_running:
        try:
            _p = psutil.Process(browser_pid)
            _p_status = _p.status()
            if _p_status == psutil.STATUS_ZOMBIE: 
                break
        except psutil.NoSuchProcess:
            break
        time.sleep(0.5)

    if web_server.is_running:
        print("Browser was closed by user")
        web_server.start_shutdown()



            
# Verbatum copy from https://psutil.readthedocs.io/en/latest/
def kill_proc_tree(pid, sig=signal.SIGTERM, include_parent=True,
                   timeout=None, on_terminate=None):
    """Kill a process tree (including grandchildren) with signal
    "sig" and return a (gone, still_alive) tuple.
    "on_terminate", if specified, is a callback function which is
    called as soon as a child terminates.
    """
    assert pid != os.getpid(), "won't kill myself"
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    if include_parent:
        children.append(parent)
    for p in children:
        try:
            p.send_signal(sig)
        except psutil.NoSuchProcess:
            pass
    gone, alive = psutil.wait_procs(children, timeout=timeout,
                                    callback=on_terminate)
    return (gone, alive)


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except Exception as ex:
        raise ex
