# 使用官方Python镜像作为基础镜像
FROM python:3.11

# 设置工作目录
WORKDIR /app

# 复制当前目录内容到容器中的工作目录
COPY . /app

# 安装所需的Python包
RUN pip install --no-cache-dir -r requirements.txt

# # 暴露应用运行的端口
# EXPOSE 8080

# # 定义环境变量
# ENV PORT 8080

# 启动应用
CMD ["python", "main.py"]