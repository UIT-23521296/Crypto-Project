FROM sagemath/sagemath:latest

USER root

RUN apt-get update && \
    apt-get install -y socat python3-pip && \
    sage --pip install pycryptodome

COPY server1.sage .
COPY file_test.jpg .

VOLUME [ "/output" ]

EXPOSE 8888

ENTRYPOINT ["socat", "TCP-LISTEN:8888,fork,reuseaddr", "EXEC:'sage server1.sage',stderr"]