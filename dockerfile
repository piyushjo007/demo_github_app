# NOTE : Multi-stage Dockerfile to optimize the image size and build time. 
#The first stage will be used to install the dependencies and run the unit tests,
# while the second stage will be used to copy only the necessary files and run the app.
# Unit test before image build to ensure that the app is working correctly before building the final image. This will help catch any issues early on and prevent building a broken image.

# used base image with Python 3.11-slim as the app does not have much functionality and does not require a full Python image. The slim version is smaller in size and will help reduce the overall image size.
FROM python:3.11-slim as build

# Create a non-root user to run the app for better security.
RUN useradd -m appuser
#switch to the appuser to avoid running the app as root.
WORKDIR /app


COPY requirements.txt .
# Install the dependencies from the requirements.txt file. The --no-cache-dir option is used to prevent pip from caching the installed packages, which can help reduce the image size.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app code to the /app directory in the container. This will include the main.py file and the tests directory.
COPY . .

# Change the ownership of the /app directory to the appuser and switch to that user. This will ensure that the app runs with non-root privileges.
RUN chown -R appuser:appuser /app

# switch to the non-root user
USER appuser

# RUN pytest tests/ # this fails somehow . used PYTHONPATH=. pytest -v instead to run the tests in the build stage to ensure that the app is working correctly before building the final image.
RUN PYTHONPATH=. pytest -v
# Stage 2: main image build with the app and its dependencies

# Start with a fresh base image to keep the final image size small.
FROM python:3.11-slim

# Create a non-root user to run the app for better security.
RUN useradd -m appuser
WORKDIR /app

COPY requirements-prod.txt .
# Install the dependencies from the requirements.txt file. The --no-cache-dir option is used to prevent pip from caching the installed packages, which can help reduce the image size.
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy only the necessary files from the build stage to the final image. 
#This will include the main.py file and any other files required to run the app, but will exclude the tests and any unnecessary files that were used during the build stage.
COPY --from=build /app/main.py .

RUN chown -R appuser:appuser /app
USER appuser

# Expose the port that the app will run on (8080 in this case) this was a requirement from mock interview question prespective.
EXPOSE 8080

# Set the command to run the app when the container starts.
ENTRYPOINT [ "python3" ]
CMD [ "main.py"]
