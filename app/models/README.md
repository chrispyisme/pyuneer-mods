"""Model and Datasource Architecture - Comprehensive Guide

## Overview

This is a port of the PHP HTTPStack v2 Model and Datasource architecture to Python.
It provides a flexible, extensible system for managing data models with multiple persistence backends.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
│                   (Your Controllers)                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   AbstractModel                             │
│  - State Management (push/pop states)                       │
│  - Attribute Management (get/set/has/remove)               │
│  - Datasource Integration (pull/push)                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
   ┌───────▼────────┐ ┌───▼──────┐ ┌────▼──────────┐
   │ JsonDatasource │ │ FileDatasource │ │ DBDatasource  │
   └────────────────┘ └──────────┘ └───────────────┘
           │               │               │
   ┌───────▼────────┐ ┌───▼──────┐ ┌────▼──────────┐
   │  JSON File     │ │   Files  │ │  Database    │
   └────────────────┘ └──────────┘ └───────────────┘
```

## Key Concepts

### 1. Contracts (Interfaces)

#### CrudInterface
- `create(payload, params)` - Create a record
- `read(query, filter)` - Read records
- `update(where, payload)` - Update records
- `delete(where, params)` - Delete records

#### DatasourceInterface
- `push(attributes)` - Save data to storage
- `pull()` - Load data from storage
- `set_read_only(bool)` - Set read-only mode
- `is_read_only()` - Check read-only status

### 2. AbstractModel

Implements both Attributes and AttributeState contracts:

**Attributes:**
- `get(key)` - Get attribute
- `set(key, value)` - Set attribute
- `has(key)` - Check existence
- `get_all()` - Get all attributes
- `set_all(data)` - Set multiple
- `remove(key)` - Remove attribute
- `clear()` - Clear all
- `count()` - Count attributes

**AttributeState:**
- `push_state(restore_point)` - Save current state
- `pop_state()` - Restore previous state
- `get_state(restore_point)` - Get named state

**Datasource Integration:**
- `pull()` - Load from datasource
- `push()` - Save to datasource

### 3. Datasource Implementations

#### JsonDatasource
Backs data with a single JSON file.

```python
from app.datasources.json_datasource import JsonDatasource

# Read-only mode
ds = JsonDatasource('/path/to/data.json', read_only=True)

# Writable mode
ds = JsonDatasource('/path/to/data.json', read_only=False)
ds.create({'id': 1, 'name': 'Alice'})
ds.update({'id': 1}, {'name': 'Alice Updated'})
ds.delete({'id': 1})
```

#### FileDatasource
Backs data with a directory of JSON files or a single JSON file.

```python
from app.datasources.file_datasource import FileDatasource

# Directory mode (each file = a record)
ds = FileDatasource('/path/to/data_dir', read_only=False)

# Single file mode
ds = FileDatasource('/path/to/data.json', read_only=False)
```

#### DBDatasource
Backs data with a relational database.

```python
from app.datasources.db_datasource import DBDatasource

ds = DBDatasource(db_connection, table_name='users', read_only=False)
```

### 4. Creating a Model

```python
from app.models.model import AbstractModel
from app.datasources.json_datasource import JsonDatasource

class UserModel(AbstractModel):
    def get_name(self):
        return self.get('name')
    
    def set_name(self, name):
        self.set('name', name)

# Create datasource
ds = JsonDatasource('/tmp/users.json', read_only=False)

# Create model
user = UserModel(ds, {'id': 1, 'name': 'Alice'})

# Use model
print(user.get_name())
user.set_name('Alice Updated')
user.push()  # Save to datasource
```

## Usage Examples

### Example 1: Basic CRUD

```python
user = UserModel(datasource)

# Create
user.set('username', 'john')
user.set('email', 'john@example.com')
user.push()

# Read
user.pull()

# Update
user.set('email', 'newemail@example.com')
user.push()

# Delete (via datasource)
datasource.delete({'id': user.get('id')})
```

### Example 2: State Management

```python
model = UserModel(datasource)
model.set('status', 'active')  # Auto-saves state as "before_set_status"

model.set('status', 'inactive')  # Auto-saves state as "before_set_status"

# Restore previous state
model.pop_state()
print(model.get('status'))  # "active"

# Get specific state
state = model.get_state('before_set_status')
```

### Example 3: Query & Filter

```python
# Read with query
results = datasource.read({'status': 'active'})

# Update with where clause
datasource.update({'user_id': 5}, {'last_login': '2024-01-30'})

# Delete with where clause
datasource.delete({'status': 'inactive'})
```

### Example 4: Multiple Datasources

```python
# Switch datasources
model = UserModel(json_ds)
model.pull()  # Load from JSON

# Later, use a different datasource
model.datasource = db_ds
model.push()  # Save to database

# Or load from database
model.pull()
```

## Best Practices

1. **Use type hints in models:**
   ```python
   class UserModel(AbstractModel):
       def get_email(self) -> str:
           return self.get('email') or ''
   ```

2. **Handle read-only mode:**
   ```python
   if not datasource.is_read_only():
       datasource.create({'id': 1, 'name': 'New Record'})
   ```

3. **Leverage state management:**
   ```python
   model.push_state('before_major_change')
   # Make changes...
   if error:
       model.pop_state()  # Rollback
   ```

4. **Use pull/push for sync:**
   ```python
   model.pull()  # Refresh from source
   # Modify...
   model.push()  # Save back
   ```

5. **Combine queries efficiently:**
   ```python
   results = datasource.read({'status': 'active'})
   for record in results.values():
       # Process
   ```

## File Structure

```
app/
├── models/
│   ├── __init__.py
│   ├── contracts.py         # Attributes, AttributeState interfaces
│   ├── base.py              # BaseModel (attribute storage)
│   └── model.py             # AbstractModel (with state + datasource)
├── datasources/
│   ├── __init__.py
│   ├── contracts.py         # CrudInterface, DatasourceInterface
│   ├── abstract.py          # AbstractDatasource
│   ├── json_datasource.py   # JSON file backend
│   ├── file_datasource.py   # File directory backend
│   └── db_datasource.py     # Database backend
└── examples/
    └── model_datasource_example.py
```

## Running Examples

```bash
python app/examples/model_datasource_example.py
```

## Extending

Create custom models:
```python
class ProductModel(AbstractModel):
    def get_price(self):
        return self.get('price', 0)
    
    def apply_discount(self, percent):
        price = self.get_price()
        new_price = price * (1 - percent / 100)
        self.set('price', new_price)

# Use
product = ProductModel(datasource)
product.pull()
product.apply_discount(10)
product.push()
```

Create custom datasources:
```python
from app.datasources.abstract import AbstractDatasource

class CustomDatasource(AbstractDatasource):
    def create(self, payload, params=None):
        # Custom implementation
        pass
    
    def read(self, query=None, filter_=None):
        # Custom implementation
        pass
    
    # ... implement other CRUD methods
```

## Notes

- Models automatically push state when mutated (via `set`, `remove`, `set_all`, `clear`)
- Datasources can be switched at runtime
- Read-only mode prevents writes across all CRUD operations
- JSON datasource is ideal for config/small data; use DBDatasource for large datasets
"""
