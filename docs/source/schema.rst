Data Schema
===========

The recommendation system aims to provide users with relevant health resources based on their initial query.
We can use service data from different sources such as the `Ontario 211 API <https://211ontario.ca/211-data/>`_
or the `Empower API <https://www.empower.ca/it>`_. But, for the recommendation system, we use a common schema.

The schema is as follows:

.. code-block:: json

    [
        {
            "id": "1",
            "name": "Test Service 1",
            "description": "This is a test service 1 providing medical clinic services.",
            "latitude": 43.563807766096275,
            "longitude": -79.40435634607296,
            "phone_numbers": [
                {
                    "number": "574-696-8554",
                    "type": "primary",
                    "name": "Test Service 1",
                    "description": "This is the primary phone number for Test Service 1.",
                    "extension": "123"
                }
            ],
            "address": {
                "street1": "994 Yonge Street",
                "city": "Toronto",
                "province": "ON",
                "postal_code": "M5E1 B07",
                "country": "Canada"
            },
            "email": "service1@example.com",
            "metadata": {
                "type": "Medical Clinic",
                "languages": [
                    "English",
                    "French"
                ]
            }
        }
    ]

The schema is a JSON object with the following fields:

- ``id``: A unique identifier for the service.
- ``name``: The name of the service.
- ``description``: A brief description of the service.
- ``latitude``: The latitude of the service location.
- ``longitude``: The longitude of the service location.
- ``phone_numbers``: A list of phone numbers associated with the service. Each phone number object has two fields:
  - ``number``: The phone number.
  - ``type``: The type of the phone number (e.g., primary, secondary).
- ``address``: The address of the service. The address object has the following fields:
    - ``street1``: The first line of the street address.
    - ``city``: The city where the service is located.
    - ``province``: The province where the service is located.
    - ``postal_code``: The postal code of the service location.
    - ``country``: The country where the service is located.
- ``metadata``: Additional metadata about the service. The metadata object can have any number of fields.
