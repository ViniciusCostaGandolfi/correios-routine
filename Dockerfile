# Use the official Miniconda3 image as the base image
FROM continuumio/miniconda3:latest

# Set the working directory in the container
WORKDIR /app

# Copy the environment.yaml file into the container
COPY environment.yaml .

# Create a Conda environment named "correios-routine" based on the environment.yaml file
RUN conda env create -n correios-routine -f environment.yaml

# Activate the Conda environment
SHELL ["/bin/bash", "-c"]

# Install additional dependencies if needed
# RUN conda install -c conda-forge <package_name>

# Copy the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Activate the Conda environment and run the FastAPI server using uvicorn
CMD ["/bin/bash", "-c", "source activate correios-routine && python3 dashboards/v1/vrp_dash_app.py"]