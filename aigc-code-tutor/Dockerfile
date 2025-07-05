# 使用 Python 官方镜像（基础环境）
FROM python:3.10-slim

# 设置容器内的工作目录（相当于cd /app）
WORKDIR /app

# 将当前目录所有文件复制到容器的/app目录
COPY . .

# 安装Flask依赖（用pip）
RUN pip install flask

# 容器启动时运行的命令
CMD ["python", "backend/app.py"]