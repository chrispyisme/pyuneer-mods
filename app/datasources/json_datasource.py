"""app.datasources.json_datasource - JSON File Datasource

Persists data to a single JSON file using FileSystem for I/O.

Origin:
    Converted from PHP HTTPStack v2 App/Datasources JsonDatasource.
    
Changelog:
    - 2026-01-30: Converted from PHP. JsonDatasource for JSON file persistence.
    - 2026-01-30: Updated update() and delete() to use unified query format.
        * Separates WHERE conditions from update values automatically.
        * Format: {"collection": ["id": 1, "name": "newname"]}
    - 2026-01-30: Integrated FileSystem class for file I/O operations.

Usage:
    from app.datasources.json_datasource import JsonDatasource
    from lib.fs.files import FileSystem
    
    fs = FileSystem()
    # Read-only (for loading config/data)
    ds = JsonDatasource('/tmp/users.json', read_only=True, filesystem=fs)
    data = ds.pull()
    
    # Writable (for persistence)
    ds = JsonDatasource('/tmp/users.json', read_only=False, filesystem=fs)
    ds.create({'id': 1, 'name': 'Alice'})
    ds.update({'id': 1}, {'name': 'Alice Smith'})
    ds.delete({'id': 1})

File Format:
    {
        "1": {"id": 1, "name": "Alice"},
        "2": {"id": 2, "name": "Bob"}
    }

Best For:
    - Small datasets (< 10MB)
    - Configuration files
    - Development/testing
    - Single-user access

NOT Recommended For:
    - Large datasets
    - High-concurrency scenarios
    - Production transactional systems
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.datasources.abstract import AbstractDatasource
from lib.fs.files import FileSystem


class JsonDatasource(AbstractDatasource):
    """Datasource backed by a single JSON file.
    
    Stores records as a dict with string keys, serialized to JSON.
    Uses FileSystem class for file I/O.
    Thread-safe for reads; not safe for concurrent writes.
    
    Raises Exception on write attempts if read_only=True.
    """
    
    def __init__(self, file_path: str, read_only: bool = True, filesystem: Optional[FileSystem] = None):
        """Initialize with a JSON file path.
        
        Args:
            file_path: Path to JSON file
            read_only: If True, prevents write operations
            filesystem: FileSystem instance (creates default if not provided)
        """
        super().__init__(read_only)
        self.file_path = Path(file_path)
        self.filesystem = filesystem or FileSystem()
        self._data: Dict[str, Any] = {}
        self._load_data()
    
    def _load_data(self) -> None:
        """Load data from JSON file using FileSystem."""
        if self.file_path.exists():
            try:
                content = self.filesystem.load_file(str(self.file_path))
                self._data = json.loads(content) or {}
            except (json.JSONDecodeError, IOError):
                self._data = {}
    
    def _save_data(self) -> None:
        """Save data to JSON file using FileSystem."""
        if self.read_only:
            raise Exception("Datasource is read-only.")
        
        content = json.dumps(self._data, indent=2)
        self.filesystem.write_file(str(self.file_path), content)
    
    def create(self, payload: Dict[str, Any], params: Optional[Dict[str, Any]] = None) -> bool:
        """Create a new record using new unified format.
        
        Format: {"collection": [{"id": 1, "name": "Alice"}]}
        """
        if self.read_only:
            raise Exception("Datasource is read-only.")
        
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
        
        # Store with ID as key
        record_id = record_data.get('id', len(self._data) + 1)
        self._data[str(record_id)] = record_data
        self._save_data()
        return True
    
    def read(self, query: Optional[Dict[str, Any]] = None, filter_: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Read records using new unified format.
        
        Format:
        - Read all: {"collection": []}
        - Read with WHERE: {"collection": ["col": value]}
        - Read with columns: {"collection": ["col1", "col2"]}
        """
        if query is None:
            # Return all data
            return self._data.copy()
        
        # Check if query follows new format {"collection": specs}
        if isinstance(query, dict) and len(query) == 1:
            collection_name = list(query.keys())[0]
            specs = query[collection_name]
            
            # Empty list = return all
            if isinstance(specs, list) and len(specs) == 0:
                return self._data.copy()
            
            # List of column names = filter to those columns
            if isinstance(specs, list) and all(isinstance(s, str) for s in specs):
                result = {}
                for key, item in self._data.items():
                    if isinstance(item, dict):
                        filtered_item = {col: item.get(col) for col in specs if col in item}
                        result[key] = filtered_item
                return result
            
            # Dict = WHERE conditions
            if isinstance(specs, dict):
                result = {}
                for key, item in self._data.items():
                    if isinstance(item, dict):
                        if self._matches_item(item, specs):
                            result[key] = item
                return result
        
        # Fallback for old format
        result = {}
        for key, item in self._data.items():
            if isinstance(item, dict):
                if self._matches_item(item, query):
                    result[key] = item
        
        return result
    
    def update(self, query: Dict[str, Any]) -> bool:
        """Update records using new unified format.
        
        Format: {"collection": {"col_name": match_value, "col_to_update": new_value}}
        """
        if self.read_only:
            raise Exception("Datasource is read-only.")
        
        if not query:
            return False
        
        # Extract collection name and specs
        collection_name = list(query.keys())[0]
        specs = query[collection_name]
        
        # Separate WHERE conditions from UPDATE values
        # Assume first item(s) with matching values in existing records are WHERE
        where_conditions = {}
        update_values = {}
        
        if isinstance(specs, dict):
            for key, value in specs.items():
                # Check if this key-value exists in any record (WHERE condition)
                found_match = any(
                    isinstance(item, dict) and self._matches_item(item, {key: value})
                    for item in self._data.values()
                )
                if found_match:
                    where_conditions[key] = value
                else:
                    update_values[key] = value
        
        # Apply updates
        updated = False
        for key, item in self._data.items():
            if isinstance(item, dict):
                if self._matches_item(item, where_conditions):
                    self._data[key].update(update_values)
                    updated = True
        
        if updated:
            self._save_data()
        
        return updated
    
    def delete(self, query: Dict[str, Any], params: Optional[Dict[str, Any]] = None) -> bool:
        """Delete records using new unified format.
        
        Format: {"collection": ["col_name": match_value]}
        """
        if self.read_only:
            raise Exception("Datasource is read-only.")
        
        if not query:
            return False
        
        # Extract collection name and specs
        collection_name = list(query.keys())[0]
        specs = query[collection_name]
        
        # Build WHERE conditions from specs
        where_conditions = {}
        if isinstance(specs, dict):
            where_conditions = specs
        
        keys_to_delete = []
        for key, item in self._data.items():
            if isinstance(item, dict):
                if self._matches_item(item, where_conditions):
                    keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del self._data[key]
        
        if keys_to_delete:
            self._save_data()
        
        return len(keys_to_delete) > 0
    
    def push(self, attributes: Dict[str, Any]) -> None:
        """Save all attributes to file."""
        if self.read_only:
            raise Exception("Datasource is read-only.")
        self._data = attributes
        self._save_data()
    
    def pull(self) -> Dict[str, Any]:
        """Load all data from file."""
        self._load_data()
        return self._data.copy()
