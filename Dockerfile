# Use the official Python 3.12 image
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files from the current directory to the working directory in the container
COPY . /app

# Expose the port the app runs on
EXPOSE 5001

# Define environment variables
ENV FLASK_APP=main.py
ENV FLASK_ENV=production

# Run the Flask application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]
