FROM sagemath/sagemath:latest

WORKDIR /app

# Cài thư viện cần thiết cho server và attack
RUN sage -pip install flask pycryptodome requests tqdm

# Copy toàn bộ mã nguồn vào container
COPY . .

# Mặc định chạy server, có thể override khi chạy container
CMD ["sage", "server.py"]