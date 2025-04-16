# Etapa 1: Construcción
FROM node:18 AS build

# Crear directorio de trabajo
WORKDIR /app

# Copiar los archivos de package.json y package-lock.json desde chatbot-ui
COPY chatbot-ui/package*.json ./

# Instalar dependencias
RUN npm install

# Copiar el resto de los archivos del proyecto desde chatbot-ui
COPY chatbot-ui/ ./

# Construir la aplicación para producción
RUN npm run build

# Etapa 2: Servir con nginx
FROM nginx:alpine

# Copiar los archivos construidos al directorio de nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Exponer el puerto 80
EXPOSE 80

# Comando por defecto para iniciar nginx
CMD ["nginx", "-g", "daemon off;"]