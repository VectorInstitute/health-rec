"""Utility functions for the services module."""

import json
import logging
from typing import Any, Dict, List

from chromadb.api.types import QueryResult

from api.data import PhoneNumber, Service, ServiceDocument


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _parse_chroma_result(chroma_results: QueryResult) -> List[ServiceDocument]:
    """
    Parse the results from ChromaDB into a list of Service objects.

    Parameters
    ----------
    chroma_results : QueryResult
        The results from a ChromaDB query.

    Returns
    -------
    List[ServiceDocument]
        A list of ServiceDocument objects created from the ChromaDB results.
    """
    parsed_results: List[ServiceDocument] = [
        ServiceDocument(id=id_, document=doc, metadata=meta, relevancy_score=score)
        for id_, doc, meta, score in zip(
            chroma_results["ids"][0] if chroma_results["ids"] else [],
            chroma_results["documents"][0] if chroma_results["documents"] else [],
            chroma_results["metadatas"][0] if chroma_results["metadatas"] else [],
            chroma_results["distances"][0] if chroma_results["distances"] else [],
        )
    ]

    return parsed_results


def _metadata_to_service(metadata: Dict[str, Any]) -> Service:
    """
    Convert metadata to a Service object.

    Parameters
    ----------
    metadata : Dict[str, Any]
        The metadata dictionary containing service information.

    Returns
    -------
    Service
        A Service object created from the metadata.
    """
    # Handle ServiceArea
    if "ServiceArea" in metadata:
        if isinstance(metadata["ServiceArea"], str):
            metadata["ServiceArea"] = [
                s.strip() for s in metadata["ServiceArea"].split(",")
            ]
        elif metadata["ServiceArea"] is None:
            metadata["ServiceArea"] = []
    else:
        metadata["ServiceArea"] = []

    # Convert numeric fields
    metadata["Latitude"] = (
        float(metadata["Latitude"]) if metadata.get("Latitude") else None
    )
    metadata["Longitude"] = (
        float(metadata["Longitude"]) if metadata.get("Longitude") else None
    )
    metadata["Score"] = int(metadata["Score"]) if metadata.get("Score") else None
    metadata["ParentId"] = (
        int(metadata["ParentId"]) if metadata.get("ParentId") else None
    )

    # Handle PhoneNumbers
    if "PhoneNumbers" in metadata:
        if isinstance(metadata["PhoneNumbers"], str):
            try:
                phone_numbers = json.loads(metadata["PhoneNumbers"])
            except json.JSONDecodeError:
                phone_numbers = []
        elif isinstance(metadata["PhoneNumbers"], list):
            phone_numbers = metadata["PhoneNumbers"]
        else:
            phone_numbers = []

        metadata["PhoneNumbers"] = [PhoneNumber(**phone) for phone in phone_numbers]
    else:
        metadata["PhoneNumbers"] = []

    return Service(
        id=int(metadata["id"]),
        parent_id=metadata["ParentId"],
        public_name=metadata["PublicName"],
        score=metadata["Score"],
        service_area=metadata["ServiceArea"],
        distance=metadata.get("Distance"),
        description=metadata.get("Description"),
        latitude=metadata["Latitude"],
        longitude=metadata["Longitude"],
        physical_address_street1=metadata.get("PhysicalAddressStreet1"),
        physical_address_street2=metadata.get("PhysicalAddressStreet2"),
        physical_address_city=metadata.get("PhysicalAddressCity"),
        physical_address_province=metadata.get("PhysicalAddressProvince"),
        physical_address_postal_code=metadata.get("PhysicalAddressPostalCode"),
        physical_address_country=metadata.get("PhysicalAddressCountry"),
        mailing_attention_name=metadata.get("MailingAttentionName"),
        mailing_address_street1=metadata.get("MailingAddressStreet1"),
        mailing_address_street2=metadata.get("MailingAddressStreet2"),
        mailing_address_city=metadata.get("MailingAddressCity"),
        mailing_address_province=metadata.get("MailingAddressProvince"),
        mailing_address_postal_code=metadata.get("MailingAddressPostalCode"),
        mailing_address_country=metadata.get("MailingAddressCountry"),
        phone_numbers=metadata["PhoneNumbers"],
        website=metadata.get("Website"),
        email=metadata.get("Email"),
        hours=metadata.get("Hours"),
        hours2=metadata.get("Hours2"),
        min_age=metadata.get("MinAge"),
        max_age=metadata.get("MaxAge"),
        updated_on=metadata.get("UpdatedOn"),
        taxonomy_term=metadata.get("TaxonomyTerm"),
        taxonomy_terms=metadata.get("TaxonomyTerms"),
        taxonomy_codes=metadata.get("TaxonomyCodes"),
        eligibility=metadata.get("Eligibility"),
        fee_structure_source=metadata.get("FeeStructureSource"),
        official_name=metadata.get("OfficialName"),
        physical_city=metadata.get("PhysicalCity"),
        unique_id_prior_system=metadata.get("UniqueIDPriorSystem"),
        record_owner=metadata.get("RecordOwner"),
    )
