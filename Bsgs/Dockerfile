FROM sagemath/sagemath:latest

# Đặt thư mục làm việc
WORKDIR /home/sage/app

# Cài đặt thư viện Python 
RUN sage -pip install pycryptodome

# Copy toàn bộ mã nguồn trong thư mục server vào container
COPY server/ ./

# Lệnh mặc định để chạy server.py bằng Sage
CMD ["sage", "-python", "-u", "server.py"]
