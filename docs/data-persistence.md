# Data Persistence

## Issue
ChromaDB collections are lost when containers restart or when running `docker system prune`.

## Solution

### Current Setup
The Docker configuration uses named volumes for persistence:
- Development: `chroma_data_dev`
- Production: `chroma_data`

### Prevent Data Loss

**Option 1: Selective Pruning (Recommended)**
```bash
# Safe cleanup - preserves volumes
docker system prune --volumes=false

# Or clean individually
docker container prune
docker image prune
docker network prune
```

**Option 2: Volume Backups**
```bash
# Check volume status
docker volume ls | grep chroma

# Backup before cleanup
docker run --rm -v health-rec_chroma_data_dev:/source -v $(pwd)/backups:/backup alpine tar czf /backup/chroma_backup_$(date +%Y%m%d).tar.gz -C /source .
```

### Restore Data
```bash
# Restore from backup
docker run --rm -v health-rec_chroma_data_dev:/target -v $(pwd)/backups:/backup alpine tar xzf /backup/chroma_backup_YYYYMMDD.tar.gz -C /target
```

### Alternative: Bind Mounts for Development
For guaranteed persistence during development, uncomment the bind mount in `docker-compose.dev.yml`:

```yaml
chromadb-dev:
  volumes:
    # - chroma_data_dev:/chroma/chroma        # Named volume
    - ./data/chroma_dev:/chroma/chroma        # Bind mount (uncomment this)
```

## Quick Commands

```bash
# Safe restart with data preservation
docker compose --env-file .env.development -f docker-compose.dev.yml down
docker compose --env-file .env.development --profile frontend -f docker-compose.dev.yml up

# Check if data exists
docker exec $(docker compose --env-file .env.development -f docker-compose.dev.yml ps -q chromadb-dev) ls -la /chroma/chroma
```

!!! tip "Best Practice"
    Never use `docker system prune` without the `--volumes=false` flag to preserve your data.
