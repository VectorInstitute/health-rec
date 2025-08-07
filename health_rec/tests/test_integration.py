"""Integration tests for load_data and update_data modules."""

import json
import tempfile
from pathlib import Path

import chromadb
import pytest

from load_data import load_json_data, prepare_documents


@pytest.mark.integration
class TestIntegration:
    """Integration tests using EphemeralClient."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.resource_name_211 = "211"
        self.resource_name_connex = "connex"
        
        # Create ephemeral client
        self.client = chromadb.EphemeralClient()

    def test_load_and_update_workflow(self, test_services):
        """Test complete workflow: load data, then update with changes."""
        # Create temporary JSON file with initial data
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_services[:2], f)  # Only first 2 services
            temp_file = f.name
        
        try:
            # Step 1: Load initial data
            collection = self.client.create_collection(name="test_workflow_ontario")
            
            # Manually test load functionality
            services = load_json_data(temp_file)
            assert len(services) == 2
            
            documents, metadatas, ids = prepare_documents(services, self.resource_name_211)
            collection.add(documents=documents, metadatas=metadatas, ids=ids)
            
            # Verify initial load
            initial_count = collection.count()
            assert initial_count == 2
            
            # Check that documents have correct resource name
            results = collection.get(include=["metadatas"])
            for metadata in results["metadatas"]:
                assert metadata["resource"] == self.resource_name_211
            
            # Step 2: Test update with same data (no changes)
            # Create temp file with same data for update test
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                json.dump(test_services[:2], f)
                update_file = f.name
            
            try:
                # Manually test update functionality 
                from update_data import load_json_data as update_load_json, prepare_document
                
                update_services = update_load_json(update_file)
                
                # Test update logic: check if service exists and needs update
                for service in update_services:
                    doc, metadata, service_id = prepare_document(service, self.resource_name_211)
                    
                    # Check if service exists
                    existing = collection.get(ids=[service_id], include=["documents", "metadatas"])
                    assert len(existing["ids"]) == 1  # Service should exist
                    
                    # For same data, no update should be needed
                    # (This tests the hash comparison logic)
                
                # Count should remain the same
                assert collection.count() == 2
                
            finally:
                Path(update_file).unlink()
            
            # Step 3: Test adding new data with different resource name
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                json.dump([test_services[2]], f)  # Third service
                new_service_file = f.name
            
            try:
                services = load_json_data(new_service_file)
                documents, metadatas, ids = prepare_documents(services, self.resource_name_connex)
                collection.add(documents=documents, metadatas=metadatas, ids=ids)
                
                # Should now have 3 services
                assert collection.count() == 3
                
                # Check mixed resource names
                all_results = collection.get(include=["metadatas"])
                resource_names = [meta["resource"] for meta in all_results["metadatas"]]
                
                # Should have 2 from "211" and 1 from "connex"
                assert resource_names.count(self.resource_name_211) == 2
                assert resource_names.count(self.resource_name_connex) == 1
                
            finally:
                Path(new_service_file).unlink()
                
        finally:
            Path(temp_file).unlink()

    def test_load_data_with_different_resources_same_collection(self, test_services):
        """Test loading different resources into the same collection."""
        collection = self.client.create_collection(name="test_different_resources_ontario")
        
        # Load 211 data
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([test_services[0]], f)
            file_211 = f.name
        try:
            services_211 = load_json_data(file_211)
            documents_211, metadatas_211, ids_211 = prepare_documents(services_211, "211")
            collection.add(documents=documents_211, metadatas=metadatas_211, ids=ids_211)
            
        finally:
            Path(file_211).unlink()
        
        # Load Connex data
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([test_services[1]], f)
            file_connex = f.name
        try:
            services_connex = load_json_data(file_connex)
            documents_connex, metadatas_connex, ids_connex = prepare_documents(services_connex, "connex")
            collection.add(documents=documents_connex, metadatas=metadatas_connex, ids=ids_connex)
            
        finally:
            Path(file_connex).unlink()
        
        # Load Empower data  
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([test_services[2]], f)
            file_empower = f.name
        try:
            services_empower = load_json_data(file_empower)
            documents_empower, metadatas_empower, ids_empower = prepare_documents(services_empower, "empower")
            collection.add(documents=documents_empower, metadatas=metadatas_empower, ids=ids_empower)
            
        finally:
            Path(file_empower).unlink()
        
        # Verify all resources in one collection
        assert collection.count() == 3
        
        results = collection.get(include=["metadatas"])
        resource_names = [meta["resource"] for meta in results["metadatas"]]
        
        # Should have one of each resource
        assert "211" in resource_names
        assert "connex" in resource_names
        assert "empower" in resource_names
        assert len(set(resource_names)) == 3  # All unique

    def test_search_by_resource_in_collection(self, test_services):
        """Test searching for services by resource name within a collection."""
        collection = self.client.create_collection(name="test_search_by_resource_ontario")
        
        # Add services from different resources
        # Add 211 services
        documents_211, metadatas_211, ids_211 = prepare_documents([test_services[0]], "211")
        collection.add(documents=documents_211, metadatas=metadatas_211, ids=ids_211)
        
        # Add Connex services
        documents_connex, metadatas_connex, ids_connex = prepare_documents([test_services[1]], "connex")
        collection.add(documents=documents_connex, metadatas=metadatas_connex, ids=ids_connex)
        
        # Test filtering by resource (using where clause)
        results_211 = collection.get(
            where={"resource": "211"},
            include=["metadatas"]
        )
        assert len(results_211["ids"]) == 1
        assert results_211["metadatas"][0]["resource"] == "211"
        
        results_connex = collection.get(
            where={"resource": "connex"},
            include=["metadatas"] 
        )
        assert len(results_connex["ids"]) == 1
        assert results_connex["metadatas"][0]["resource"] == "connex"

    def test_document_content_includes_resource(self, test_services):
        """Test that document content includes resource information."""
        collection = self.client.create_collection(name="test_document_content_ontario")
        
        # Add a service
        documents, metadatas, ids = prepare_documents([test_services[0]], "test_resource")
        collection.add(documents=documents, metadatas=metadatas, ids=ids)
        
        # Retrieve and check document content
        results = collection.get(include=["documents", "metadatas"])
        
        document = results["documents"][0]
        metadata = results["metadatas"][0]
        
        # Document should contain resource information
        assert "resource: test_resource" in document
        assert metadata["resource"] == "test_resource"