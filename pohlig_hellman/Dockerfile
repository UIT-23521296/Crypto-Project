FROM sagemath/sagemath:latest

# Tạo thư mục làm việc
WORKDIR /app

# Sao chép toàn bộ nội dung vào container
COPY . .

# Cài Flask cho server
RUN sage -pip install flask pycryptodome

CMD ["sage", "-python", "-u", "server/server.py"]