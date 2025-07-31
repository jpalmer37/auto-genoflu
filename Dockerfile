# Use an official Python runtime as a parent image
FROM condaforge/miniforge3:latest

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any necessary build tools and dependencies
RUN mamba env create -f environment.yml

# Set the default command to run your application
ENTRYPOINT ["mamba", "run", "-n", "auto-genoflu", "auto_genoflu"]

# Optional: Provide a default config file
CMD ["-c", "/data/config.json"]