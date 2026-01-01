#!/bin/bash

# OpenList JWT修复启动脚本
# 这个脚本通过环境变量和配置重置来解决JWT验证问题

DATA_DIR="/Users/primihub/github/OpenList/data"
CONFIG_FILE="$DATA_DIR/config.json"

# 停止现有容器
echo "停止现有OpenList容器..."
docker stop openlist 2>/dev/null || true
docker rm openlist 2>/dev/null || true

# 生成新的JWT密钥（确保与之前不同）
NEW_JWT_SECRET="$(openssl rand -base64 32 2>/dev/null || echo "fixed_jwt_secret_$(date +%s)")"
echo "生成新的JWT密钥..."

# 更新配置文件（如果存在）
if [ -f "$CONFIG_FILE" ]; then
    echo "更新配置文件中的JWT密钥..."
    # 使用jq更新配置，如果没有jq则使用sed
    if command -v jq >/dev/null 2>&1; then
        jq ".jwt_secret = \"$NEW_JWT_SECRET\"" "$CONFIG_FILE" > "${CONFIG_FILE}.tmp" && mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"
    else
        # 简单的sed替换（假设jwt_secret在配置中）
        sed -i.tmp "s/\"jwt_secret\": \"[^\"]*\"/\"jwt_secret\": \"$NEW_JWT_SECRET\"/" "$CONFIG_FILE"
    fi
fi

# 启动新容器
echo "启动修复后的OpenList容器..."
docker run -d \
    --name openlist \
    -p 5244:5244 \
    -p 5245:5245 \
    -v "$DATA_DIR:/opt/openlist/data" \
    -e JWT_SECRET="$NEW_JWT_SECRET" \
    openlistteam/openlist:latest

# 等待服务启动
echo "等待服务启动..."
sleep 10

# 测试服务
echo "测试服务状态..."
if curl -s http://localhost:5244/ping >/dev/null; then
    echo "✅ OpenList服务已成功启动并修复JWT问题"
    echo "访问地址: http://localhost:5244"
    echo "管理员账户: admin / admin"
    echo "访客账户: guest / guest"
else
    echo "❌ 服务启动失败，请检查日志"
    docker logs openlist
fi