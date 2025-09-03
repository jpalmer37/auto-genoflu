# Use an official Python runtime as a parent image
FROM condaforge/miniforge3:latest

# Set the working directory in the container
WORKDIR /app

# 2. Copy ONLY the dependency definition files first
COPY environment.yml ./

RUN mamba env create -f environment.yml && \
    mamba clean -afy

RUN mkdir -p /home/ubuntu/genoflu/{rename,outputs,logs} && mkdir -p /data

COPY . .

# Set the default command to run your application
ENTRYPOINT ["mamba", "run", "-n", "auto-genoflu", "auto_genoflu"]

# Optional: Provide a default config file
CMD ["-c", "/app/aws-config.json", "--log-level", "DEBUG"]