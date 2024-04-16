# EVFHQ-Fetcher

EVFHQ-Fetcher is responsible for automatically gathering and storing metadata related to video files from various sources.

## DockerHub Repository

You can find the Docker image for EVFHQ-Fetcher on DockerHub: [anjieyang/evfhq-fetcher](https://hub.docker.com/repository/docker/anjieyang/evfhq-fetcher/general)

## Deployment Configurations

### Local Build Deployment with Docker Compose

For deploying EVFHQ-Fetcher using Docker Compose and building the Docker image locally, you can use the provided `docker-compose.yml` file in the root directory of this repository.

### DockerHub Deployment

If you prefer a quick and straightforward deployment using the Docker image from DockerHub.

1. Download the `dockerhub_deploy.yml` file from the `dockerhub_deploy` folder.

2. Replace the placeholder values (`your_db_host`, `your_db_name`, `your_db_user`, `your_db_password`, `your_db_port`, `your_api_key`, `your_search_query`, `your_number_of_videos`) with your actual configurations.

3. Run the following command to start the EVFHQ-Fetcher service:

```bash
docker-compose -f dockerhub_deploy.yml up -d
```
