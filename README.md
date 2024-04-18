# EVFHQ-Fetcher

EVFHQ-Fetcher is responsible for automatically gathering and storing metadata related to video files from various sources.

## DockerHub Repository

You can find the [Docker image](https://hub.docker.com/repository/docker/anjieyang/evfhq-fetcher/general) for EVFHQ-Fetcher on DockerHub.

## Deployment Configurations

### Local Build Deployment with Docker Compose

For deploying EVFHQ-Fetcher using Docker Compose and building the Docker image locally, you can use the provided `docker-compose.yml` file.

### DockerHub Deployment

If you prefer a quick and straightforward deployment using the Docker image from DockerHub.

1. Download [evfhq-fetcher-deploy.yml](https://drive.google.com/uc?export=download&id=1-GZPdvvrCp6mchBnhhnq6-rRr0VpD7qr).

2. Replace the placeholder values (`your_db_host`, `your_db_name`, `your_db_user`, `your_db_password`, `your_db_port`, `your_api_key`, `your_search_query`, `your_number_of_videos`) with your actual configurations.

3. Run the following command to start the EVFHQ-Fetcher service:

```bash
docker-compose -f evfhq-fetcher-deploy.yml up -d
```
