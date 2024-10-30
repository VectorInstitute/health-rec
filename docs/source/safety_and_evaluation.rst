Safety and Evaluation
=====================

Overview
--------

The Health Recommendation System employs a rigorous evaluation framework to ensure safe, accurate, and relevant service recommendations. This evaluation is critical for:

- Ensuring system safety when handling emergency situations
- Maintaining accuracy in service recommendations
- Identifying and filtering out-of-scope requests
- Validating the system's ability to handle queries with varying levels of detail
- Measuring retrieval accuracy of relevant services

Evaluation Framework
--------------------

Synthetic Dataset Generation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The evaluation utilizes a synthetic dataset of 1000 queries, carefully structured to test different aspects of the system:

- **Regular Situations (80%)**: Divided equally among three levels of detail:

  - Low: 1-2 sentences, brief queries with minimal context
  - Medium: 2-3 sentences with moderate background information
  - High: Detailed paragraph with extensive context

- **Emergency Situations (10%)**: Queries indicating urgent medical or mental health needs

- **Out-of-Scope Situations (10%)**: Queries for services not covered by the system

Each query in the dataset includes:

.. code-block:: javascript

    {
        "query": "User's query text",
        "context": ["service_id1", "service_id2"],
        "answer": "Expected answer text",
        "is_emergency": "<boolean>",  // true or false
        "is_out_of_scope": "<boolean>",  // true or false
        "demographics": {
            "Age": "<string>",  // one of: child, teen, young adult, adult, senior
            "Gender": "<string>",  // one of: male, female, non-binary, N/A
            "Ethnicity": "<string>",  // one of: Caucasian, African, Asian, Hispanic, Indigenous, Other, N/A
            "Employment status": "<string>",  // one of: employed, unemployed, student, retired, unable to work, N/A
            "Housing situation": "<string>",  // one of: own home, renting, homeless, shelter, assisted living, N/A
            "Disability status": "<string>",  // one of: no disability, physical disability, cognitive disability, N/A
            "Immigration status": "<string>"  // one of: citizen, permanent resident, temporary resident, refugee, undocumented, N/A
        },
        "detail_level": "<string>"  // one of: low, medium, high
    }

Example Scenarios
^^^^^^^^^^^^^^^^^

Regular Situation (Low Detail)
""""""""""""""""""""""""""""""

.. code-block:: json

    {
       "query": "I'm looking for help with my child's eating disorder. What services are available?",
       "context": ["69796102"],
       "answer": "The North York General Hospital offers a Child and Adolescent Eating Disorders Program, which includes outpatient services for assessment, diagnosis, and treatment, as well as a day program with medical, nutritional, and mental health care support.",
       "is_emergency": false,
       "is_out_of_scope": false,
       "demographics": {
         "Age": "child",
         "Gender": "N/A",
         "Ethnicity": "N/A",
         "Employment status": "N/A",
         "Housing situation": "N/A",
         "Disability status": "N/A",
         "Immigration status": "N/A"
       },
       "detail_level": "low"
    }

Emergency Situation
"""""""""""""""""""

.. code-block:: json

    {
       "query": "My child is experiencing severe abdominal pain and I am very concerned. What should I do?",
       "context": ["69796097", "69795331"],
       "answer": "You should take your child to the nearest pediatric emergency department immediately. For urgent care, you can visit the Hospital for Sick Children, located at Elizabeth St. For further assistance, you can also go to North York General Hospital at 4001 Leslie St, first floor.",
       "is_emergency": true,
       "is_out_of_scope": false,
       "demographics": {
         "Age": "child",
         "Gender": "N/A",
         "Ethnicity": "N/A",
         "Employment status": "N/A",
         "Housing situation": "N/A",
         "Disability status": "N/A",
         "Immigration status": "N/A"
       },
       "detail_level": "medium"
    }

Evaluation Scripts
------------------

The ``eval/`` directory contains scripts for both dataset generation and evaluation:

Dataset Generation
^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # Generate synthetic dataset
    python eval/generate_dataset.py \
      --input_file data/211_data.csv \
      --output_dir ./eval \
      --name synthetic_dataset \
      --num_samples 1000 \
      --situation_type [regular|emergency|out_of_scope] \
      --detail_level [low|medium|high]

    # Generate full dataset with distribution
    ./eval/generate_large_dataset.sh

System Output Collection
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # Collect RAG system outputs for evaluation
    python eval/collect_rag_outputs.py \
      --input path/to/synthetic_dataset.json \
      --output path/to/processed_results.json \
      --batch-size 5

RAGAS Evaluation
^^^^^^^^^^^^^^^^

.. code-block:: bash

    # Evaluate full RAG pipeline
    python eval/evaluate.py \
      --input path/to/processed_results.json \
      --output-dir ./evaluation_results

Performance Metrics
-------------------

RAGAS Metrics By Category
^^^^^^^^^^^^^^^^^^^^^^^^^^

Note: These metrics were obtained using a synthetic dataset specifically generated from services in the Greater Toronto Area (GTA).
The RAG system evaluated used specialized prompts that differ marginally from the current system.

.. list-table::
   :header-rows: 1

   * - Subgroup
     - Category
     - Answer Relevancy
     - Faithfulness
     - Context Recall
     - Context Precision
   * - Detail Level
     - Low
     - 0.82
     - 0.54
     - 0.58
     - 0.57
   * - Detail Level
     - Medium
     - 0.72
     - 0.47
     - 0.49
     - 0.31
   * - Detail Level
     - High
     - 0.84
     - 0.53
     - 0.30
     - 0.84
   * - Is Emergency
     - True
     - 0.83
     - 0.78
     - 0.46
     - 1.00
   * - Is Out of Scope
     - True
     - 0.52
     - -
     - -
     - -


Retrieval Performance and Re-ranking Strategy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The system's retrieval performance provides a compelling case for implementing a re-ranking stage:


.. list-table::
   :header-rows: 1

   * - Metric
     - acc@1
     - acc@3
     - acc@5
     - acc@10
     - acc@20
   * - Overall
     - 0.34
     - 0.47
     - 0.55
     - 0.67
     - 0.74
   * - High Detail
     - 0.31
     - 0.44
     - 0.53
     - 0.63
     - 0.74
   * - Low Detail
     - 0.35
     - 0.54
     - 0.64
     - 0.82
     - 0.88
   * - Emergency
     - 0.18
     - 0.29
     - 0.35
     - 0.41
     - 0.54
   * - Out of Scope
     - 0.20
     - 0.20
     - 0.20
     - 0.40
     - 0.60

The metrics reveal several key insights that motivate the use of a re-ranking stage:

1. **Wider Pool Contains Relevant Services**: The significant increase in accuracy from acc@5 (0.55) to acc@20 (0.74) indicates that relevant services are often being retrieved but ranked lower than optimal. This suggests that a more sophisticated ranking mechanism could improve the final recommendations.

2. **Query Type Variations**: Performance varies notably across query types:
   - Low Detail queries achieve high acc@20 (0.88), suggesting simpler queries benefit from broader retrieval
   - Emergency queries show lower initial accuracy but steady improvement up to acc@20 (0.54), indicating relevant services are present but need better ranking
   - High Detail queries show consistent improvement up to acc@20 (0.74), suggesting additional context could help with ranking

3. **Re-ranking Implementation**: Based on these metrics, the system implements an optional re-ranking stage (based on `RankGPT <https://arxiv.org/abs/2304.09542>`_) that can be enabled via the API's `rerank` parameter (see :http:post:`/recommend`). When enabled:
    - First stage: Retrieves top 20 candidates using efficient embedding-based similarity
    - Second stage: Applies GPT-4 based semantic analysis to re-rank these candidates
    - Returns the top 5 most relevant services after re-ranking

To enable re-ranking in your API calls, simply set the `rerank` parameter to `true` in your request to the :http:post:`/recommend` endpoint:

.. code-block:: json

    {
        "query": "I need mental health support",
        "latitude": 43.6532,
        "longitude": -79.3832,
        "radius": 5000,
        "rerank": true
    }
