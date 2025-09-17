# Use Python slim image
FROM python:3.12-slim

# Set metadata
LABEL maintainer="Guepard Team"
LABEL description="Guepard MCP Server - Real API implementation"
LABEL version="2.0.0"

# Set workdir
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy the MCP server
COPY main.py .
COPY src/ ./src/

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash guepard && \
    chown -R guepard:guepard /app
USER guepard

# Environment variables (can be overridden at runtime)
ENV ACCESS_TOKEN=""
ENV GUEPARD_API_URL="https://api.guepard.run"
ENV GUEPARD_AUTH_API="https://auth.guepard.run"
ENV SUPABASE_ANON_KEY=""
ENV POSTGRES16_PROFILE_ID="e54710e1-73dd-4628-a51d-93d1aab5226c"
ENV POSTGRES17_PROFILE_ID="b0a4e557-bb67-4463-b774-ad82c04ab087"

# Tool activation configuration
ARG GUEPARD_CONFIG=""
ENV GUEPARD_CONFIG=${GUEPARD_CONFIG}
ENV GUEPARD_ENABLED_MODULES=""
ENV GUEPARD_ENABLED_TOOLS=""
ENV GUEPARD_DISABLED_TOOLS=""
ENV GUEPARD_DISABLED_MODULES=""

# Default command to run MCP server
CMD ["python", "main.py"]
