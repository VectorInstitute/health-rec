"""Unit tests for update_data.py module."""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import chromadb
import pytest

from update_data import calculate_hash, prepare_document, update_data


class TestUpdateData:
    """Unit tests for update_data module."""

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
        # Using prepare_document function imported at module level

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
            # Using prepare_document function imported at module level

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


class TestUpdateDataDeduplication:
    """Integration tests for update_data with deduplication."""

    @pytest.fixture
    def services_with_duplicates_json(self):
        """Create a temporary JSON file with duplicate services for update testing."""
        base_time = datetime.now()
        services_data = [
            {
                "id": "1",
                "name": "Medical Center",
                "description": "Updated primary care",
                "latitude": 43.6532,
                "longitude": -79.3832,
                "phone_numbers": [{"number": "416-555-1234", "type": "primary"}],
                "email": "medical1@example.com",
                "last_updated": base_time.isoformat(),
            },
            {
                "id": "2",
                "name": "Medical Center",  # Duplicate
                "description": "Same location, updated description",
                "latitude": 43.6532,
                "longitude": -79.3832,
                "phone_numbers": [{"number": "416-555-5678", "type": "primary"}],
                "address": {"street1": "123 Main St", "city": "Toronto"},
                "metadata": {"email": "medical2@example.com"},
                "last_updated": (
                    base_time + timedelta(hours=2)
                ).isoformat(),  # More recent
            },
            {
                "id": "3",
                "name": "Wellness Center",
                "description": "Updated wellness services",
                "latitude": 43.6600,
                "longitude": -79.3900,
                "phone_numbers": [{"number": "416-555-9999", "type": "primary"}],
                "email": "wellness@example.com",
                "last_updated": base_time.isoformat(),
            },
            {
                "id": "4",
                "name": "Medical Center",  # Another duplicate
                "description": "Third instance, older",
                "latitude": 43.6532,
                "longitude": -79.3832,
                "phone_numbers": [{"number": "416-555-0000", "type": "primary"}],
                "address": {"street1": "123 Main St", "city": "Toronto"},
                "metadata": {"email": "medical3@example.com"},
                "last_updated": (base_time - timedelta(hours=1)).isoformat(),  # Oldest
            },
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(services_data, f, indent=2)
            temp_path = f.name

        yield temp_path
        Path(temp_path).unlink(missing_ok=True)

    @patch("update_data.get_or_create_collection")
    @patch("update_data.logger")
    def test_update_data_with_deduplication_enabled(
        self, mock_logger, mock_get_collection, services_with_duplicates_json
    ):
        """Test update_data with deduplication enabled."""
        # Setup mock collection
        mock_collection = Mock()
        mock_get_collection.return_value = mock_collection

        # Mock that all services are new (not existing)
        mock_collection.get.return_value = {"ids": []}

        # Call update_data with deduplication enabled
        update_data(
            file_path=services_with_duplicates_json,
            host="localhost",
            port=8000,
            collection_name="test_collection",
            resource_name="test",
            load_embeddings=False,
            remove_duplicates_before_update=True,
        )

        # Verify deduplication logging
        mock_logger.info.assert_any_call(
            "Removed 2 duplicate services during data update"
        )

        # Verify collection operations
        # Should have 2 unique services after deduplication
        add_calls = list(mock_collection.add.call_args_list)
        update_calls = list(mock_collection.update.call_args_list)
        total_operations = len(add_calls) + len(update_calls)

        assert total_operations == 2  # 2 unique services

    @patch("update_data.get_or_create_collection")
    @patch("update_data.logger")
    def test_update_data_with_deduplication_disabled(
        self, mock_logger, mock_get_collection, services_with_duplicates_json
    ):
        """Test update_data with deduplication disabled."""
        # Setup mock collection
        mock_collection = Mock()
        mock_get_collection.return_value = mock_collection

        # Mock that all services are new (not existing)
        mock_collection.get.return_value = {"ids": []}

        # Call update_data with deduplication disabled
        update_data(
            file_path=services_with_duplicates_json,
            host="localhost",
            port=8000,
            collection_name="test_collection",
            resource_name="test",
            load_embeddings=False,
            remove_duplicates_before_update=False,
        )

        # Verify no deduplication logging
        dedup_logs = [
            call for call in mock_logger.info.call_args_list if "duplicate" in str(call)
        ]
        assert len(dedup_logs) == 0

        # Verify collection operations
        # Should have all 4 services processed
        add_calls = list(mock_collection.add.call_args_list)
        update_calls = list(mock_collection.update.call_args_list)
        total_operations = len(add_calls) + len(update_calls)

        assert total_operations == 4  # All 4 services

    @patch("update_data.get_or_create_collection")
    def test_update_data_preserves_existing_unique_services(
        self, mock_get_collection, services_with_duplicates_json
    ):
        """Test deduplication preserves existing services that aren't duplicates."""
        # Setup mock collection
        mock_collection = Mock()
        mock_get_collection.return_value = mock_collection

        # Mock get method to simulate existing service "3" and new services for others
        def mock_get_side_effect(ids, **kwargs):
            if ids[0] == "3":
                # Service 3 already exists
                return {
                    "ids": ["3"],
                    "documents": ["existing doc"],
                    "metadatas": [{"name": "Old Wellness Center", "resource": "test"}],
                }
            # Other services are new
            return {"ids": []}

        mock_collection.get.side_effect = mock_get_side_effect

        # Call update_data with deduplication enabled
        update_data(
            file_path=services_with_duplicates_json,
            host="localhost",
            port=8000,
            collection_name="test_collection",
            resource_name="test",
            load_embeddings=False,
            remove_duplicates_before_update=True,
        )

        # Verify that service 3 was updated (not added)
        # and only one Medical Center was added
        add_calls = mock_collection.add.call_args_list
        update_calls = mock_collection.update.call_args_list

        # Should have 1 add call (for the deduplicated Medical Center)
        # and 1 update call (for the existing Wellness Center)
        assert len(add_calls) == 1
        assert len(update_calls) == 1
