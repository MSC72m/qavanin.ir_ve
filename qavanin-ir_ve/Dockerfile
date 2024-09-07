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

# Stage 2: Final image with Python and PostgreSQL
FROM python:3.12-slim AS python_base

# Install PostgreSQL dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set default environment variables for PostgreSQL
ENV POSTGRES_DB=your_database_name
ENV POSTGRES_USER=your_username
ENV POSTGRES_PASSWORD=your_password

# Copy pgvector files from the builder stage
COPY --from=pgvector_builder /usr/lib/postgresql/15/lib/vector.so /usr/lib/postgresql/15/lib/
COPY --from=pgvector_builder /usr/share/postgresql/15/extension/vector* /usr/share/postgresql/15/extension/

# Add pgvector to shared_preload_libraries
RUN echo "shared_preload_libraries = 'vector'" >> /usr/share/postgresql/postgresql.conf.sample

# Set the working directory
WORKDIR /app

# Expose the PostgreSQL and API ports
EXPOSE 5432 8000

# Create and activate virtual environment
RUN python3 -m venv /app/venv

# Ensure pip is installed in the virtual environment
RUN /app/venv/bin/python -m ensurepip --upgrade

# Upgrade pip and install required dependencies in the virtual environment
COPY requirements.txt /app/
RUN /app/venv/bin/pip install --upgrade pip && /app/venv/bin/pip install -r /app/requirements.txt

# Install python-dotenv in the virtual environment
RUN /app/venv/bin/pip install python-dotenv

# Set the environment path to use the virtual environment's Python
ENV PATH="/app/venv/bin:$PATH"

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
# Activate virtual environment\n\
source /app/venv/bin/activate\n\
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
