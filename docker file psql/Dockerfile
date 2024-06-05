FROM postgres:latest

# Set environment variables for PostgreSQL
ENV POSTGRES_DB postgres
ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD 1234

# Copy the initialization script to the docker-entrypoint-initdb.d directory
COPY init.sql /docker-entrypoint-initdb.d/

