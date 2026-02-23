def make_template_service( c, base_layout='',  assets=[]): 
    print(c)                                                                                                                          
    sm = c.get_property("service_manager")                                                                  
    settings = sm.get_property("settings")
    return settings
