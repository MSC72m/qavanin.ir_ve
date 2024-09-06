# Stage 1: Build pgvector
FROM alpine as pgvector-builder

RUN apk add --no-cache \
    build-base \
    git \
    postgresql-dev \
    && rm -rf /var/cache/apk/*

RUN git clone https://github.com/pgvector/pgvector.git \
    && cd pgvector \
    && make \
    && mkdir -p /usr/local/lib/postgresql/extension \
    && cp vector.so /usr/local/lib/postgresql/extension/ \
    && cd .. \
    && rm -rf pgvector

# Stage 2: Build the application
FROM python:3.11-slim-buster as app-builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Stage 3: Final image
FROM postgres:15

ENV POSTGRES_DB=your_database_name
ENV POSTGRES_USER=your_username
ENV POSTGRES_PASSWORD=your_password

# Copy the pgvector library from the pgvector-builder stage
COPY --from=pgvector-builder /usr/local/lib/postgresql/extension/vector.so /usr/local/lib/postgresql/extension/

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

# Copy the application code from the app-builder stage
COPY --from=app-builder /app /app

# Install supervisord to manage both PostgreSQL and the API
RUN apk add --no-cache supervisor \
    && echo "[program:postgresql]\ncommand=/usr/local/bin/docker-entrypoint.sh postgres\nautostart=true\nautorestart=true\n\n[program:api]\ncommand=uvicorn api.main:app --host 0.0.0.0 --port 8000\ndirectory=/app\nautostart=true\nautorestart=true" > /etc/supervisor/conf.d/supervisord.conf

# Expose the API port
EXPOSE 8000

# Add a healthcheck for PostgreSQL
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD pg_isready --quiet --username "$POSTGRES_USER" --dbname "$POSTGRES_DB"

# Use supervisord as the entrypoint
ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
