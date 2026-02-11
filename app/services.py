def make_database(container, **params):
    host = params.get('host', 'localhost')
    user = params.get('user', 'pycgi')
    password = params.get('password', 'bf6912')
    database = params.get('database', 'httpstack')
    port = params.get('port', 3306)
    
    from lib.db.Database import Database
    return Database(host=host, user=user, password=password, database=database, port=port)



# Create factory for ActiveRecord tables
def make_active_record(container, **params):
    table_name = params.get('table', '')
    primary_key = params.get('primary_key', 'id')
    db = container.make('database')
    
    from lib.db.ActiveRecord import ActiveRecord
    return ActiveRecord(db, table_name, primary_key)