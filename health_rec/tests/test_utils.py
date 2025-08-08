"""Test utilities and helper functions."""

import json
import tempfile
from contextlib import suppress
from pathlib import Path
from typing import Any, Dict, List

import chromadb


def create_test_json_file(services: List[Dict[str, Any]]) -> str:
    """Create a temporary JSON file with test services data.

    Parameters
    ----------
    services : List[Dict[str, Any]]
        List of service dictionaries to write to JSON file

    Returns
    -------
    str
        Path to the temporary JSON file

    Note
    ----
    Remember to clean up the file after use with Path(file_path).unlink()
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(services, f, indent=2)
        return f.name


def create_ephemeral_collection(collection_name: str) -> chromadb.Collection:
    """Create an ephemeral ChromaDB collection for testing.

    Parameters
    ----------
    collection_name : str
        Name of the collection to create

    Returns
    -------
    chromadb.Collection
        An ephemeral ChromaDB collection
    """
    client = chromadb.EphemeralClient()
    return client.create_collection(name=collection_name)


def cleanup_test_file(file_path: str) -> None:
    """Clean up a temporary test file.

    Parameters
    ----------
    file_path : str
        Path to the file to delete
    """
    with suppress(FileNotFoundError):
        Path(file_path).unlink()


def assert_valid_service_document(
    document: str, metadata: Dict[str, Any], service_id: str
):
    """Assert that a service document and metadata are valid.

    Parameters
    ----------
    document : str
        The document string to validate
    metadata : Dict[str, Any]
        The metadata dictionary to validate
    service_id : str
        Expected service ID
    """
    # Check document format
    assert isinstance(document, str)
    assert len(document) > 0

    # Check metadata structure
    assert isinstance(metadata, dict)
    assert "resource" in metadata

    # Check service ID is provided
    assert service_id

    # Check that key fields appear in document
    if "name" in metadata and metadata["name"]:
        assert f"name: {metadata['name']}" in document
    if "description" in metadata and metadata["description"]:
        assert f"description: {metadata['description']}" in document
