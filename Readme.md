# PrintAi Technical Project

## Description
PrintAi Technical Project

## Features
- Hacker News Scraping
- Books Scraping
- API to serve books and news
- n8n workflow and AI Agent
- Chatbot to interact wiht the AI Agent 

## Installation
3. Build and run the Docker container:
   ```bash
   docker-compose up --build
   ```

## Usage
1. Ensure the Docker container is running:
   ```bash
   docker-compose up

**Notes**
- Workflows and credentials for n8n are automatic loaded
- Books scraping starts automatically and may take some time to finish.
- n8n interface accessible from : `http://localhost:5678`
- API Accessible from: `http://localhost:5000`

3. Access the chatbot interface in your browser at http://localhost:3000.

## Tests
**Tests runs automatically on docker container starts.**

In case of desire of manually run the tests:

With container runnin:
- Backend tests
```bash
 docker exec -it source_code-api-1 pytest app/tests
```




