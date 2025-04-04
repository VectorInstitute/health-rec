# API Reference

This section provides detailed information about the API endpoints for the Health Recommendation System.

## Health Recommendations

### POST /recommend

Generate a health service recommendation based on the input query.

**Request Body**

```json
{
   "query": "I need mental health support",
   "latitude": 43.6532,
   "longitude": -79.3832,
   "radius": 5000,
   "rerank": false
}
```

**Parameters:**
- `query` (string, required): The user's health-related query
- `latitude` (number, optional): Latitude for location-based search
- `longitude` (number, optional): Longitude for location-based search
- `radius` (number, optional): Search radius in meters (default: 5000)
- `rerank` (boolean, optional): Flag to enable/disable reranking of the services (default: false)

**Response Body**

```json
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
```

**Response Fields:**
- `message` (string): Generated recommendation text
- `is_emergency` (boolean): Indicates if the query suggests an emergency
- `is_out_of_scope` (boolean): Indicates if the query is outside service scope
- `services` (array, optional): List of relevant health services
- `no_services_found` (boolean): Indicates if no matching services were found

**Status Codes:**
- `200`: Recommendation generated successfully
- `422`: Invalid request parameters
- `500`: Server error

## Question Generation

### GET /questions

Generate follow-up questions based on the initial query and recommendation.

**Example Request**

```bash
GET /questions?query=mental+health+support&recommendation=Based+on+your+query...
```

**Query Parameters:**
- `query` (string, required): The user's original health query
- `recommendation` (string, required): The previously generated recommendation

**Response Body**

```json
{
   "questions": [
      "Do you prefer in-person or virtual care?",
      "What type of mental health support are you looking for?"
   ]
}
```

**Response Fields:**
- `questions` (array): List of generated follow-up questions

**Status Codes:**
- `200`: Questions generated successfully
- `400`: Invalid query parameters
- `500`: Server error

## Recommendation Refinement

### POST /refine_recommendations

Refine the initial recommendation based on answers to follow-up questions.

**Request Body**

```json
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
```

**Request Fields:**
- `query` (object): Query object containing:
  - `query.query` (string, required): The user's health-related query
  - `query.latitude` (number, optional): Latitude for location-based search
  - `query.longitude` (number, optional): Longitude for location-based search
  - `query.radius` (number, optional): Search radius in meters
- `questions` (array, required): List of follow-up questions
- `answers` (array, required): User's answers to the follow-up questions
- `recommendation` (string, required): The previous recommendation

**Response Body**

```json
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
```

**Response Fields:**
- `message` (string): Refined recommendation text
- `is_emergency` (boolean): Updated emergency status
- `is_out_of_scope` (boolean): Updated scope status
- `services` (array, optional): Updated list of relevant services
- `no_services_found` (boolean): Indicates if no matching services were found

**Status Codes:**
- `200`: Recommendation refined successfully
- `422`: Invalid request data
- `500`: Server error

## Service Information

### GET /services/all

Retrieve all available health services from the database.

**Response Body**

```json
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
```

**Response Fields:**
- `services` (array): List of all health services

**Status Codes:**
- `200`: Services retrieved successfully
- `500`: Server error

### GET /services/count

Get the total number of available health services.

**Response Body**

```json
{
   "count": 150
}
```

**Response Fields:**
- `count` (integer): Total number of services in the database

**Status Codes:**
- `200`: Count retrieved successfully
- `500`: Server error

## Error Responses

All endpoints may return the following error responses:

```json
{
   "detail": "Error message describing what went wrong"
}
```

## Common HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid parameters
- `422 Unprocessable Entity`: Invalid request body
- `500 Internal Server Error`: Server-side error

## API Benchmark

The following table shows latency benchmarks for the /recommend API endpoint. Tests were run with different combinations of query parameters and reranking options. Each request was made sequentially to measure individual request latency accurately.
The summary statistics are generating from 50 runs with a timeout of 30 seconds w/ no delay between each request.

| Test Case | Mean (s) | Median (s) | Std Dev (s) | Min (s) | Max (s) | Sample Size |
|-----------|----------|------------|-------------|---------|---------|-------------|
| Query only | 6.686 | 5.985 | 2.336 | 4.504 | 19.362 | 48 |
| Query w/ reranking | 8.729 | 8.547 | 1.964 | 5.249 | 14.133 | 50 |
| Query w/ location | 6.795 | 6.260 | 3.560 | 3.277 | 27.860 | 46 |
| Query w/ location and reranking | 8.197 | 7.934 | 1.867 | 5.720 | 13.688 | 50 |
