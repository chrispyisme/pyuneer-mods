import os
import sys
from pathlib import Path
from app.controllers.middleware.InitView import InitView
from lib.fs.files import FileSystem
from lib.di.Container import Container
from lib.di.Autoloader import Autoloader
from lib.http import Response
from lib.logging.Logger import Logger

class App:
    def __init__(self, config: str):

        # Load settings from config file
        self._settings = FileSystem.parse_config_file(config)
    
    # Init logger
        log_format = self._settings.get("log_format", "%(asctime)s [%(levelname)s] %(message)s")
        self._log = Logger(
            level="INFO",
            file="/usr/lib/cgi-bin/app/logs/App.log",
            format=log_format,
            name="App"
        )
        
        #self._log.info(f"App initializing with config: {config}")
        
        # Get paths
        paths = self._settings.get("paths", {})
        document_root = paths.get("document_root", "/usr/lib/cgi-bin")
        
        # Initialize container and filesystem
        self.container = Container()
        self.container.factory("settings", self._settings)
                # Set up autoloader BEFORE adding routes
        lib_paths = self._settings.get("autoload_paths", ["app", "lib"])
        autoloader = Autoloader()
        
        # Build proper paths
        full_paths = []
        for p in lib_paths:
            if p.startswith('/'):
                full_path = os.path.join(document_root, p.lstrip('/'))
            else:
                full_path = os.path.join(document_root, p)
            full_paths.append(full_path)
        
        # Also add document_root for complete scanning
        full_paths.append(document_root)
        
        autoloader.register_paths(full_paths)
        autoloader.load()
        self.container.set_autoloader(autoloader)
        # Register base services FIRST
        self.container.singleton("router", "lib.routing.Router.Router")
        self.container.singleton("request", "lib.http.Request.Request")
        self.container.singleton(Response, "lib.http.Response.Response")
        
        request = self.container.make("request")
        self.router = self.container.make("router", request=request)


        

       
            # Register middleware
        def mw_init_view(container, request, nxt):
            #self._log.info("Init Middleware executing")
            mw = InitView(container)
            mw.handle(container, request, nxt)

        self.container.singleton("mw_init_view", mw_init_view)
        self.router.register_middleware("mw_init_view", mw_init_view)
        #self._log.info("App initialization complete")
        self.router.add_route("/", "GET", "app.controllers.routes.Home.Home@index")
    def run(self):
        """Run the application"""
        #self._log.info("App running - starting dispatch")

        # FIX: Get the actual path from environment
        import os
        path_info = os.environ.get('PATH_INFO', '')
        
        # Clean up the path
        if path_info.endswith('/index.py') or path_info.endswith('/index'):
            path_info = path_info.replace('/index.py', '').replace('/index', '')
        
        if not path_info or path_info == '/cgi-bin/public/index.py':
            path_info = '/'
        
        #self._log.info(f"Final path to dispatch: {path_info}")
        
        # Dispatch
        self.router.dispatch(self.container)

        
        # Return error response
        response = self.container.make(Response)
        response.set_status_code(500)
        response.set_body(f"""
        <h1>Server Error</h1>
        <pre>{str(e)}</pre>
        <p>Check the application logs for details.</p>
        """)
