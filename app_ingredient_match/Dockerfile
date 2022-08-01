# Dockerfile to build the container with the server for ingredient match

# Used Python 3.8 for development
FROM python:3.8

# code directory will contain all files
WORKDIR /code

# Copy requirements file
COPY ./requirements.txt /code/requirements.txt

# Install package requirements
RUN pip install --no-cache-dir -r /code/requirements.txt

# Copy all required files
COPY . /code/

# Load required Python modules (downloads from sentence-transformer library)
RUN python ./src/config_env.py

# Activate server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]