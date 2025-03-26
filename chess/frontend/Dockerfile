FROM node:16-alpine as build

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Copy SSL certificates for build
COPY ../cert.pem ./cert.pem
COPY ../key.pem ./key.pem

# Build the application
RUN npm run build

# Production stage
FROM nginx:1.21-alpine

# Create SSL directory
RUN mkdir -p /etc/nginx/ssl/

# Copy SSL certificates
COPY cert.pem /etc/nginx/ssl/cert.pem
COPY key.pem /etc/nginx/ssl/key.pem

# Copy built assets from the build stage
COPY --from=build /app/build /usr/share/nginx/html

# Add custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose ports
EXPOSE 80
EXPOSE 443

# Start nginx
CMD ["nginx", "-g", "daemon off;"]