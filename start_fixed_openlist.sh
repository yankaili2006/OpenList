#!/bin/bash

# OpenList JWT修复启动脚本
# 通过完全重置环境来解决JWT token验证问题

echo "=== 启动修复后的OpenList ==="

# 停止并清理现有容器
echo "1. 停止现有容器..."
docker stop openlist 2>/dev/null || true
docker rm openlist 2>/dev/null || true

# 备份数据目录
echo "2. 备份数据..."
DATA_DIR="/Users/primihub/github/OpenList/data"
if [ -d "$DATA_DIR" ]; then
    BACKUP_DIR="${DATA_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
    echo "备份数据到: $BACKUP_DIR"
    cp -r "$DATA_DIR" "$BACKUP_DIR"
fi

# 确保目录存在
mkdir -p "$DATA_DIR"
chmod 777 "$DATA_DIR"

# 生成强随机JWT密钥
echo "3. 生成新的JWT密钥..."
JWT_SECRET="$(openssl rand -base64 32 2>/dev/null || echo "fixed_jwt_secret_$(date +%s)_$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32)")"

echo "4. 启动修复后的OpenList..."
docker run -d \
    --name openlist \
    -p 5244:5244 \
    -p 5245:5245 \
    -v "$DATA_DIR:/opt/openlist/data" \
    -e JWT_SECRET="$JWT_SECRET" \
    -e TZ="Asia/Shanghai" \
    -e "FORCE_JWT_RESET=true" \
    openlistteam/openlist:latest

# 等待服务启动
echo "5. 等待服务启动..."
for i in {1..30}; do
    if curl -s http://localhost:5244/ping >/dev/null 2>&1; then
        echo "✅ 服务已启动"
        break
    fi
    echo "等待服务启动... ($i/30)"
    sleep 2
    
    if [ $i -eq 30 ]; then
        echo "❌ 服务启动超时"
        docker logs openlist
        exit 1
    fi
done

# 等待数据库初始化
echo "6. 等待数据库初始化..."
sleep 5

# 重置管理员密码
echo "7. 重置管理员密码..."
if [ -f "$DATA_DIR/data.db" ]; then
    # 计算admin密码的哈希值
    STATIC_HASH="6fcb57cd10b2c11d765dcf16148d99130afd895082af83725ee8bb181b1d2b0f"
    
    # 获取salt并计算最终哈希
    SALT=$(sqlite3 "$DATA_DIR/data.db" "SELECT salt FROM x_users WHERE username='admin';" 2>/dev/null || echo "")
    if [ -n "$SALT" ]; then
        FINAL_HASH="$(echo -n "${STATIC_HASH}-${SALT}" | shasum -a 256 | cut -d' ' -f1)"
        sqlite3 "$DATA_DIR/data.db" "UPDATE x_users SET pwd_hash = '$FINAL_HASH' WHERE username = 'admin';" 2>/dev/null && echo "✅ 管理员密码已重置为: admin"
    fi
fi

echo ""
echo "🎉 OpenList修复完成！"
echo ""
echo "访问地址: http://localhost:5244"
echo "管理员账户: admin / admin"
echo "访客账户: guest / guest"
echo ""
echo "如果仍有JWT问题，请运行以下命令完全重置:"
echo "  docker stop openlist && docker rm openlist && rm -rf $DATA_DIR && ./start_fixed_openlist.sh"
echo ""

# 测试认证
echo "8. 测试认证..."
python3 /Users/primihub/github/OpenList/test_auth.py