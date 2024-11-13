

# Health Recommendation System

Welcome to the Health Recommendation System documentation! This system helps connect people with health and community services using AI-powered recommendations.

## 🌟 Overview

The Health Recommendation System is built with a modern microservices architecture:

| Component | Technology | Purpose |
|-----------|------------|----------|
| Frontend | Next.js | User interface |
| Backend | FastAPI | API services |
| Vector Database | ChromaDB | Service data storage |
| AI Engine | OpenAI | Embeddings & recommendations |

For API documentation, see the [API Reference](https://vectorinstitute.github.io/health-rec/api.html).

## 🚀 Getting started

### Prerequisites

Make sure you have these tools installed:

- Docker & Docker Compose (v20.10.0+)
- Python (3.11+)
- Node.js (18.0.0+)
- Poetry (1.4.0+)

### 🔑 API keys setup

Create a `.env.development` file in the project root:

```bash
# Required Keys
OPENAI_API_KEY=your_openai_key
211_API_KEY=your_211_key
DATA_DIR=/path/to/data
COLLECTION_NAME=your_collection_name

# Optional Frontend Keys
MAPBOX_API_KEY=your_mapbox_key
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your_google_maps_key
```

### 🛠️ Installation

1. **Clone and setup backend**
   ```bash
   # Clone repository
   git clone https://github.com/VectorInstitute/health-rec.git
   cd health-rec

   # Create virtual environment
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install dependencies
   poetry install --with test,docs
   ```

2. **Run pre-commit checks**

```bash
pre-commit run --all-files
```

### 🏃‍♂️ Running the services

**Backend only**

```bash
docker compose --env-file .env.development -f docker-compose.dev.yml up
```

**UI and Backend**

```bash
docker compose --env-file .env.development --profile frontend -f docker-compose.dev.yml up
```

### 📥 Data setup

For a detailed description of the data schema used for the recommendation engine, see [Data Schema](schema.rst).

#### Test data

If you want to test the system without real data, you can generate some dummy testing data:

```bash
python3 scripts/generate_test_data.py --output-dir <path_to_output_dir>
```

This would create a file `<path_to_output_dir>/test_data/data-00.json` with about 300 dummy services.
You can follow the next step to load this data and embeddings to ChromaDB.

#### Download service data

If you are using the 211 API or Empower's API, make sure you check with them to see if the API keys are
configured correctly for the geography of interest. The scripts fetch data from the respective APIs and
transforms them to be compatible with the [Data Schema](schema.rst).

**GTA data (211 API)**

```bash
python3 scripts/download_211_data.py --api-key $YOUR_211_API_KEY --dataset on --is-gta --data-dir <path_to_data_dir>
```

**Ontario-wide data (211 API)**

```bash
python3 scripts/download_211_data.py --api-key $YOUR_211_API_KEY --dataset on --data-dir <path_to_data_dir>
```

**Empower API data**

```bash
python3 scripts/download_empower_data.py --api-key $YOUR_EMPOWER_API_KEY --data-dir <path_to_data_dir>
```

#### Upload data and embeddings

First we use an interactive container:

```bash
docker run -it --network health-rec_app-network -v <path_to_data_dir_with_json_files>:/data -v `pwd`:/workspace -w /workspace vectorinstitute/health-rec:backend-dev-latest bash
```

Then we can run the following commands to upload the data to the vector database:

```bash
python3 health_rec/manage_data.py create --name <collection_name>
OPENAI_API_KEY=$YOUR_OPENAI_API_KEY python3 health_rec/manage_data.py load --name <collection_name> --data_dir /data --load_embeddings
python3 health_rec/manage_data.py list
```

Careful while loading embeddings, it uses the OpenAI API, and hence make sure the data you want to use is correct. Test with a small amount of data first.

#### Navigate to the UI on the browser

```bash
https://localhost:<frontend_port>
```

Note that the URL uses `https`, and hence in the browser you will get a warning about the insecure connection. You can ignore it and proceed.

#### In case, you wish to update frontend dependencies, run the following commands in the `ui` directory:

```bash
npm install <package_name>
```
