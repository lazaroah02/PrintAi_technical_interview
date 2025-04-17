FROM n8nio/n8n:latest

USER root

# Copiar archivos necesarios
COPY ./n8n_credentials.json /data/n8n_credentials.json
COPY ./n8n_workflow.json /data/n8n_workflow.json

# Aseguramos que el usuario node tenga acceso
RUN chown -R node:node /data

USER node
