FROM python:3.13-alpine

WORKDIR /app

COPY requirements.txt .

# Install build dependencies for Python packages that might require compilation
RUN apk add --no-cache --virtual .build-deps gcc musl-dev

RUN pip install --no-cache-dir -r requirements.txt

# Remove build dependencies
RUN apk del .build-deps

COPY . .

# Make port 5000 available
EXPOSE 5000

# Define environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1

CMD ["flask", "run", "--host=0.0.0.0"]