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

Installation for Evaluation
----------------------------

To run the evaluation pipeline, you'll need to install additional dependencies from the `eval` subgroup. From the project root:

.. code-block:: bash

    # Create virtual environment
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate

    # Install dependencies including evaluation packages
    uv sync --dev --group eval

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
       "context": ["69796097"],
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

RAGAS Metrics Overview
^^^^^^^^^^^^^^^^^^^^^^^

The system uses four key RAGAS metrics for evaluation:

1. **Answer Relevancy**: Measures response alignment with user input using:

   .. math::

      \text{Answer Relevancy} = \frac{1}{N} \sum_{i=1}^{N} \frac{E_{g_i} \cdot E_o}{\|E_{g_i}\| \|E_o\|}

   Where E_g are embeddings of generated questions and E_o is the embedding of the original query and the metric is defined by the mean cosine similarity between LLM-generated questions and the original query ranging from -1 to 1 (though we expect values to be between 0 to 1).

2. **Faithfulness**: Measures factual consistency with retrieved context:

   .. math::

      \text{Faithfulness} = \frac{\text{Claims supported by context}}{\text{Total claims in response}}

   Uses LLM to generate a set of claims from the generated answer and cross-checks them with given context to determine if it can be inferred from the context.

3. **Context Recall**: Measures completeness of retrieved relevant documents (asks the question, did we retrieve all the contexts we needed?):

   .. math::

      \text{Context Recall} = \frac{\text{Claims in reference supported by context}}{\text{Total claims in reference}}

   LLM breaks down the reference answer into individual claims and classifies whether they can be attributed to the retrieved contexts. High recall means we found most of the needed information. Low recall means we missed important information.

4. **Context Precision**: Measures relevance of retrieved chunks (asks the question, of the contexts we retrieved, how many were actually relevant?)

   .. math::

      \text{Context Precision@K} = \frac{\sum_{k=1}^{K} (\text{Precision@k} \times v_k)}{\text{Relevant items in top K}}

   LLM computes a score based on the position and usefulness of each context and calculates weighted average. High precision means most retrieved contexts were useful. Low precision means we retrieved many irrelevant contexts.



Evaluation Workflow
^^^^^^^^^^^^^^^^^^^^

To run evaluations, follow these steps:

1. Export your OpenAI API key:

   .. code-block:: bash

      export OPENAI_API_KEY=your_key_here

2. Generate evaluation dataset:

   .. code-block:: bash

      # For Connex dataset
      ./eval/generate_connex_dataset.sh
      # OR for Ontario dataset
      ./eval/generate_on_dataset.sh

3. Evaluate retrieval accuracy:

   .. code-block:: bash

      python3 evaluate_topkacc.py dataset_connex.json --output connex_topkacc_results.json

4. Collect RAG outputs:

   .. code-block:: bash

      python3 eval/collect_rag_outputs.py --input eval/dataset_connex.json --output eval/rag_outputs.json --collection 211cx

5. Run RAGAS evaluation:

   .. code-block:: bash

      python eval/evaluate.py --input ./eval/rag_outputs.json --query-dataset eval/dataset_connex.json --output-dir ./eval

Performance Metrics
-------------------

RAGAS Metrics By Category - Ontario Data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

RAGAS Metrics By Category - Connex Data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
     - 0.88
     - 0.82
     - 0.75
     - 0.89
   * - Detail Level
     - Medium
     - 0.80
     - 0.59
     - 0.67
     - 0.64
   * - Detail Level
     - High
     - 0.87
     - 0.67
     - 0.73
     - 0.93
   * - Is Emergency
     - True
     - 0.81
     - 0.50
     - 0.60
     - 0.10
   * - Is Emergency
     - False
     - 0.84
     - 0.69
     - 0.72
     - 0.86
   * - Is Out of Scope
     - True
     - 0.59
     - -
     - -
     - -

Retrieval Performance - Ontario Data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

Retrieval Performance - Connex Data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1

   * - Metric
     - acc@5
     - acc@10
     - acc@15
     - acc@20
   * - Overall
     - 0.77
     - 0.82
     - 0.82
     - 0.84
   * - High Detail
     - 0.83
     - 0.89
     - 0.89
     - 0.89
   * - Low Detail
     - 0.75
     - 0.79
     - 0.79
     - 0.81
   * - Emergency
     - 0.45
     - 0.55
     - 0.60
     - 0.65
   * - Out of Scope
     - 0.60
     - 0.60
     - 0.60
     - 0.60

The metrics reveal several key insights:

1. **Improved Overall Performance**: The Connex dataset shows generally higher performance across most metrics compared to the Ontario dataset, particularly in detail handling and non-emergency cases.

2. **Emergency Detection**: Both datasets show distinct performance characteristics for emergency vs. non-emergency queries, with emergency queries generally showing lower performance metrics, indicating the system's conservative approach to emergency situations.

3. **Detail Level Impact**: High detail queries show strong performance in the Connex dataset, particularly in context precision (0.93) and retrieval accuracy (acc@20 = 0.89).

4. **Out-of-Scope Handling**: The system shows robust capability in identifying out-of-scope queries, with clear differentiation in metrics between in-scope and out-of-scope requests.

Based on these metrics, the system implements an optional re-ranking stage that can be enabled via the API's `rerank` parameter. When enabled:
    - First stage: Retrieves top 20 candidates using efficient embedding-based similarity
    - Second stage: Applies GPT-4 based semantic analysis to re-rank these candidates
    - Returns the top 5 most relevant services after re-ranking

To enable re-ranking in your API calls, simply set the `rerank` parameter to `true` in your request:

.. code-block:: json

    {
        "query": "I need mental health support",
        "latitude": 43.6532,
        "longitude": -79.3832,
        "radius": 5000,
        "rerank": true
    }
