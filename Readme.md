# PrintAi Technical Project

## Description
PrintAi Technical Project

## Features
- Hacker News Scraping
- Books Scraping
- API to serve books and news
- n8n workflow and AI Agent
- Chatbot to interact wiht the AI Agent 

## Configuration
1. Add required .env files
/backend/.env
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

/workflows/.env
N8N_RUNNERS_ENABLED=true

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

2. Access the n8n interface at: `http://localhost:5678` and **activate** the workflow.(Will be automatically activated soon)
   ```
3. Access the chatbot interface in your browser at `http://localhost:3000`.

API Accessible by http://localhost:5000



