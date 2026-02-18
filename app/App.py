import sys
import os
sys.path.insert(0,"/usr/lib/cgi-bin")
from lib.fs.files import FileSystem
from lib.logging.Logger import Logger
from lib.di import Container, Autoloader
from lib.service.ServiceManager import ServiceManager
from app.config import settings, class_load, file_load
from lib.routing.Router import Router
class App:
   
    def __init__(self):
        self._settings = settings
        self.init_services_manager()
        self.load_base_services()
        self.router:Router = self.service_manager.make("router")
        self.fileloader = self.service_manager.get_service("fileloader")
        
    def load_base_services(self):
        self.service_manager.add_property("service_manager", self.service_manager)
        self.service_manager.add_property("app", self)
        self.service_manager.add(abstract="response", concrete="lib.http.Response.Response", service_type="singleton")
        self.service_manager.add(abstract="Request", concrete="lib.http.Request.Request", service_type="factory")
        self.service_manager.add(abstract="router", concrete="lib.routing.Router.Router", service_type="singleton", params={"request":"Request"})
        self.service_manager.add(abstract="fileloader", concrete="lib.fs.files.FileSystem", service_type="singleton", 
                                 params={
                                     "directories":file_load
                                     })
        self.service_manager.add_property("settings", self._settings)
        
        
    def init_services_manager(self):
        self.container = Container()
        al = Autoloader(class_load)
        self.container.set_autoloader(al)
        self.service_manager = ServiceManager(self.container)
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
        