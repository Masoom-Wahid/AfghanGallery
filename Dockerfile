# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirments.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirments.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Collect static files (optional)
# RUN python manage.py collectstatic --noinput

# Default command (now handled in docker-compose)
CMD ["python", "manage.py","runserver", "0.0.0.0:3020"]
