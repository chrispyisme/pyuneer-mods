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
        lib_paths = self._settings.get("autoload_paths", ["app", "lib"])
        self.container = Container()
        autoloader = Autoloader()
        autoloader.register_paths(lib_paths)
        autoloader.load()
        self.container.set_autoloader(autoloader)
        # Register base services FIRST
        self.container.factory("settings", self._settings)
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
        self._log.info("App initialization complete")
        self.router.add_route("/test", "GET", "app.controllers.routes.Home.Home@index", ["mw_init_view"])
    def run(self):
        """Run the application"""
        #self._log.info("App running - starting dispatch")


        
        # Dispatch
        self.router.dispatch(self.container)

        
        # Return error response
