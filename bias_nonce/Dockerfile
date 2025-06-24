# Dockerfile
FROM sagemath/sagemath:latest

WORKDIR /app

RUN sage -pip install flask ecdsa

COPY server/server.py .

CMD ["sage", "-python", "-u", "server.py"]
