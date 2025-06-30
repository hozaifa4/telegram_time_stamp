# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variables (optional, can be set in Railway)
# ENV NAME World

# Run app.py when the container launches using gunicorn
CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0:5000", "app:app"]
