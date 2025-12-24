FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

# Start Locust without headless mode
CMD ["locust", "-f", "locustfile.py", "--host", "$TARGET_URL"]
