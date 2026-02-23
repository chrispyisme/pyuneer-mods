settings = {
    "document_root":"/usr/lib/cgi-bin",
    "app_root":"/app",
    "code_base":"/lib",
    "class_load":["/lib", "/app/controllers"],

    "file_load":{
        "templates":"/views/templates",
        "views":"/views/routes",
        "models":"/models/routes",
    },
    
    "base":{
        "template":"base.html",
        "assets": "/static/assets/enabled",
        "log_file": "/template.log"
        
    },
    "logger":{
        "log_dir": "/usr/lib/cgi-bin/app/logs",
        "format": "%(asctime)s [%(levelname)8s] %(filename)s:%(lineno)d - %(message)s"
    }
    
}
# Prepend document_root + app_root to file_load settings
file_load = settings["file_load"]
file_load = {namespace: f"{settings['document_root']}{settings['app_root']}{path}" 
             for namespace, path in file_load.items()}

class_load = settings["class_load"]
class_load = [f"{settings['document_root']}{p}" for p in class_load]

__all__ = ["settings", "class_load", "file_load"]