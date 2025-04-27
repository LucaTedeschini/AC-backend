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
# Default to development, but allow override at runtime
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1

# Create startup scripts for different environments
COPY --chmod=755 <<-"EOF" /start-dev.sh
#!/bin/sh
flask run --host=0.0.0.0 --debug
EOF

COPY --chmod=755 <<-"EOF" /start-prod.sh
#!/bin/sh
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 app:app
EOF

# Select appropriate startup script based on environment
CMD ["/bin/sh", "-c", "if [ \"$FLASK_ENV\" = \"production\" ]; then /start-prod.sh; else /start-dev.sh; fi"]