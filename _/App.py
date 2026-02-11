import sys
import os
sys.path.insert(0,"/usr/lib/cgi-bin")
from lib.fs.files import FileSystem
from lib.logging.Logger import Logger
from lib.di import Container, Autoloader
from app.config import paths
class App:
    def __init__(self):
        self._settings = paths
        self.container = Container()
        self.doc_root = paths["document_root"]
        self.app_root = f"{self.doc_root}{paths['app_root']}"
        
        class_load = paths["class_load"]
        class_load = [f"{self.doc_root}{p}" for p in class_load]
        al = Autoloader(class_load)
        self.container.set_autoloader(al)
        self.make_services()
        self.loader = self.container.make("file_loader")
        self.router = self.container.make("router")
        response = self.container.make("response")
        
        response.set_body("my content")
        response.send()
        
    def make_services(self):
        self.container.singleton("request", "lib.http.Request.Request")
        """
        FileSystem Service
            Get the directories to map so base filenames can be used 
            and resolved to the complete abs path. 
            Initialize the file_loader with the directories list in the 
            self._settings['file_load']
            
        HTTP Services
            Response / Request services to simulate the user request
            and generate the appropriate response.
            
        Routing Services
            Route / Router services for managing routes and the relationships
            to handlers and middleware.
        """
        directories = self._settings.get("file_load", {})
        # prepend the paths with the application root
        directories = {namespace: f"{self.app_root}{path}" for namespace, path in directories.items()}
        self.container.singleton("file_loader", "lib.fs.files.FileSystem", directories=directories)
        request = self.container.make("lib.http.Request.Request")
        self.container.singleton("router", "lib.routing.Router.Router", request=request)
        self.container.singleton("response", "lib.http.Response.Response")
        
    def init_logger(self):                               
            # Init logger
        log_format = self._settings.get("log_format", "%(asctime)s [%(levelname)s] %(message)s")
        self._log = Logger(
            level="INFO",
            file="/usr/lib/cgi-bin/app/logs/_/App.log",
            format=log_format,
            name="/_/App.py"
        )
        
