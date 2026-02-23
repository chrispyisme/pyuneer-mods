import sys
import os
from unittest import case

from lib.fs.files import FileSystem
from lib.logging.Logger import Logger
from lib.di.Container import Container
from lib.di.Autoloader import Autoloader, AutoloaderException
from lib.service.ServiceManager import ServiceManager
from .config import settings, class_load, file_load
from lib.routing.Router import Router
from .services.base import make_template_service
class App:
   
    def __init__(self):
        self._settings = settings
        log_file = "/App.log"
        log_dir = self._settings.get("logger", {}).get("log_dir")
        self._settings["log_file"] = log_dir + log_file
        format = self._settings.get("logger", {}).get("format")
        self._log = Logger(level="INFO", file=self._settings["log_file"], name="App.py", format=format)
        self._log.info("Init App")
        self.init_services_manager()
        self._log.info("loading base services")
        self.load_base_services()
        self.router:Router = self.service_manager.make("router")
        self._log.info("Router Set")
        self.fileloader = self.service_manager.make("fileloader")
        self._log.info("fileloader set")
        self.logger = self.service_manager.make("logger")
        self.logger.info("sm logger set")
        
    def load_base_services(self):
        self.service_manager.add_property("settings", self._settings)
        self.service_manager.add_property("service_manager", self.service_manager)
        self.service_manager.add_property("app", self)
        self.service_manager.add(abstract='logger', concrete="lib.logging.Logger.Logger", 
                                 service_type="singleton", 
                                 params={"level":"INFO", "file":self._settings["log_file"], "name":"sm", "format":"%(asctime)s [%(levelname)8s] %(name)s:%(filename)s:%(lineno)d - %(funcName)s() - %(message)s"})
        self.service_manager.add(abstract="response", concrete="lib.http.Response.Response", service_type="singleton")
        self.service_manager.add(abstract="Request", concrete="lib.http.Request.Request", service_type="factory")
        self.service_manager.add(abstract="router", concrete="lib.routing.Router.Router", service_type="singleton", params={"request":"Request"})
        self.service_manager.add(abstract="fileloader", concrete="lib.fs.files.FileSystem", service_type="singleton", 
                                 params={
                                     "directories":file_load
                                     })
        
        self.service_manager.add(abstract="template", concrete=make_template_service, service_type="singleton", params={"base_layout":"base.html", "assets":[]})
        
    def init_services_manager(self):
        self._log.info("Initializing Service Manager")
        self.container = Container()
        self._log.info("Composed Container")
        al = Autoloader(class_load)
        self._log.info("Initialized Autoloader")
        self.container.set_autoloader(al)
        
        self.service_manager = ServiceManager(self.container)
        self._log.info("Initialized ServMan")
        #print(self.service_manager.list_services())
                
    def get_container(self):
        return self.container
    
    def _POST(self, uri, handler, middleware):
        self.router.add_route(uri=uri, method="POST", handler=handler, middleware=middleware)
        
    def _GET(self, uri, handler, middleware):
        self.router.add_route(uri=uri, method="GET", handler=handler, middleware=middleware)
        return self
    
    def run(self):
        self.router.dispatch(self.container)
        