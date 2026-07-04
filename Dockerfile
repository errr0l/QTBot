# --- 第一阶段：构建与安装依赖 ---
FROM docker.1ms.run/library/python:3.9-slim AS builder
WORKDIR /build
COPY requirements.txt .

# 设置清华源并一键安装所有精确版本的依赖
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --no-cache-dir --disable-pip-version-check --user -r requirements.txt && \
    # ⚡️ 精准清理：仅卸载包管理器及其残留，绝对不碰业务 bin 目录
    pip uninstall -y pip setuptools wheel && \
    find /root/.local/lib/python3.9/site-packages -maxdepth 1 \
      \( -name "pip*" -o -name "setuptools*" -o -name "wheel*" \) \
      -exec rm -rf {} + && \
    # 清理可能存在的临时编译缓存
    rm -rf /root/.cache

# --- 第二阶段：最终运行环境 ---
FROM docker.1ms.run/library/python:3.9-slim
WORKDIR /app

# 将第一阶段安装的包直接拷贝过来
COPY --from=builder /root/.local /root/.local

# 复制您的业务代码
COPY . .

# 确保 nb-cli 命令可用
ENV PATH=/root/.local/bin:$PATH

EXPOSE 8080
CMD ["python", "bot.py"]