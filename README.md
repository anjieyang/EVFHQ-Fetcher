# EVFHQ-Fetcher

EVFHQ-Fetcher is responsible for automatically gathering and storing metadata related to video files from various sources.

## DockerHub Repository

You can find the Docker image for EVFHQ-Fetcher on DockerHub: [anjieyang/evfhq-fetcher](https://hub.docker.com/repository/docker/anjieyang/evfhq-fetcher/general)

## Quick Start with Docker Compose

To quickly deploy EVFHQ-Fetcher using Docker Compose, you can use the provided `simple_deploy.yml` file.

1. Download the `simple_deploy.yml` file provided.

2. Replace the placeholder values (`your_db_host`, `your_db_name`, `your_db_user`, `your_db_password`, `your_db_port`, `your_api_key`, `your_search_query`, `your_number_of_videos`) with your actual configurations.

3. Run the following command to start the EVFHQ-Fetcher service:

```bash
docker-compose -f simple_deploy.yml up -d
```
