# Stage 1: Build the app
FROM node:slim AS build

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the files and build
COPY . .
RUN npm run build

# Stage 2: Serve the app with `serve`
FROM node:slim

WORKDIR /app

# Create a non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install serve globally
RUN npm install -g serve

# Copy only the built files from the previous stage
COPY --from=build /app/dist ./dist

# Change ownership of the dist directory
RUN chown -R appuser:appuser /app

EXPOSE 5002

# Switch to the non-root user
USER appuser

# Use serve to serve the static files
CMD ["serve", "-s", "dist", "-l", "5002"]
