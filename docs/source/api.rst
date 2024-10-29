API Reference
=============

This section provides detailed information about the API endpoints for the Health Recommendation System.

Health Recommendations
----------------------

.. http:post:: /recommend

   Generate a health service recommendation based on the input query.

   **Request Body**

   .. code-block:: json

      {
         "query": "I need mental health support",
         "latitude": 43.6532,
         "longitude": -79.3832,
         "radius": 5000
      }

   :<json string query: The user's health-related query (required)
   :<json number latitude: Optional latitude for location-based search
   :<json number longitude: Optional longitude for location-based search
   :<json number radius: Optional search radius in meters

   **Response Body**

   .. code-block:: json

      {
         "message": "Based on your query...",
         "is_emergency": false,
         "is_out_of_scope": false,
         "services": [
            {
               "id": "service_id",
               "name": "Service Name",
               "description": "Service description",
               "categories": ["category1", "category2"],
               "address": "123 Health St",
               "phone_numbers": [{
                  "number": "+1-123-456-7890",
                  "type": "Main"
               }],
               "website": "https://example.com",
               "hours": "Monday-Friday 9AM-5PM"
            }
         ],
         "no_services_found": false
      }

   :>json string message: Generated recommendation text
   :>json boolean is_emergency: Indicates if the query suggests an emergency
   :>json boolean is_out_of_scope: Indicates if the query is outside service scope
   :>json array services: List of relevant health services (optional)
   :>json boolean no_services_found: Indicates if no matching services were found
   :status 200: Recommendation generated successfully
   :status 422: Invalid request parameters
   :status 500: Server error

Question Generation
-------------------

.. http:get:: /questions

   Generate follow-up questions based on the initial query and recommendation.

   **Example Request**

   .. code-block:: bash

      GET /questions?query=mental+health+support&recommendation=Based+on+your+query...

   :query string query: The user's original health query (required)
   :query string recommendation: The previously generated recommendation (required)

   **Response Body**

   .. code-block:: json

      {
         "questions": [
            "Do you prefer in-person or virtual care?",
            "What type of mental health support are you looking for?"
         ]
      }

   :>json array questions: List of generated follow-up questions
   :status 200: Questions generated successfully
   :status 400: Invalid query parameters
   :status 500: Server error

Recommendation Refinement
-------------------------

.. http:post:: /refine_recommendations

   Refine the initial recommendation based on answers to follow-up questions.

   **Request Body**

   .. code-block:: json

      {
         "query": {
            "query": "mental health support",
            "latitude": 43.6532,
            "longitude": -79.3832,
            "radius": 5000
         },
         "questions": ["Do you prefer in-person or virtual care?"],
         "answers": ["in-person"],
         "recommendation": "Previous recommendation text..."
      }

   :<json object query: Query object containing:
   :<json string query.query: The user's health-related query (required)
   :<json number query.latitude: Optional latitude for location-based search
   :<json number query.longitude: Optional longitude for location-based search
   :<json number query.radius: Optional search radius in meters
   :<json array questions: List of follow-up questions (required)
   :<json array answers: User's answers to the follow-up questions (required)
   :<json string recommendation: The previous recommendation (required)

   **Response Body**

   .. code-block:: json

      {
         "message": "Based on your preferences...",
         "is_emergency": false,
         "is_out_of_scope": false,
         "services": [
            {
               "id": "service_id",
               "name": "Service Name",
               "description": "Service description"
            }
         ],
         "no_services_found": false
      }

   :>json string message: Refined recommendation text
   :>json boolean is_emergency: Updated emergency status
   :>json boolean is_out_of_scope: Updated scope status
   :>json array services: Updated list of relevant services (optional)
   :>json boolean no_services_found: Indicates if no matching services were found
   :status 200: Recommendation refined successfully
   :status 422: Invalid request data
   :status 500: Server error

Service Information
-------------------

.. http:get:: /services/all

   Retrieve all available health services from the database.

   **Response Body**

   .. code-block:: json

      [
         {
            "id": "service_id",
            "name": "Service Name",
            "description": "Service description",
            "categories": ["category1", "category2"],
            "address": "123 Health St",
            "phone_numbers": [{
               "number": "+1-123-456-7890",
               "type": "Main"
            }],
            "website": "https://example.com",
            "hours": "Monday-Friday 9AM-5PM"
         }
      ]

   :>json array services: List of all health services
   :status 200: Services retrieved successfully
   :status 500: Server error

.. http:get:: /services/count

   Get the total number of available health services.

   **Response Body**

   .. code-block:: json

      {
         "count": 150
      }

   :>json integer count: Total number of services in the database
   :status 200: Count retrieved successfully
   :status 500: Server error

Error Responses
---------------

All endpoints may return the following error responses:

.. code-block:: json

   {
      "detail": "Error message describing what went wrong"
   }

Common HTTP Status Codes
------------------------

- ``200 OK``: Request successful
- ``400 Bad Request``: Invalid parameters
- ``422 Unprocessable Entity``: Invalid request body
- ``500 Internal Server Error``: Server-side error
