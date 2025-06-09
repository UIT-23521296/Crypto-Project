FROM sagemath/sagemath:latest

# Đặt thư mục làm việc
WORKDIR /home/sage/app

# Cài đặt thư viện Python cần thiết (ví dụ pycryptodome)
RUN sage -pip install pycryptodome

# Copy toàn bộ mã nguồn trong thư mục server vào container
COPY server/ ./

# Mở port nếu server của bạn lắng nghe trên cổng nào đó (nếu cần)
# EXPOSE 2025

# Lệnh mặc định để chạy server.sage bằng Sage
CMD ["sage", "-python", "-u", "server.sage"]
