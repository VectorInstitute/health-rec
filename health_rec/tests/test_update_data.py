"""Unit tests for update_data.py module."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import chromadb
import pytest

from update_data import calculate_hash, prepare_document, update_data


@pytest.mark.unit
class TestUpdateData:
    def test_calculate_hash(self):
        """Test hash calculation for consistency."""
        test_dict = {"key1": "value1", "key2": "value2"}

        # Same dictionary should produce same hash
        hash1 = calculate_hash(test_dict)
        hash2 = calculate_hash(test_dict)
        assert hash1 == hash2

        # Different dictionaries should produce different hashes
        different_dict = {"key1": "value1", "key2": "different_value"}
        hash3 = calculate_hash(different_dict)
        assert hash1 != hash3

        # Order shouldn't matter (sorted internally)
        reordered_dict = {"key2": "value2", "key1": "value1"}
        hash4 = calculate_hash(reordered_dict)
        assert hash1 == hash4

    def test_prepare_document(self, sample_service):
        """Test document preparation for a service."""
        resource_name = "test_resource"
        doc, metadata, service_id = prepare_document(sample_service, resource_name)

        # Check service ID extraction
        assert service_id == "single_test"

        # Check resource name is added to metadata
        assert metadata["resource"] == resource_name

        # Check metadata contains converted service data
        assert metadata["name"] == "Test Service"
        assert metadata["description"] == "A single test service"

        # Check document format
        assert isinstance(doc, str)
        assert "name: Test Service" in doc
        assert "resource: test_resource" in doc

    def test_prepare_document_with_lists(self):
        """Test document preparation with list values."""
        service_with_lists = {
            "id": "test_list",
            "name": "Service with Lists",
            "tags": ["tag1", "tag2", "tag3"],
            "categories": ["health", "mental health"],
        }

        resource_name = "test_resource"
        doc, metadata, service_id = prepare_document(service_with_lists, resource_name)

        # Lists should be joined with commas
        assert metadata["tags"] == "tag1, tag2, tag3"
        assert metadata["categories"] == "health, mental health"
        assert "tags: tag1, tag2, tag3" in doc

    def test_prepare_document_with_none_values(self):
        """Test document preparation with None values."""
        service_with_none = {
            "id": "test_none",
            "name": "Service with None",
            "description": None,
            "email": None,
        }

        resource_name = "test_resource"
        doc, metadata, service_id = prepare_document(service_with_none, resource_name)

        # None values should become empty strings
        assert metadata["description"] == ""
        assert metadata["email"] == ""
        # Empty values should not appear in document
        assert "description: " not in doc
        assert "email: " not in doc

    @patch("update_data.get_or_create_collection")
    @patch("update_data.load_json_data")
    def test_update_data_new_service(
        self, mock_load_json, mock_get_collection, sample_service
    ):
        """Test updating data with a new service."""
        # Setup mocks
        mock_load_json.return_value = [sample_service]
        mock_collection = Mock()
        mock_get_collection.return_value = mock_collection

        # Mock collection.get to return empty (service doesn't exist)
        mock_collection.get.return_value = {"ids": []}

        # Test update without embeddings
        update_data(
            file_path="test_file.json",
            host="localhost",
            port=8000,
            collection_name="test_collection",
            resource_name="test_resource",
            load_embeddings=False,
        )

        # Verify collection.add was called (new service)
        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args

        assert call_args.kwargs["ids"] == ["single_test"]
        assert call_args.kwargs["embeddings"][0] is None  # No embeddings

        # Verify collection.update was not called
        mock_collection.update.assert_not_called()

    @patch("update_data.get_or_create_collection")
    @patch("update_data.load_json_data")
    def test_update_data_existing_service_unchanged(
        self, mock_load_json, mock_get_collection, sample_service
    ):
        """Test updating data with existing unchanged service."""
        # Setup mocks
        mock_load_json.return_value = [sample_service]
        mock_collection = Mock()
        mock_get_collection.return_value = mock_collection

        # Prepare the same document that would be generated
        from update_data import prepare_document

        doc, metadata, service_id = prepare_document(sample_service, "test_resource")

        # Mock collection.get to return existing identical data
        mock_collection.get.return_value = {
            "ids": [service_id],
            "documents": [doc],
            "metadatas": [metadata],
        }

        # Test update
        update_data(
            file_path="test_file.json",
            host="localhost",
            port=8000,
            collection_name="test_collection",
            resource_name="test_resource",
            load_embeddings=False,
        )

        # Verify neither add nor update was called (no changes)
        mock_collection.add.assert_not_called()
        mock_collection.update.assert_not_called()

    @patch("update_data.get_or_create_collection")
    @patch("update_data.load_json_data")
    def test_update_data_existing_service_changed(
        self, mock_load_json, mock_get_collection, sample_service
    ):
        """Test updating data with existing changed service."""
        # Setup mocks
        mock_load_json.return_value = [sample_service]
        mock_collection = Mock()
        mock_get_collection.return_value = mock_collection

        # Mock collection.get to return existing different data
        old_metadata = {"name": "Old Service Name", "resource": "test_resource"}
        old_doc = "name: Old Service Name | resource: test_resource"

        mock_collection.get.return_value = {
            "ids": ["single_test"],
            "documents": [old_doc],
            "metadatas": [old_metadata],
        }

        # Test update
        update_data(
            file_path="test_file.json",
            host="localhost",
            port=8000,
            collection_name="test_collection",
            resource_name="test_resource",
            load_embeddings=False,
        )

        # Verify collection.update was called (existing service changed)
        mock_collection.update.assert_called_once()
        call_args = mock_collection.update.call_args

        assert call_args.kwargs["ids"] == ["single_test"]
        assert call_args.kwargs["embeddings"][0] is None  # No embeddings

        # Verify collection.add was not called
        mock_collection.add.assert_not_called()

    @patch("update_data.OpenAIEmbedding")
    @patch("update_data.get_or_create_collection")
    @patch("update_data.load_json_data")
    def test_update_data_with_embeddings(
        self, mock_load_json, mock_get_collection, mock_embedding_class, sample_service
    ):
        """Test updating data with embeddings enabled."""
        # Setup mocks
        mock_load_json.return_value = [sample_service]
        mock_collection = Mock()
        mock_get_collection.return_value = mock_collection
        mock_collection.get.return_value = {"ids": []}  # New service

        # Mock embedding function
        mock_embedding_instance = Mock()
        mock_embedding_instance.return_value = [[0.1, 0.2, 0.3]]
        mock_embedding_class.return_value = mock_embedding_instance

        # Test update with embeddings
        update_data(
            file_path="test_file.json",
            host="localhost",
            port=8000,
            collection_name="test_collection",
            resource_name="test_resource",
            openai_api_key="test_key",
            load_embeddings=True,
        )

        # Verify embedding was generated
        mock_embedding_class.assert_called_once_with(
            api_key="test_key", model="text-embedding-3-small"
        )
        mock_embedding_instance.assert_called_once()

        # Verify collection.add was called with embedding
        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args
        assert call_args.kwargs["embeddings"] == [[0.1, 0.2, 0.3]]

    @patch("update_data.get_or_create_collection")
    @patch("update_data.load_json_data")
    def test_update_data_processing_error(
        self, mock_load_json, mock_get_collection, sample_service
    ):
        """Test handling of processing errors for individual services."""
        # Setup mocks
        mock_load_json.return_value = [sample_service]
        mock_collection = Mock()
        mock_get_collection.return_value = mock_collection

        # Mock collection.get to raise an exception
        mock_collection.get.side_effect = Exception("Database error")

        # Test should not raise exception (errors are caught and logged)
        # This should pass without raising an exception
        update_data(
            file_path="test_file.json",
            host="localhost",
            port=8000,
            collection_name="test_collection",
            resource_name="test_resource",
            load_embeddings=False,
        )

    def test_integration_with_ephemeral_client(self, test_services):
        """Integration test using EphemeralClient."""
        # Create temporary JSON file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_services, f)
            temp_path = f.name

        try:
            # Use EphemeralClient for testing
            chroma_client = chromadb.EphemeralClient()
            collection = chroma_client.create_collection(name="test_update_collection")

            # Manually add initial service
            from update_data import prepare_document

            doc, metadata, service_id = prepare_document(
                test_services[0], "test_resource"
            )
            collection.add(ids=[service_id], documents=[doc], metadatas=[metadata])

            # Verify service was added
            result = collection.get(ids=[service_id])
            assert len(result["ids"]) == 1
            assert result["ids"][0] == "test_service_1"

        finally:
            Path(temp_path).unlink()
