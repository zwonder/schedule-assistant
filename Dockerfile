FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# 复制项目文件
COPY . .

# 创建数据目录（持久化路径）
RUN mkdir -p /app/data

# 暴露端口
EXPOSE 8080

# 设置端口环境变量
ENV PORT=8080

# 启动命令
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8080", "--timeout", "120", "app:app"]
