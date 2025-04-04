# Safety and Evaluation

## Overview

The Health Recommendation System employs a rigorous evaluation framework to ensure safe, accurate, and relevant service recommendations. This evaluation is critical for:

- Ensuring system safety when handling emergency situations
- Maintaining accuracy in service recommendations
- Identifying and filtering out-of-scope requests
- Validating the system's ability to handle queries with varying levels of detail
- Measuring retrieval accuracy of relevant services

## Installation for Evaluation

To run the evaluation pipeline, you'll need to install additional dependencies from the `eval` subgroup. From the project root:

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies including evaluation packages
uv sync --dev --group eval
```

## Evaluation Framework

### Synthetic Dataset Generation

The evaluation utilizes a synthetic dataset of 1000 queries, carefully structured to test different aspects of the system:

- **Regular Situations (80%)**: Divided equally among three levels of detail:

  - Low: 1-2 sentences, brief queries with minimal context
  - Medium: 2-3 sentences with moderate background information
  - High: Detailed paragraph with extensive context

- **Emergency Situations (10%)**: Queries indicating urgent medical or mental health needs

- **Out-of-Scope Situations (10%)**: Queries for services not covered by the system

Each query in the dataset includes:

```json
{
    "query": "User's query text",
    "context": ["service_id1", "service_id2"],
    "answer": "Expected answer text",
    "demographics": {
        "Age": "<string>",  // one of: child, teen, young adult, adult, senior
        "Gender": "<string>",  // one of: male, female, non-binary, N/A
        "Ethnicity": "<string>",  // one of: Caucasian, African, Asian, Hispanic, Indigenous, Other, N/A
        "Employment status": "<string>",  // one of: employed, unemployed, student, retired, unable to work, N/A
        "Housing situation": "<string>",  // one of: own home, renting, homeless, shelter, assisted living, N/A
        "Disability status": "<string>",  // one of: no disability, physical disability, cognitive disability, N/A
        "Immigration status": "<string>"  // one of: citizen, permanent resident, temporary resident, refugee, undocumented, N/A
    },
    "is_emergency": "<boolean>",  // true or false
    "is_out_of_scope": "<boolean>",  // true or false
    "detail_level": "<string>"  // one of: low, medium, high
}
```

### Example Scenarios

#### Regular Situation (Low Detail)

```json
{
   "query": "I'm looking for help with my child's eating disorder. What services are available?",
   "context": ["69796102"],
   "answer": "The North York General Hospital offers a Child and Adolescent Eating Disorders Program, which includes outpatient services for assessment, diagnosis, and treatment, as well as a day program with medical, nutritional, and mental health care support.",
   "demographics": {
     "Age": "child",
     "Gender": "N/A",
     "Ethnicity": "N/A",
     "Employment status": "N/A",
     "Housing situation": "N/A",
     "Disability status": "N/A",
     "Immigration status": "N/A"
   },
   "is_emergency": false,
   "is_out_of_scope": false,
   "detail_level": "low"
}
```

#### Emergency Situation

```json
{
   "query": "My child is experiencing severe abdominal pain and I am very concerned. What should I do?",
   "context": ["69796097"],
   "answer": "You should take your child to the nearest pediatric emergency department immediately. For urgent care, you can visit the Hospital for Sick Children, located at Elizabeth St. For further assistance, you can also go to North York General Hospital at 4001 Leslie St, first floor.",
   "demographics": {
     "Age": "child",
     "Gender": "N/A",
     "Ethnicity": "N/A",
     "Employment status": "N/A",
     "Housing situation": "N/A",
     "Disability status": "N/A",
     "Immigration status": "N/A"
   },
   "is_emergency": true,
   "is_out_of_scope": false,
   "detail_level": "medium"
}
```

### RAGAS Metrics Overview

The system uses four key RAGAS metrics for evaluation:

1. **Answer Relevancy**: Measures response alignment with user input using:

    $\text{Answer Relevancy} = \frac{1}{N} \sum_{i=1}^{N} \frac{E_{g_i} \cdot E_o}{\|E_{g_i}\| \|E_o\|}$

    Where E_g are embeddings of generated questions and E_o is the embedding of the original query and the metric is defined by the mean cosine similarity between LLM-generated questions and the original query ranging from -1 to 1 (though we expect values to be between 0 to 1).

2. **Faithfulness**: Measures factual consistency with retrieved context:

    $\text{Faithfulness} = \frac{\text{Claims supported by context}}{\text{Total claims in response}}$

    Uses LLM to generate a set of claims from the generated answer and cross-checks them with given context to determine if it can be inferred from the context.

3. **Context Recall**: Measures completeness of retrieved relevant documents (asks the question, did we retrieve all the contexts we needed?):

    $\text{Context Recall} = \frac{\text{Claims in reference supported by context}}{\text{Total claims in reference}}$

    LLM breaks down the reference answer into individual claims and classifies whether they can be attributed to the retrieved contexts. High recall means we found most of the needed information. Low recall means we missed important information.

4. **Context Precision**: Measures relevance of retrieved chunks (asks the question, of the contexts we retrieved, how many were actually relevant?)

    $\text{Context Precision@K} = \frac{\sum_{k=1}^{K} (\text{Precision@k} \times v_k)}{\text{Relevant items in top K}}$

    LLM computes a score based on the position and usefulness of each context and calculates weighted average. High precision means most retrieved contexts were useful. Low precision means we retrieved many irrelevant contexts.

### Evaluation Workflow

To run evaluations, follow these steps:

1. Export your OpenAI API key:

   ```bash
   export OPENAI_API_KEY=your_key_here
   ```

2. Generate evaluation dataset:

   ```bash
   # For Connex dataset
   ./eval/generate_connex_dataset.sh
   # OR for Ontario dataset
   ./eval/generate_on_dataset.sh
   ```

3. Evaluate retrieval accuracy:

   ```bash
   python3 evaluate_topkacc.py dataset_connex.json --output connex_topkacc_results.json
   ```

4. Collect RAG outputs:

   ```bash
   python3 eval/collect_rag_outputs.py --input eval/dataset_connex.json --output eval/rag_outputs.json --collection 211cx
   ```

5. Run RAGAS evaluation:

   ```bash
   python eval/evaluate.py --input ./eval/rag_outputs.json --query-dataset eval/dataset_connex.json --output-dir ./eval
   ```

## Performance Metrics

### RAGAS Metrics By Category - GTA Data

| Model | Category | Answer Relevancy | Faithfulness | Context Recall | Context Precision |
|-------|----------|------------------|--------------|----------------|-------------------|
| GPT-4o | Emergency | 0.801 | 0.920 | 0.485 | 0.107 |
| GPT-4o | Out of Scope | 0.717 | - | - | - |
| GPT-4o-mini | Emergency | 0.805 | 0.889 | 0.527 | 0.162 |
| GPT-4o-mini | Out of Scope | 0.721 | - | - | - |

| Subgroup | Category | Answer Relevancy | Faithfulness | Context Recall | Context Precision |
|----------|----------|------------------|--------------|----------------|-------------------|
| detail level | high | 0.82 | 0.68 | 0.72 | 0.89 |
| detail level | low | 0.85 | 0.76 | 0.70 | 0.86 |
| detail level | medium | 0.79 | 0.72 | 0.59 | 0.65 |

| Subgroup | Category | Answer Relevancy | Faithfulness | Context Recall | Context Precision |
|----------|----------|------------------|--------------|----------------|-------------------|
| detail level | high | 0.83 | 0.72 | 0.72 | 0.91 |
| detail level | low | 0.87 | 0.84 | 0.71 | 0.87 |
| detail level | medium | 0.81 | 0.76 | 0.62 | 0.67 |

### RAGAS Metrics By Category - Connex Data

| Model | Category | Answer Relevancy | Faithfulness | Context Recall | Context Precision |
|-------|----------|------------------|--------------|----------------|-------------------|
| GPT-4o | Emergency | 0.803 | 0.908 | 0.588 | 0.050 |
| GPT-4o | Out of Scope | 0.547 | - | - | - |
| GPT-4o-mini | Emergency | 0.809 | 0.929 | 0.580 | 0.150 |
| GPT-4o-mini | Out of Scope | 0.565 | - | - | - |

| Subgroup | Category | Answer Relevancy | Faithfulness | Context Recall | Context Precision |
|----------|----------|------------------|--------------|----------------|-------------------|
| detail level | high | 0.84 | 0.68 | 0.77 | 0.97 |
| detail level | low | 0.89 | 0.76 | 0.70 | 0.90 |
| detail level | medium | 0.79 | 0.68 | 0.67 | 0.65 |

| Subgroup | Category | Answer Relevancy | Faithfulness | Context Recall | Context Precision |
|----------|----------|------------------|--------------|----------------|-------------------|
| detail level | high | 0.89 | 0.69 | 0.80 | 0.98 |
| detail level | low | 0.91 | 0.81 | 0.72 | 0.91 |
| detail level | medium | 0.80 | 0.75 | 0.69 | 0.68 |

### Retrieval Performance - GTA Data

| Metric | acc@5 | acc@10 | acc@15 | acc@20 |
|--------|-------|--------|--------|--------|
| Overall | 0.57 | 0.63 | 0.66 | 0.68 |
| High Detail | 0.66 | 0.71 | 0.74 | 0.75 |
| Low Detail | 0.65 | 0.72 | 0.75 | 0.76 |
| Emergency | 0.55 | 0.63 | 0.66 | 0.69 |

### Retrieval Performance - Connex Data

| Metric | acc@5 | acc@10 | acc@15 | acc@20 |
|--------|-------|--------|--------|--------|
| Overall | 0.70 | 0.74 | 0.75 | 0.77 |
| High Detail | 0.83 | 0.89 | 0.89 | 0.89 |
| Low Detail | 0.75 | 0.79 | 0.79 | 0.81 |
| Emergency | 0.45 | 0.55 | 0.60 | 0.65 |

The metrics reveal several key insights:

1. **Dataset Performance Variation**: The Connex dataset shows higher performance in standard queries and detail handling, while the GTA dataset demonstrates more consistent performance across different query types. This suggests the need for dataset-specific optimization strategies.

2. **Emergency Response Challenges**: Both datasets show concerning performance metrics for emergency queries, particularly in context precision (0.050-0.162) and retrieval accuracy.

3. **Detail Level Impact**: High and low detail queries consistently outperform medium detail queries across both datasets. High detail queries in the Connex dataset achieve particularly strong context precision (0.97-0.98) and retrieval accuracy (acc@20 = 0.89), suggesting the system handles comprehensive queries more effectively than ambiguous ones.

4. **Out-of-Scope Detection Variance**: The system shows notably different capabilities in out-of-scope detection between datasets (GTA: 0.717-0.721 vs Connex: 0.547-0.565 answer relevancy), indicating a need for more consistent out-of-scope query handling across different data sources.

Based on these metrics, the system implements an optional re-ranking stage that can be enabled via the API's `rerank` parameter. When enabled:
    - First stage: Retrieves top 20 candidates using efficient embedding-based similarity
    - Second stage: Applies GPT-4 based semantic analysis to re-rank these candidates
    - Returns the top 5 most relevant services after re-ranking

To enable re-ranking in your API calls, simply set the `rerank` parameter to `true` in your request:

```json
{
    "query": "I need mental health support",
    "latitude": 43.6532,
    "longitude": -79.3832,
    "radius": 5000,
    "rerank": true
}
```
