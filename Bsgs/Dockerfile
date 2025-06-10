FROM sagemath/sagemath:latest

# Switch to root để cài đặt gói hệ thống nếu cần
USER root

# (Tuỳ chọn) Cập nhật hệ thống — tránh lỗi gói nếu cần
RUN apt-get update

# Cài đặt thư viện Python thông qua pip của Sage
RUN sage -pip install pycryptodome

# Tạo thư mục làm việc
WORKDIR /home/sage/app

# Copy mã nguồn server vào thư mục làm việc
COPY server/ .

# Chuyển lại user 'sage' (SageMath yêu cầu chạy bằng user này)
USER sage

# Chạy script server.py bằng Sage
CMD ["sage", "-python", "-u", "server.py"]
