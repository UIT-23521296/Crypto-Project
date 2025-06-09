FROM sagemath/sagemath:latest

# Switch to root user for installation
USER root

# Install Python3 and required packages
RUN apt-get update && apt-get install -y python3 python3-pip
RUN sage -pip install pycryptodome matplotlib

# Copy all necessary files
COPY *.py .
COPY test.jpg .
# Set working directory
WORKDIR /home/sage

# Switch back to sage user
USER sage

# Default command (will be overridden by docker-compose)
CMD ["sage", "-python", "server.py"]
# docker run -v "$(pwd):/home/sage" sagemath/sagemath:latest sage find_invalid_curve.py