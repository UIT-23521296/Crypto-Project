FROM sagemath/sagemath:latest

USER root

RUN apt-get update && apt-get install -y python3 python3-pip
RUN sage -pip install pycryptodome matplotlib

WORKDIR /app

COPY . /app

ENV PYTHONDONTWRITEBYTECODE=1

CMD ["sage", "-python"]