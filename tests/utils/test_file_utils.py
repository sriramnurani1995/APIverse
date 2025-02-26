import os
import pytest
import uuid
from unittest.mock import patch
from src.utils.file_utils import get_mime_type, save_file

### Test get_mime_type function ###
def test_get_mime_type_valid():
    """Test valid MIME type retrieval."""
    assert get_mime_type("html") == "text/html"
    assert get_mime_type("json") == "application/json"
    assert get_mime_type("png") == "image/png"

def test_get_mime_type_unknown():
    """Test unknown file extension falls back to 'application/octet-stream'."""
    assert get_mime_type("xyz") == "application/octet-stream"
    assert get_mime_type("") == "application/octet-stream"

### Test save_file function ###
@pytest.fixture
def temp_folder(tmpdir):
    """Fixture to provide a temporary folder for file saving tests."""
    return str(tmpdir)

def test_save_file_creates_file(temp_folder):
    """Test if save_file properly creates a file in the given folder."""
    content = "Hello, this is a test file."
    file_path = save_file(content, "txt", temp_folder)

    # Ensure the file exists
    assert os.path.exists(file_path)

    # Ensure the file contains the correct content
    with open(file_path, "r", encoding="utf-8") as f:
        assert f.read() == content

def test_save_file_returns_correct_path(temp_folder):
    """Test if save_file returns the correct path."""
    content = "Test content"
    file_path = save_file(content, "txt", temp_folder)

    # Ensure file path is inside the expected folder
    assert file_path.startswith(temp_folder)

    # Ensure file has correct extension
    assert file_path.endswith(".txt")

def test_save_file_unique_names(temp_folder):
    """Test if save_file generates unique file names."""
    content = "Sample content"
    file1 = save_file(content, "txt", temp_folder)
    file2 = save_file(content, "txt", temp_folder)

    # Ensure both file paths are different
    assert file1 != file2

# Run tests
if __name__ == "__main__":
    pytest.main()
