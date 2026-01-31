"""app.datasources.file_datasource - File-Based Datasource

Persists data to files (directory or single-file modes) using FileSystem for I/O.

Origin:
    Converted from PHP HTTPStack v2 App/Datasources FileDatasource.
    
Changelog:
    - 2026-01-30: Converted from PHP. FileDatasource for file-based persistence.
    - 2026-01-30: Updated update() and delete() to use unified query format.
        * Works in both directory and single-file modes.
        * Format: {"collection": ["id": match_value, "field": new_value]}
    - 2026-01-30: Integrated FileSystem class for file I/O operations.

Usage:
    from app.datasources.file_datasource import FileDatasource
    from lib.fs.files import FileSystem
    
    fs = FileSystem()
    # Directory mode: /tmp/users/ contains user_1.json, user_2.json, etc.
    ds = FileDatasource('/tmp/users', read_only=False, filesystem=fs)
    ds.create({'id': 1, 'name': 'Alice'})
    # Creates: /tmp/users/1.json
    
    # Single-file mode: /tmp/users.json contains all records
    ds = FileDatasource('/tmp/users.json', read_only=False, filesystem=fs)
    ds.create({'id': 1, 'name': 'Alice'})
    # Adds to: /tmp/users.json {"1": {"id": 1, ...}}

Directory Mode:
    Perfect for:
        - One record per file
        - Larger datasets
        - Easy file-by-file viewing
    Structure:
        /tmp/users/
            1.json
            2.json
            3.json

Single-File Mode:
    Perfect for:
        - Small datasets
        - Configuration
        - Atomic saves
    Structure:
        /tmp/users.json
            {"1": {...}, "2": {...}, "3": {...}}

Best For:
    - Moderate datasets (up to 100MB)
    - File-based configuration
    - Development/testing
    - Systems with periodic backups
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from app.datasources.abstract import AbstractDatasource
from lib.fs.files import FileSystem


class FileDatasource(AbstractDatasource):
    """
    Datasource backed by files (JSON or otherwise).
    Uses FileSystem class for file I/O operations.
    
    Supports two modes:
    - Directory mode: each JSON file represents a record
    - Single file mode: one JSON file with multiple records
    
    Automatically detects mode based on path type (directory vs file).
    """
    
    def __init__(self, data_path: str, read_only: bool = True, filesystem: Optional[FileSystem] = None):
        """
        Initialize with a file or directory path.
        
        Args:
            data_path: Path to a directory or file
            read_only: If True, prevents write operations
            filesystem: FileSystem instance (creates default if not provided)
        """
        super().__init__(read_only)
        self.path = Path(data_path)
        self.filesystem = filesystem or FileSystem()
        self.is_dir = self.path.is_dir() if self.path.exists() else False
    
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
            
            if self.is_dir:
                # Directory mode: save as file using FileSystem
                file_name = record_data.get('id', 'record')
                file_path = self.path / f"{file_name}.json"
                content = json.dumps(record_data, indent=2)
                self.filesystem.write_file(str(file_path), content)
            else:
                # Single file mode: add to file using FileSystem
                data = {}
                if self.path.exists():
                    try:
                        content = self.filesystem.load_file(str(self.path))
                        data = json.loads(content) or {}
                    except:
                        data = {}
                
                record_id = record_data.get('id', len(data) + 1)
                data[str(record_id)] = record_data
                
                file_content = json.dumps(data, indent=2)
                self.filesystem.write_file(str(self.path), file_content)
            
            return True
        except Exception as e:
            print(f"FileDatasource.create error: {e}")
            return False
    
    def read(self, query: Optional[Dict[str, Any]] = None, filter_: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
                
                if self.is_dir:
                    # Directory mode
                    if isinstance(specs, list) and len(specs) == 0:
                        # Return all files
                        result = {}
                        for json_file in self.path.glob("*.json"):
                            try:
                                content = self.filesystem.load_file(str(json_file))
                                result[json_file.stem] = json.loads(content) or {}
                            except:
                                pass
                        return result
                    elif isinstance(specs, dict):
                        # Filter by WHERE conditions
                        result = {}
                        for json_file in self.path.glob("*.json"):
                            try:
                                content = self.filesystem.load_file(str(json_file))
                                file_data = json.loads(content) or {}
                            except:
                                continue
                            if self._matches_item(file_data, specs):
                                        result[json_file.stem] = file_data
                        return result
                else:
                    # Single file mode
                    if not self.path.exists():
                        return {}
                    
                    try:
                        content = self.filesystem.load_file(str(self.path))
                        data = json.loads(content) or {}
                    except:
                        return {}
                    
                    if isinstance(specs, list) and len(specs) == 0:
                        # Return all
                        return data
                    elif isinstance(specs, list) and all(isinstance(s, str) for s in specs):
                        # Return only specified columns
                        result = {}
                        for k, v in data.items():
                            if isinstance(v, dict):
                                filtered_item = {col: v.get(col) for col in specs if col in v}
                                result[k] = filtered_item
                        return result
                    elif isinstance(specs, dict):
                        # Filter by WHERE conditions
                        result = {}
                        for k, v in data.items():
                            if isinstance(v, dict) and self._matches_item(v, specs):
                                result[k] = v
                        return result
            
            # Fallback for old format
            if query is None:
                if self.is_dir:
                    result = {}
                    for json_file in self.path.glob("*.json"):
                        try:
                            content = self.filesystem.load_file(str(json_file))
                            result[json_file.stem] = json.loads(content) or {}
                        except:
                            pass
                    return result
                else:
                    if not self.path.exists():
                        return {}
                    try:
                        content = self.filesystem.load_file(str(self.path))
                        return json.loads(content) or {}
                    except:
                        return {}
            
            return {}
        except Exception as e:
            print(f"FileDatasource.read error: {e}")
            return {}
    
    def update(self, query: Dict[str, Any]) -> bool:
        """Update records using new unified format.
        
        Format: {"collection": {"col_name": match_value, "col_to_update": new_value}}
        """
        if self.read_only:
            raise Exception("Datasource is read-only.")
        
        if not query:
            return False
        
        try:
            # Extract collection name and specs
            collection_name = list(query.keys())[0]
            specs = query[collection_name]
            
            # Separate WHERE conditions from UPDATE values
            where_conditions = {}
            update_values = {}
            
            if isinstance(specs, dict):
                for key, value in specs.items():
                    # Check if this key-value exists in any record (WHERE condition)
                    found_match = False
                    if self.is_dir:
                        for json_file in self.path.glob("*.json"):
                            try:
                                content = self.filesystem.load_file(str(json_file))
                                file_data = json.loads(content) or {}
                            except:
                                continue
                            if self._matches_item(file_data, {key: value}):
                                found_match = True
                                break
                    else:
                        if self.path.exists():
                            try:
                                content = self.filesystem.load_file(str(self.path))
                                data = json.loads(content) or {}
                            except:
                                data = {}
                            found_match = any(
                                isinstance(item, dict) and self._matches_item(item, {key: value})
                                for item in data.values()
                            )

                    if found_match:
                        where_conditions[key] = value
                    else:
                        update_values[key] = value
            
            if self.is_dir:
                # Directory mode: update specific files using FileSystem
                for json_file in self.path.glob("*.json"):
                    try:
                        content = self.filesystem.load_file(str(json_file))
                        file_data = json.loads(content) or {}
                    except:
                        continue
                    
                    if self._matches_item(file_data, where_conditions):
                        file_data.update(update_values)
                        file_content = json.dumps(file_data, indent=2)
                        self.filesystem.write_file(str(json_file), file_content)
            else:
                # Single file mode: update entries using FileSystem
                data = {}
                if self.path.exists():
                    try:
                        content = self.filesystem.load_file(str(self.path))
                        data = json.loads(content) or {}
                    except:
                        data = {}
                
                for k, v in data.items():
                    if isinstance(v, dict) and self._matches_item(v, where_conditions):
                        data[k].update(update_values)
                
                file_content = json.dumps(data, indent=2)
                self.filesystem.write_file(str(self.path), file_content)
            
            return True
        except Exception as e:
            print(f"FileDatasource.update error: {e}")
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
            # Extract collection name and specs
            collection_name = list(query.keys())[0]
            specs = query[collection_name]
            
            # Build WHERE conditions from specs
            where_conditions = {}
            if isinstance(specs, dict):
                where_conditions = specs
            
            if self.is_dir:
                # Directory mode: delete files using FileSystem
                for json_file in self.path.glob("*.json"):
                    try:
                        content = self.filesystem.load_file(str(json_file))
                        file_data = json.loads(content) or {}
                    except:
                        continue
                    
                    if self._matches_item(file_data, where_conditions):
                        json_file.unlink()
            else:
                # Single file mode: delete entries using FileSystem
                if not self.path.exists():
                    return True
                
                try:
                    content = self.filesystem.load_file(str(self.path))
                    data = json.loads(content) or {}
                except:
                    return True
                
                keys_to_delete = [k for k, v in data.items()
                                 if isinstance(v, dict) and self._matches_item(v, where_conditions)]
                
                for k in keys_to_delete:
                    del data[k]
                
                file_content = json.dumps(data, indent=2)
                self.filesystem.write_file(str(self.path), file_content)
            
            return True
        except Exception as e:
            print(f"FileDatasource.delete error: {e}")
            return False
    
    def push(self, attributes: Dict[str, Any]) -> None:
        """Save all attributes to file(s) using FileSystem."""
        if self.read_only:
            raise Exception("Datasource is read-only.")
        
        if self.is_dir:
            for filename, content in attributes.items():
                file_path = self.path / f"{filename}.json"
                file_content = json.dumps(content, indent=2)
                self.filesystem.write_file(str(file_path), file_content)
        else:
            file_content = json.dumps(attributes, indent=2)
            self.filesystem.write_file(str(self.path), file_content)
    
    def pull(self) -> Dict[str, Any]:
        """Load all data from file(s)."""
        return self.read()
