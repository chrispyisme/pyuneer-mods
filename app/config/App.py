from dataclasses import dataclass, field

class Settings:
    def __init__(self,scope):
        self.attributes = {}
        match scope:
            case "App":
               self.attributes = {
                   "autoload":["/usr/lib/cgi-bin/lib"],
                   "":"",
                   "":""
               } 
