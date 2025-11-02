# Use a lightweight Python base image
FROM python:3.14-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port your Flask app will run on
EXPOSE 5000

# Command to run the Flask application
CMD gunicorn --bind 0.0.0.0:5000 wsgi:app
