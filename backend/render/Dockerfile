# VibePoster Render - Node.js/Express Backend
# ============================================

FROM node:20-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（sharp 需要 libvips）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libvips-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制应用代码
COPY src/ ./src/

# 暴露端口
EXPOSE 3000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

# 启动命令
CMD ["node", "src/server.js"]

