"""Unit tests for load_data.py module."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import chromadb
import pytest

from load_data import (
    OpenAIEmbedding,
    get_or_create_collection,
    load_json_data,
    prepare_documents,
)


@pytest.mark.unit
class TestLoadData:

    def test_load_json_data_success(self, temp_json_file):
        """Test successful JSON data loading."""
        loaded_data = load_json_data(temp_json_file)
        assert len(loaded_data) == 3
        assert loaded_data[0]["id"] == "test_service_1"
        assert loaded_data[1]["id"] == "test_service_2"

    def test_load_json_data_file_not_found(self):
        """Test JSON loading with non-existent file."""
        with pytest.raises(FileNotFoundError):
            load_json_data("non_existent_file.json")

    def test_load_json_data_invalid_json(self):
        """Test JSON loading with invalid JSON."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            temp_path = f.name

        try:
            with pytest.raises(json.JSONDecodeError):
                load_json_data(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_load_json_data_not_list(self):
        """Test JSON loading when data is not a list."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"not": "a list"}, f)
            temp_path = f.name

        try:
            with pytest.raises(ValueError):
                load_json_data(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_prepare_documents(self, test_services):
        """Test document preparation."""
        resource_name = "test_resource"
        documents, metadatas, ids = prepare_documents(test_services, resource_name)

        assert len(documents) == 3
        assert len(metadatas) == 3
        assert len(ids) == 3

        # Check resource name is added to metadata
        assert metadatas[0]["resource"] == resource_name
        assert metadatas[1]["resource"] == resource_name

        # Check IDs are extracted correctly
        assert ids[0] == "test_service_1"
        assert ids[1] == "test_service_2"

        # Check document format
        assert "name: Community Health Center" in documents[0]
        assert "description: Provides primary healthcare services" in documents[0]

    def test_get_or_create_collection_ephemeral(self):
        """Test collection creation with EphemeralClient."""
        # Use EphemeralClient for testing
        chroma_client = chromadb.EphemeralClient()
        collection_name = "test_collection"

        # Create collection
        collection = chroma_client.create_collection(name=collection_name)
        assert collection.name == collection_name

        # Get existing collection
        existing_collection = chroma_client.get_collection(name=collection_name)
        assert existing_collection.name == collection_name

    @patch("load_data.get_or_create_collection")
    def test_load_data_without_embeddings(self, mock_get_collection, temp_json_file):
        """Test loading data without embeddings using mocked collection."""
        # Setup mock collection
        mock_collection = Mock()
        mock_get_collection.return_value = mock_collection

        from load_data import load_data

        # Test without embeddings (no host/port needed for testing)
        load_data(
            file_path=temp_json_file,
            host="localhost",
            port=8000,
            collection_name="test_collection",
            resource_name="test_resource",
            load_embeddings=False,
        )

        # Verify collection.add was called
        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args
        
        # Check that documents, metadatas, and ids were passed
        assert "documents" in call_args.kwargs
        assert "metadatas" in call_args.kwargs
        assert "ids" in call_args.kwargs
        
        # Verify correct number of documents
        assert len(call_args.kwargs["documents"]) == 3
        assert len(call_args.kwargs["metadatas"]) == 3
        assert len(call_args.kwargs["ids"]) == 3

    def test_openai_embedding_call(self):
        """Test OpenAI embedding function call (mocked)."""
        with patch("openai.Client") as mock_client:
            # Mock the embeddings response
            mock_response = Mock()
            mock_response.data = [
                Mock(embedding=[0.1, 0.2, 0.3]),
                Mock(embedding=[0.4, 0.5, 0.6]),
            ]
            mock_client.return_value.embeddings.create.return_value = mock_response

            # Test embedding function
            embedding_func = OpenAIEmbedding(api_key="test_key")
            result = embedding_func(["test text 1", "test text 2"])

            assert len(result) == 2
            assert list(result[0]) == [0.1, 0.2, 0.3]
            assert list(result[1]) == [0.4, 0.5, 0.6]

    def test_openai_embedding_error(self):
        """Test OpenAI embedding function error handling."""
        with patch("openai.Client") as mock_client:
            # Mock an exception
            mock_client.return_value.embeddings.create.side_effect = Exception("API Error")

            embedding_func = OpenAIEmbedding(api_key="test_key")
            with pytest.raises(Exception):
                embedding_func(["test text"])