paths = {
    "document_root":"/usr/lib/cgi-bin",
    "app_root":"/app",
    "code_base":"/lib",
    "class_load":["/lib", "/app/controllers"],

    "file_load":{
        "templates":"/views/templates",
        "views":"/views/routes",
        "models":"/models/routes",
    }
}

__all__ = ["paths"]