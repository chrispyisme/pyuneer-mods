"""app.datasources.db_datasource - Database Datasource

Persists data to a relational database via Database/QueryBuilder.

Origin:
    Converted from PHP HTTPStack v2 Core/Datasource DBDatasource.
    
Changelog:
    - 2026-01-30: Converted from PHP. DBDatasource for database persistence.
    - 2026-01-30: Updated update() and delete() to use unified query format.
        * Intelligently separates WHERE from update values using db.select().
        * Format: {"collection": ["col": match_value, "col_to_update": new_value]}

Usage:
    from app.datasources.db_datasource import DBDatasource
    from lib.db.Database import Database
    
    db = Database(config)
    ds = DBDatasource(db, 'users', primary_key='id', read_only=False)
    
    ds.create({'name': 'Alice', 'email': 'alice@example.com'})
    results = ds.read({'active': True})
    ds.update({'id': 1}, {'email': 'newemail@example.com'})
    ds.delete({'id': 1})
    
    # Set row context
    ds.set_row_id(5)
    row_id = ds.get_row_id()  # 5

Database Interface Expected:
    db.insert(table, payload) -> record_id or None
    db.select(table, where=None) -> List[Dict]
    db.update(table, payload, where=Dict) -> count or None
    db.delete(table, where=Dict) -> count or None

Best For:
    - Large datasets
    - Multi-user applications
    - ACID transactions
    - Complex queries
    - Production systems
"""

from typing import Any, Dict, List, Optional, Union
from app.datasources.abstract import AbstractDatasource
from lib.db.QueryBuilder import QueryBuilder


class DBDatasource(AbstractDatasource):
    """Datasource backed by a relational database.
    
    Wraps Database/QueryBuilder for CRUD operations.
    Supports row_id context for single-record operations.
    
    Raises Exception on write attempts if read_only=True.
    """
    
    def __init__(self, db, table_name: str, primary_key: str = 'id', read_only: bool = True):
        """
        Initialize with a database connection and table name.
        
        Args:
            db: Database connection object (e.g., from lib.db.Database)
            table_name: Name of the table
            primary_key: Primary key column (default: 'id')
            read_only: If True, prevents write operations
        """
        super().__init__(read_only)
        self.db = db
        self.table_name = table_name
        self.primary_key = primary_key
        self.row_id = -1
    
    def set_row_id(self, row_id: int) -> None:
        """Set the current row ID context."""
        self.row_id = row_id
    
    def get_row_id(self) -> int:
        """Get the current row ID context."""
        return self.row_id
    
    def create(self, payload: Dict[str, Any], params: Optional[Dict[str, Any]] = None) -> bool:
        """Create a new record using new unified format.
        
        Format: {"collection": [{"id": 1, "name": "Alice"}]}
        """
        if self.read_only:
            raise Exception("Datasource is read-only.")
        
        try:
            # Handle new format {"collection": [record_data]}
            if isinstance(payload, dict) and len(payload) == 1:
                collection_name = list(payload.keys())[0]
                specs = payload[collection_name]
                
                if isinstance(specs, list) and len(specs) > 0:
                    # Create record from list (first item)
                    record_data = specs[0] if isinstance(specs[0], dict) else {}
                elif isinstance(specs, dict):
                    record_data = specs
                else:
                    return False
            else:
                record_data = payload
            
            # Prefer higher-level DB API if available (ActiveRecord-like)
            if hasattr(self.db, 'create') and callable(self.db.create):
                try:
                    res = self.db.create(record_data)
                    return res is not None
                except TypeError:
                    pass

            # If DB provides insert(table, data)
            if hasattr(self.db, 'insert') and callable(self.db.insert):
                try:
                    res = self.db.insert(self.table_name, record_data)
                    return res is not None
                except Exception:
                    pass

            # Fallback to QueryBuilder + low-level execute
            try:
                qb = QueryBuilder(self.table_name)
                query, params = qb.build_insert(record_data)
                if hasattr(self.db, 'execute_query'):
                    self.db.execute_query(query, params)
                    return True
            except Exception:
                pass

            return False
        except Exception as e:
            print(f"DBDatasource.create error: {e}")
            return False
    
    def read(self, query: Optional[Dict[str, Any]] = None, filter_: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Read records using new unified format.
        
        Format:
        - Read all: {"collection": []}
        - Read with WHERE: {"collection": ["col": value]}
        - Read with columns: {"collection": ["col1", "col2"]}
        """
        try:
            # Handle new unified format
            if isinstance(query, dict) and len(query) == 1:
                collection_name = list(query.keys())[0]
                specs = query[collection_name]
                
                if isinstance(specs, list) and len(specs) == 0:
                    # Return all records
                    if hasattr(self.db, 'read'):
                        return getattr(self.db, 'read')() .all() if hasattr(getattr(self.db, 'read')(), 'all') else getattr(self.db, 'read')()
                    if hasattr(self.db, 'select'):
                        return self.db.select(self.table_name) or []
                    qb = QueryBuilder(self.table_name).select()
                    query, params = qb.build_select()
                    return (self.db.fetch_all(query, params) if hasattr(self.db, 'fetch_all') else []) or []
                elif isinstance(specs, dict):
                    # WHERE conditions - prefer ActiveRecord-like read
                    if hasattr(self.db, 'read'):
                        res = self.db.read(specs)
                        return res.all() if hasattr(res, 'all') else res
                    if hasattr(self.db, 'select'):
                        return self.db.select(self.table_name, where=specs) or []
                    qb = QueryBuilder(self.table_name).select().where(specs)
                    query, params = qb.build_select()
                    return (self.db.fetch_all(query, params) if hasattr(self.db, 'fetch_all') else []) or []
                elif isinstance(specs, list) and all(isinstance(s, str) for s in specs):
                    # Column selection
                    if hasattr(self.db, 'read'):
                        # ActiveRecord.read may accept a dict of columns; try via QueryBuilder fallback
                        qb = QueryBuilder(self.table_name).select(specs)
                        query, params = qb.build_select()
                        return (self.db.fetch_all(query, params) if hasattr(self.db, 'fetch_all') else []) or []
                    if hasattr(self.db, 'select'):
                        return self.db.select(self.table_name, columns=specs) or []
                    qb = QueryBuilder(self.table_name).select(specs)
                    query, params = qb.build_select()
                    return (self.db.fetch_all(query, params) if hasattr(self.db, 'fetch_all') else []) or []
            
            # Fallback for old format
            if query is None:
                if hasattr(self.db, 'read'):
                    res = self.db.read()
                    return res.all() if hasattr(res, 'all') else res
                if hasattr(self.db, 'select'):
                    return self.db.select(self.table_name) or []
                qb = QueryBuilder(self.table_name).select()
                query_str, params = qb.build_select()
                return (self.db.fetch_all(query_str, params) if hasattr(self.db, 'fetch_all') else []) or []
            else:
                # query may be criteria dict - try ActiveRecord-like read
                if hasattr(self.db, 'read'):
                    res = self.db.read(query)
                    return res.all() if hasattr(res, 'all') else res
                if hasattr(self.db, 'select'):
                    return self.db.select(self.table_name, where=query) or []
                qb = QueryBuilder(self.table_name).select().where(query)
                query_str, params = qb.build_select()
                return (self.db.fetch_all(query_str, params) if hasattr(self.db, 'fetch_all') else []) or []
        except Exception as e:
            print(f"DBDatasource.read error: {e}")
            return []
    
    def update(self, query: Dict[str, Any]) -> bool:
        """Update records using new unified format.
        
        Format: {"collection": {"col_name": match_value, "col_to_update": new_value}}
        """
        if self.read_only:
            raise Exception("Datasource is read-only.")
        
        if not query:
            return False
        
        try:
            # Extract specs from query
            specs = list(query.values())[0]
            
            # Separate WHERE conditions from UPDATE values
            where_conditions = {}
            update_values = {}
            
            if isinstance(specs, dict):
                for key, value in specs.items():
                    # Try to find if this key-value exists (is a WHERE condition)
                    existing = None
                    # Prefer ActiveRecord-style read
                    if hasattr(self.db, 'read'):
                        try:
                            res = self.db.read({key: value})
                            existing = res.all() if hasattr(res, 'all') else res
                        except Exception:
                            existing = None
                    elif hasattr(self.db, 'select'):
                        try:
                            existing = self.db.select(self.table_name, where={key: value})
                        except Exception:
                            existing = None
                    else:
                        # Fallback QueryBuilder check
                        try:
                            qb = QueryBuilder(self.table_name).select().where({key: value})
                            q, p = qb.build_select()
                            existing = self.db.fetch_all(q, p) if hasattr(self.db, 'fetch_all') else None
                        except Exception:
                            existing = None

                    if existing:
                        where_conditions[key] = value
                    else:
                        update_values[key] = value

            # Perform update using available API
            # Try ActiveRecord-like update(data, criteria)
            if hasattr(self.db, 'update') and callable(self.db.update):
                try:
                    # prefer ActiveRecord signature: update(data, criteria)
                    res = None
                    try:
                        res = self.db.update(update_values, where_conditions)
                    except TypeError:
                        # maybe signature update(table, data, where=...)
                        res = self.db.update(self.table_name, update_values, where=where_conditions)
                    return res is not None
                except Exception:
                    pass

            # Fallback to QueryBuilder + execute
            try:
                qb = QueryBuilder(self.table_name).where(where_conditions)
                query_str, params = qb.build_update(update_values)
                if hasattr(self.db, 'execute_query'):
                    self.db.execute_query(query_str, params)
                    return True
            except Exception:
                pass

            return False
        except Exception as e:
            print(f"DBDatasource.update error: {e}")
            return False
    
    def delete(self, query: Dict[str, Any], params: Optional[Dict[str, Any]] = None) -> bool:
        """Delete records using new unified format.
        
        Format: {"collection": {"col_name": match_value}}
        """
        if self.read_only:
            raise Exception("Datasource is read-only.")
        
        if not query:
            return False
        
        try:
            # Extract specs from query
            specs = list(query.values())[0]

            # Build WHERE conditions from specs
            where_conditions = {}
            if isinstance(specs, dict):
                where_conditions = specs

            # Try ActiveRecord-like delete(criteria)
            if hasattr(self.db, 'delete') and callable(self.db.delete):
                try:
                    # try delete(criteria)
                    try:
                        res = self.db.delete(where_conditions)
                        return res is not None
                    except TypeError:
                        # try delete(table, where=...)
                        res = self.db.delete(self.table_name, where=where_conditions)
                        return res is not None
                except Exception:
                    pass

            # Fallback to QueryBuilder + execute
            try:
                qb = QueryBuilder(self.table_name).where(where_conditions)
                query_str, params = qb.build_delete()
                if hasattr(self.db, 'execute_query'):
                    self.db.execute_query(query_str, params)
                    return True
            except Exception:
                pass

            return False
        except Exception as e:
            print(f"DBDatasource.delete error: {e}")
            return False
    
    def fetch(self, key: Optional[Union[str, int, List]]) -> List[Dict[str, Any]]:
        """
        Fetch data by key (legacy method from PHP).
        
        Args:
            key: Can be None (all), str/int (single), or list (multiple)
        
        Returns:
            List of records
        """
        if key is None:
            return self.read()
        elif isinstance(key, (str, int)):
            return self.read({self.primary_key: key})
        elif isinstance(key, list):
            # Fetch multiple IDs
            return self.read({f"{self.primary_key}_in": key})
        return []
    
    def push(self, attributes: Dict[str, Any]) -> None:
        """Save (insert/update) data to the database."""
        if self.read_only:
            raise Exception("Datasource is read-only.")
        
        if self.primary_key in attributes:
            # Update existing
            pk_val = attributes[self.primary_key]
            # prefer update by id
            try:
                if hasattr(self.db, 'update'):
                    try:
                        self.db.update(attributes, {self.primary_key: pk_val})
                        return
                    except TypeError:
                        self.db.update(self.table_name, attributes, where={self.primary_key: pk_val})
                        return
            except Exception:
                pass

            # Fallback
            self.update({self.primary_key: pk_val})
        else:
            # Create new
            self.create(attributes)
    
    def pull(self) -> Dict[str, Any]:
        """Load all data from the database."""
        result = self.read()
        return {self.table_name: result}
