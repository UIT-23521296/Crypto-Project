FROM sagemath/sagemath:latest

USER root

RUN apt-get update && \
    apt-get install -y python3-pip && \
    sage -python -m pip install pycryptodome pwntools

COPY attack1.py .

CMD ["sage", "-python", "attack1.py"]