# Stage 1: Build
FROM node:18 AS build

# Create working directory
WORKDIR /app

# Copy package.json and package-lock.json files from chatbot-ui
COPY chatbot-ui/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the project files from chatbot-ui
COPY chatbot-ui/ ./

# Build the application for production
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

# Copy the built files to the nginx directory
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Default command to start nginx
CMD ["nginx", "-g", "daemon off;"]