# Use the official Node.js image from the Docker Hub
FROM node:14

# Set the working directory
WORKDIR /app

# Copy the package.json and package-lock.json files
COPY package.json package-lock.json /app/

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . /app/

# Build the React application
RUN npm run build

# Expose the port the app runs on
EXPOSE 3000

# Run the application
CMD ["npm", "start"]