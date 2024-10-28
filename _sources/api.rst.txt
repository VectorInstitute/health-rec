API Reference
=============

This section provides detailed information about the API endpoints.

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

   :<json string query: The user's health-related query
   :<json number latitude: Optional latitude for location-based search
   :<json number longitude: Optional longitude for location-based search
   :<json number radius: Optional search radius in meters (default: 5000)
   :>json string recommendation: Generated recommendation text
   :>json array services: List of relevant health services
   :>json boolean is_emergency: Indicates if the query suggests an emergency
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

   :query string query: The user's original health query
   :query string recommendation: The previously generated recommendation
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

   :<json object query: The original query object with search parameters
   :<json array questions: List of follow-up questions
   :<json array answers: User's answers to the follow-up questions
   :<json string recommendation: The previous recommendation
   :>json string recommendation: Refined recommendation text
   :>json array services: Updated list of relevant services
   :>json boolean is_emergency: Updated emergency status
   :status 200: Recommendation refined successfully
   :status 422: Invalid request data
   :status 500: Server error

Service Information
-------------------

.. http:get:: /services/all

   Retrieve all available health services from the database.

   :>json array services: List of all health services with details:

   .. code-block:: json

      [{
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
      }]

   :status 200: Services retrieved successfully
   :status 500: Server error

.. http:get:: /services/count

   Get the total number of available health services.

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
