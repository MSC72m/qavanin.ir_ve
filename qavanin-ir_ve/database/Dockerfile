# Stage 1: Build pgvector
FROM postgres:15 AS pgvector_builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    postgresql-server-dev-15 \
    && rm -rf /var/lib/apt/lists/*

# Install pgvector
RUN git clone https://github.com/pgvector/pgvector.git \
    && cd pgvector \
    && make \
    && make install

# Stage 2: Final image for PostgreSQL with pgvector
FROM postgres:15

# Set default environment variables (can be overridden at runtime)
ENV POSTGRES_DB=your_database_name
ENV POSTGRES_USER=your_username
ENV POSTGRES_PASSWORD=your_password

# Copy pgvector files from the builder stage
COPY --from=pgvector_builder /usr/lib/postgresql/15/lib/vector.so /usr/lib/postgresql/15/lib/
COPY --from=pgvector_builder /usr/share/postgresql/15/extension/vector* /usr/share/postgresql/15/extension/

# Add pgvector to shared_preload_libraries
RUN echo "shared_preload_libraries = 'vector'" >> /usr/share/postgresql/postgresql.conf.sample

# Create a script to initialize the database with only the necessary extensions
RUN mkdir -p /docker-entrypoint-initdb.d && \
    echo '#!/bin/bash\n\
set -e\n\
\n\
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL\n\
    CREATE EXTENSION IF NOT EXISTS vector;\n\
EOSQL' > /docker-entrypoint-initdb.d/init-pgvector.sh \
    && chmod +x /docker-entrypoint-initdb.d/init-pgvector.sh

# Expose PostgreSQL port
EXPOSE 5432

# Use PostgreSQL's default entrypoint
ENTRYPOINT ["docker-entrypoint.sh"]

# Start PostgreSQL
CMD ["postgres"]
