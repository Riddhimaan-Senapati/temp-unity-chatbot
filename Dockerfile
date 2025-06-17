# Use an official Python runtime as a parent image
FROM python:3.13-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any dependencies
# The --no-cache-dir option prevents caching of the packages, which helps reduce the size of the Docker image.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit app files into the container
COPY . .

# Expose the port that Streamlit runs on (default 8501)
EXPOSE 8501

# Command to run the Streamlit app
# "--server.port=8501" makes sure this listens on the correct port (8501) inside the container.
# "--server.address=0.0.0.0" makes sure that this listens on an address (0.0.0.0) that makes it accessible from outside the container through Docker's port mapping.
CMD ["streamlit", "run", "chatbot.py", "--server.port=8501", "--server.address=0.0.0.0"]