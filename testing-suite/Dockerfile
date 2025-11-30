# Dockerfile for testing suite
FROM node:18-alpine

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    python3-dev \
    py3-pip \
    chromium \
    chromium-chromedriver \
    postgresql-client \
    mysql-client \
    git \
    curl \
    bash

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY requirements.txt ./

# Install Node.js dependencies
RUN npm ci

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Create directories for test results
RUN mkdir -p results/coverage results/reports results/logs

# Copy application code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001
RUN chown -R nodejs:nodejs /app
USER nodejs

# Expose ports for test services
EXPOSE 3000 5432 3306 27017 6379

# Default command
CMD ["npm", "test"]