"""
1Password CLI wrapper for Python
"""

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class OnePasswordError(Exception):
    """Custom exception for 1Password CLI errors"""

    pass


class OpClient:
    """
    A Python wrapper for the 1Password CLI (op) tool.

    This class provides methods to interact with 1Password vaults,
    items, and secrets through the op CLI using token-based authentication.

    Requires either:
    - OP_SERVICE_ACCOUNT_TOKEN environment variable for service account auth, or
    - Both OP_CONNECT_HOST and OP_CONNECT_TOKEN for 1Password Connect
    """

    def __init__(
        self,
        op_path: str = "op",
        use_dotenv: bool = False,
        dotenv_path: Union[str, Path] = ".env",
        dotenv_override: bool = False,
    ):
        """
        Initialize the OpClient.

        Args:
            op_path: Path to the op CLI executable (default: "op")
            use_dotenv: Whether to load environment variables from .env file (default: False)
            dotenv_path: Path to .env file to load (default: ".env"). Only used if use_dotenv=True.
            dotenv_override: Values from .env file override existing environment variables. Only used if use_dotenv=True.

        Raises:
            OnePasswordError: If required authentication environment variables are not set
        """
        logger.debug(
            "op-python instantiating OpClient class instance, { 'op_path' : %s, 'use_dotenv': %s, 'dotenv_path': %s, 'dotenv_override': %s",
            op_path,
            use_dotenv,
            dotenv_path,
            dotenv_override,
        )
        self.op_path = op_path
        if use_dotenv:
            self._load_dotenv(dotenv_path, dotenv_override)
        self._check_op_available()
        self._check_authentication_config()

    def _load_dotenv(
        self, dotenv_path: Union[str, Path], dotenv_override: bool
    ) -> None:
        """
        Load environment variables from .env file if it exists.

        Args:
            dotenv_path: Path to .env file to load
        """
        dotenv_path = Path(dotenv_path)
        if str(dotenv_path).startswith("~"):
            dotenv_path = dotenv_path.expanduser()
        else:
            dotenv_path = dotenv_path.resolve()

        if dotenv_path.exists():
            logger.info("op-python loading dotenv_path  %s", dotenv_path)
            load_dotenv(dotenv_path, override=dotenv_override)
        else:
            logger.warning("op-python could not find dotenv_path %s", dotenv_path)

    def _check_op_available(self) -> None:
        """Check if the op CLI is available and accessible."""
        try:
            result = subprocess.run(
                [self.op_path, "--version"], capture_output=True, text=True, check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise OnePasswordError(
                f"1Password CLI not found or not accessible at '{self.op_path}'. "
                f"Please install the 1Password CLI and ensure it's in your PATH. "
                f"Error: {e}"
            )

    def _check_authentication_config(self) -> None:
        """
        Check that required authentication environment variables are set.

        Raises:
            OnePasswordError: If authentication is not properly configured
        """
        service_account_token = os.getenv("OP_SERVICE_ACCOUNT_TOKEN")
        connect_host = os.getenv("OP_CONNECT_HOST")
        connect_token = os.getenv("OP_CONNECT_TOKEN")

        # Check if service account token is set
        if service_account_token:
            return  # Service account auth is configured

        # Check if Connect auth is fully configured
        if connect_host and connect_token:
            return  # Connect auth is configured

        # Neither auth method is properly configured
        missing_vars = []
        if not service_account_token:
            missing_vars.append("OP_SERVICE_ACCOUNT_TOKEN")

        if not connect_host or not connect_token:
            if not connect_host:
                missing_vars.append("OP_CONNECT_HOST")
            if not connect_token:
                missing_vars.append("OP_CONNECT_TOKEN")

        raise OnePasswordError(
            "Authentication not configured. Please set either:\n"
            "1. OP_SERVICE_ACCOUNT_TOKEN for service account authentication, or\n"
            "2. Both OP_CONNECT_HOST and OP_CONNECT_TOKEN for 1Password Connect authentication.\n"
            f"Missing environment variables: {', '.join(missing_vars)}"
        )

    def _run_op_command(self, args: List[str]) -> str:
        """
        Run an op CLI command and return the output.

        Args:
            args: List of command arguments

        Returns:
            Command output as string

        Raises:
            OnePasswordError: If command fails
        """
        try:
            result = subprocess.run(
                [self.op_path] + args, capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise OnePasswordError(f"Command failed: {e.stderr.strip()}")

    def get_item(
        self, item_identifier: str, vault: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get an item from 1Password.

        Args:
            item_identifier: Item name, ID, or unique identifier
            vault: Vault name or ID (optional)

        Returns:
            Item data as dictionary
        """
        args = ["item", "get", item_identifier, "--format=json"]
        if vault:
            args.extend(["--vault", vault])

        output = self._run_op_command(args)
        return json.loads(output)

    def list_items(
        self, vault: Optional[str] = None, categories: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        List items in 1Password.

        Args:
            vault: Vault name or ID to search in (optional)
            categories: List of item categories to filter by (optional)

        Returns:
            List of items
        """
        args = ["item", "list", "--format=json"]
        if vault:
            args.extend(["--vault", vault])
        if categories:
            for category in categories:
                args.extend(["--categories", category])

        output = self._run_op_command(args)
        return json.loads(output)

    def get_secret(self, secret_reference: str) -> str:
        """
        Get a secret value using secret reference syntax.

        Args:
            secret_reference: Secret reference (e.g., "op://vault/item/field")

        Returns:
            Secret value as string
        """
        args = ["read", secret_reference]
        return self._run_op_command(args)

    def list_vaults(self) -> List[Dict[str, Any]]:
        """
        List all available vaults.

        Returns:
            List of vaults
        """
        args = ["vault", "list", "--format=json"]
        output = self._run_op_command(args)
        return json.loads(output)

    def create_item(
        self, title: str, category: str = "Login", vault: Optional[str] = None, **fields
    ) -> Dict[str, Any]:
        """
        Create a new item in 1Password.

        Args:
            title: Item title
            category: Item category (default: "Login")
            vault: Vault to create item in (optional)
            **fields: Additional fields to set

        Returns:
            Created item data
        """
        args = [
            "item",
            "create",
            "--category",
            category,
            "--title",
            title,
            "--format=json",
        ]
        if vault:
            args.extend(["--vault", vault])

        # Add custom fields
        for field_name, field_value in fields.items():
            args.extend([f"--{field_name}", str(field_value)])

        output = self._run_op_command(args)
        return json.loads(output)

    def delete_item(self, item_identifier: str, vault: Optional[str] = None) -> str:
        """
        Delete an item from 1Password.

        Args:
            item_identifier: Item name, ID, or unique identifier
            vault: Vault name or ID (optional)

        Returns:
            Success message
        """
        args = ["item", "delete", item_identifier]
        if vault:
            args.extend(["--vault", vault])

        return self._run_op_command(args)
