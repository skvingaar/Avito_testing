FROM mcr.microsoft.com/playwright/python:v1.62.0-noble

WORKDIR /tests

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "pytest", "--browser", "chromium"]
