# python:3.9-slim 会自动适配当前构建的目标架构
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

EXPOSE 8080

CMD ["nb", "run"]