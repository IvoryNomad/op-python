"""
Tests for OpClient
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from op_python import OnePasswordError, OpClient


class TestOpClient:
    @patch.dict(os.environ, {"OP_SERVICE_ACCOUNT_TOKEN": "test_token"})
    def test_init_success_with_service_account(self):
        """Test successful initialization with service account token."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="2.0.0")
            _ = OpClient()  # Default: no dotenv loading
            mock_run.assert_called_once()

    @patch.dict(
        os.environ,
        {
            "OP_CONNECT_HOST": "https://connect.example.com",
            "OP_CONNECT_TOKEN": "test_token",
        },
    )
    def test_init_success_with_connect(self):
        """Test successful initialization with Connect credentials."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="2.0.0")
            _ = OpClient()  # Default: no dotenv loading
            mock_run.assert_called_once()

    def test_init_with_dotenv_enabled(self):
        """Test initialization with .env file loading enabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a .env file in temp directory
            env_file = Path(temp_dir) / ".env"
            env_file.write_text("OP_SERVICE_ACCOUNT_TOKEN=dotenv_token\n")

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(stdout="2.0.0")

                # Change to temp directory and test dotenv loading
                original_cwd = Path.cwd()
                try:
                    os.chdir(temp_dir)
                    with patch.dict(os.environ, {}, clear=True):
                        _ = OpClient(use_dotenv=True)
                        # Should succeed because dotenv loaded the token
                        assert os.getenv("OP_SERVICE_ACCOUNT_TOKEN") == "dotenv_token"
                finally:
                    os.chdir(original_cwd)

    def test_init_with_custom_dotenv_path(self):
        """Test initialization with custom .env file path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a custom .env file
            custom_env = Path(temp_dir) / "production.env"
            custom_env.write_text("OP_SERVICE_ACCOUNT_TOKEN=custom_token\n")

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(stdout="2.0.0")

                with patch.dict(os.environ, {}, clear=True):
                    _ = OpClient(use_dotenv=True, dotenv_path=custom_env)
                    # Should succeed because custom dotenv loaded the token
                    assert os.getenv("OP_SERVICE_ACCOUNT_TOKEN") == "custom_token"

    def test_init_dotenv_disabled_by_default(self):
        """Test that dotenv loading is disabled by default."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a .env file that would provide auth
            env_file = Path(temp_dir) / ".env"
            env_file.write_text("OP_SERVICE_ACCOUNT_TOKEN=dotenv_token\n")

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(stdout="2.0.0")

                original_cwd = Path.cwd()
                try:
                    os.chdir(temp_dir)
                    with patch.dict(os.environ, {}, clear=True):
                        # Should fail because dotenv is not loaded by default
                        with pytest.raises(
                            OnePasswordError, match="Authentication not configured"
                        ):
                            OpClient()  # use_dotenv=False by default
                finally:
                    os.chdir(original_cwd)

    def test_init_dotenv_file_not_exists(self):
        """Test initialization when .env file doesn't exist but use_dotenv=True."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="2.0.0")

            with patch.dict(os.environ, {"OP_SERVICE_ACCOUNT_TOKEN": "env_token"}):
                # Should work fine when .env doesn't exist but env vars are set
                _ = OpClient(use_dotenv=True)

    def test_env_vars_override_dotenv(self):
        """Test that existing environment variables are not overridden by .env file by default."""
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            env_file.write_text("OP_SERVICE_ACCOUNT_TOKEN=dotenv_token\n")

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(stdout="2.0.0")

                original_cwd = Path.cwd()
                try:
                    os.chdir(temp_dir)
                    # Set environment variable that should take precedence
                    with patch.dict(
                        os.environ, {"OP_SERVICE_ACCOUNT_TOKEN": "env_token"}
                    ):
                        _ = OpClient(
                            use_dotenv=True
                        )  # dotenv_override=False by default
                        # Environment variable should take precedence over .env
                        assert os.getenv("OP_SERVICE_ACCOUNT_TOKEN") == "env_token"
                finally:
                    os.chdir(original_cwd)

    def test_dotenv_override_env_vars(self):
        """Test that .env file can override environment variables when dotenv_override=True."""
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            env_file.write_text("OP_SERVICE_ACCOUNT_TOKEN=dotenv_token\n")

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(stdout="2.0.0")

                original_cwd = Path.cwd()
                try:
                    os.chdir(temp_dir)
                    # Set environment variable that will be overridden
                    with patch.dict(
                        os.environ, {"OP_SERVICE_ACCOUNT_TOKEN": "env_token"}
                    ):
                        _ = OpClient(use_dotenv=True, dotenv_override=True)
                        # .env value should override environment variable
                        assert os.getenv("OP_SERVICE_ACCOUNT_TOKEN") == "dotenv_token"
                finally:
                    os.chdir(original_cwd)

    @patch.dict(os.environ, {}, clear=True)
    def test_init_no_auth_configured(self):
        """Test initialization failure when no auth is configured."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="2.0.0")
            with pytest.raises(OnePasswordError, match="Authentication not configured"):
                OpClient()

    @patch.dict(os.environ, {"OP_CONNECT_HOST": "https://connect.example.com"})
    def test_init_incomplete_connect_auth(self):
        """Test initialization failure with incomplete Connect auth."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="2.0.0")
            with pytest.raises(OnePasswordError, match="OP_CONNECT_TOKEN"):
                OpClient()

    def test_init_op_not_found(self):
        """Test initialization failure when op CLI is not found."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()
            with pytest.raises(OnePasswordError, match="1Password CLI not found"):
                OpClient()

    @patch.dict(os.environ, {"OP_SERVICE_ACCOUNT_TOKEN": "test_token"})
    @patch("subprocess.run")
    def test_get_secret(self, mock_run):
        """Test getting a secret value."""
        # Mock the version check
        mock_run.return_value = MagicMock(stdout="2.0.0")
        client = OpClient()

        # Mock the actual secret retrieval
        mock_run.return_value = MagicMock(stdout="secret_value")
        result = client.get_secret("op://vault/item/field")

        assert result == "secret_value"

    @patch.dict(os.environ, {"OP_SERVICE_ACCOUNT_TOKEN": "test_token"})
    @patch("subprocess.run")
    def test_list_vaults(self, mock_run):
        """Test listing vaults."""
        # Mock version check
        mock_run.return_value = MagicMock(stdout="2.0.0")
        client = OpClient()

        # Mock vault listing
        mock_vault_data = '[{"id": "vault1", "name": "Personal"}]'
        mock_run.return_value = MagicMock(stdout=mock_vault_data)

        result = client.list_vaults()
        assert len(result) == 1
        assert result[0]["name"] == "Personal"
