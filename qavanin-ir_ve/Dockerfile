# Start from the official PostgreSQL image
FROM postgres:15

# Set default environment variables (can be overridden at runtime)
ENV POSTGRES_DB=your_database_name
ENV POSTGRES_USER=your_username
ENV POSTGRES_PASSWORD=your_password

# Install build dependencies and other necessary packages
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    postgresql-server-dev-15 \
    python3-pip \
    python3-dev \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install pgvector
RUN git clone https://github.com/pgvector/pgvector.git \
    && cd pgvector \
    && make \
    && make install \
    && cd .. \
    && rm -rf pgvector

# Add pgvector to shared_preload_libraries
RUN echo "shared_preload_libraries = 'vector'" >> /usr/share/postgresql/postgresql.conf.sample

# Create a script to initialize the database with only the necessary extensions
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL\n\
    CREATE EXTENSION IF NOT EXISTS vector;\n\
EOSQL' > /docker-entrypoint-initdb.d/init-pgvector.sh \
    && chmod +x /docker-entrypoint-initdb.d/init-pgvector.sh

# Set the working directory
WORKDIR /app

# Copy the application code into the container
COPY . /app

# Install Python dependencies for the API
RUN pip3 install --no-cache-dir -r requirements.txt --break-system-packages

# Expose the PostgreSQL port and the API port
EXPOSE 5432 8000

# Add a healthcheck for PostgreSQL
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB} || exit 1

# Create a start script to run both PostgreSQL and the API
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Start PostgreSQL\n\
docker-entrypoint.sh postgres &\n\
\n\
# Wait for PostgreSQL to be ready\n\
until pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}; do\n\
  echo "Waiting for PostgreSQL to be ready..."\n\
  sleep 2\n\
done\n\
\n\
# Run database initialization\n\
python3 database/models.py\n\
\n\
# Start the API\n\
uvicorn api.main:app --host 0.0.0.0 --port 8000\n\
' > /app/start.sh \
    && chmod +x /app/start.sh

# Use the start script as the entrypoint
ENTRYPOINT ["/app/start.sh"]