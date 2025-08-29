# Use Python slim image
FROM python:3.12-slim

# Set workdir
WORKDIR /app

# Copy MCP server code
COPY . /app

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable (replace with your token or use runtime ENV)
ENV ACCESS_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZjg0NDBhOC1kNTk0LTQ3ODgtODJhMi03YjYzNDM4ZWE3NmQiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJzY29wZXMiOlsiYWRtaW4iXSwiZXhwIjoxNzc2MzY4OTY3LCJ0b2tlbl9pZCI6IjFhOWE4ZWJlLTdmMjQtNDRjZS1hNmJhLWQwZTUyOWM4YTRjOCIsImlhdCI6MTc1MDA3OTc0N30.oF0OKm-DSsGgI5k8BQWNkkOFFiOY-KCwcQo31lxEd3I


# Default command to run StdIO MCP server
CMD ["python", "guepard-mcp.py", "--transport", "stdio"]