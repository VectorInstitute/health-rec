# health-rec

## Overview

Welcome to the health-rec project! This project is designed to develop a recommendation system for health and community services.

The project is built using a microservices architecture. It has the following components:

- Next.js frontend
- FastAPI backend
- Chroma vector database
- OpenAI for embedding and recommendation


## Development

### Prerequisites

- Docker
- Docker Compose
- Node.js
- Python
- pip
- npm

### Setup

#### Clone the repository

#### Add API keys

In the `.env.development` file in the root of the project, set the following environment variables:
  - `OPENAI_API_KEY`
  - `211_API_KEY`
  - `MAPBOX_API_KEY`
  - `DATA_DIR`
  - `COLLECTION_NAME`

Make sure to set appropriate values for these variables. The `CHROMA_HOST`, `CHROMA_PORT`, and `COLLECTION_NAME`
are already defined in the file, but you may need to adjust their values if necessary.

#### Install dependencies in a virtual environment for the backend

```bash
cd health_rec
python3 -m venv .venv
source .venv/bin/activate
poetry install --with test
```

Now you can run pre-commit checks and tests:

```bash
pre-commit run --all-files
```

#### Run the services

For development, we use docker compose to run the services.

To run only the backend and chroma db services, run the following command:

```bash
docker compose --env-file .env.development -f docker-compose.dev.yml up
```

To run the frontend and backend, run the following command:

```bash
docker compose --env-file .env.development --profile frontend -f docker-compose.dev.yml up
```

#### Download data

For example, to download GTA data, run the following command:

```bash
python scripts/download_data.py --api-key $YOUR_211_API_KEY --dataset on --is-gta --data-dir /mnt/data/211
```

To download Ontario-wide data, run the following command:

```bash
python scripts/download_data.py --api-key $YOUR_211_API_KEY --dataset on --data-dir /mnt/data/211
```

#### Upload data and embeddings

First we use an interactive container:

```bash
docker run -it --network health-rec_app-network -v <data_dir_with_json_files>:/data -v `pwd`:/workspace -w /workspace vectorinstitute/health-rec:backend-dev-latest bash
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
http://localhost:<frontend_port>
```

#### In case, you wish to update frontend dependencies, run the following commands in the `ui` directory:

```bash
npm install <package_name>
```
