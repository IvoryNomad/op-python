# op-python

[![PyPI - Version](https://img.shields.io/pypi/v/:op-python)](https://pypi.org/project/op-python/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![CI](https://github.com/IvoryNomad/op-python/workflows/CI/badge.svg)](https://github.com/IvoryNomad/op-python/actions)
[![codecov](https://codecov.io/gh/IvoryNomad/op-python/branch/master/graph/badge.svg)](https://codecov.io/gh/IvoryNomad/op-python)

A Python wrapper for the 1Password CLI (`op`) tool, providing a clean interface for managing secrets programmatically.

## Features

- **Token-based authentication** - Supports both Service Account tokens and 1Password Connect
- **Flexible .env support** - Optional dotenv loading with customizable paths and override behavior
- **Comprehensive API** - Get items, list vaults, manage secrets, and more
- **Type hints** - Full typing support for better IDE experience
- **Error handling** - Clear error messages and custom exceptions

## Installation

```bash
pip install op-python
```

## Quick Start

### Authentication

Choose one of the following authentication methods:

**Option 1: Service Account Token**
```bash
export OP_SERVICE_ACCOUNT_TOKEN="ops_your_service_account_token"
```

**Option 2: 1Password Connect**
```bash
export OP_CONNECT_HOST="https://your-connect-server.com"
export OP_CONNECT_TOKEN="your_connect_token"
```

### Basic Usage

```python
from op_python import OpClient, OnePasswordError

try:
    # Initialize client
    op = OpClient()
    
    # Get a secret
    password = op.get_secret("op://Personal/MyApp/password")
    
    # Get an item
    item = op.get_item("MyApp", vault="Personal")
    
    # List items in a vault
    items = op.list_items(vault="Personal")
    
    # List all vaults
    vaults = op.list_vaults()
    
except OnePasswordError as e:
    print(f"Error: {e}")
```

## Configuration Options

### Using .env Files

```python
# Enable .env loading (disabled by default)
op = OpClient(use_dotenv=True)

# Custom .env file path
op = OpClient(use_dotenv=True, dotenv_path="config/production.env")

# Let .env override environment variables
op = OpClient(use_dotenv=True, dotenv_override=True)
```

### .env File Format

Create a `.env` file in your project root:

```bash
# Service Account Authentication
OP_SERVICE_ACCOUNT_TOKEN=ops_your_service_account_token

# OR Connect Authentication
# OP_CONNECT_HOST=https://your-connect-server.com
# OP_CONNECT_TOKEN=your_connect_token
```

## API Reference

### OpClient

#### Constructor

```python
OpClient(
    op_path: str = "op",
    use_dotenv: bool = False,
    dotenv_path: Union[str, Path] = ".env",
    dotenv_override: bool = False
)
```

- `op_path`: Path to the `op` CLI executable
- `use_dotenv`: Enable loading environment variables from .env file
- `dotenv_path`: Path to .env file (only used if `use_dotenv=True`)
- `dotenv_override`: Whether .env values override existing environment variables

#### Methods

**`get_secret(secret_reference: str) -> str`**
Get a secret using 1Password's secret reference syntax.

```python
password = op.get_secret("op://vault/item/field")
```

**`get_item(item_identifier: str, vault: Optional[str] = None) -> Dict[str, Any]`**
Get a complete item with all its fields.

```python
item = op.get_item("MyApp", vault="Personal")
```

**`list_items(vault: Optional[str] = None, categories: Optional[List[str]] = None) -> List[Dict[str, Any]]`**
List items, optionally filtered by vault and categories.

```python
items = op.list_items(vault="Personal", categories=["Login", "Password"])
```

**`list_vaults() -> List[Dict[str, Any]]`**
List all available vaults.

```python
vaults = op.list_vaults()
```

**`create_item(title: str, category: str = "Login", vault: Optional[str] = None, **fields) -> Dict[str, Any]`**
Create a new item.

```python
item = op.create_item(
    title="New App",
    category="Login",
    vault="Personal",
    username="user@example.com",
    password="secret123"
)
```

**`delete_item(item_identifier: str, vault: Optional[str] = None) -> str`**
Delete an item.

```python
op.delete_item("MyApp", vault="Personal")
```

## Requirements

- Python 3.9+
- 1Password CLI (`op`) installed and accessible in PATH
- Valid 1Password authentication (Service Account token or Connect credentials)

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/op-python.git
cd op-python

# Install dependencies (including dev tools)
poetry install

# Run tests
poetry run pytest

# Format code
poetry run black .

# Type checking
poetry run mypy src/

# Build package
poetry build
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
