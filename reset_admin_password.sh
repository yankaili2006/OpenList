#!/bin/bash

# OpenList 管理员密码重置脚本
# 使用方法: ./reset_admin_password.sh [新密码]

DATA_DIR="/Users/primihub/github/OpenList/data"
DB_FILE="$DATA_DIR/data.db"

# 检查数据库文件是否存在
if [ ! -f "$DB_FILE" ]; then
    echo "错误: 数据库文件不存在: $DB_FILE"
    exit 1
fi

# 设置新密码，默认为 'admin'
NEW_PASSWORD="${1:-admin}"

# 计算密码哈希
echo "正在重置管理员密码为: $NEW_PASSWORD"

# 计算 StaticHash
STATIC_HASH=$(echo -n "${NEW_PASSWORD}-https://github.com/alist-org/alist" | shasum -a 256 | cut -d' ' -f1)
echo "Static Hash: $STATIC_HASH"

# 获取当前盐值
SALT=$(sqlite3 "$DB_FILE" "SELECT salt FROM x_users WHERE username='admin';")
echo "Salt: $SALT"

# 计算最终哈希
FINAL_HASH=$(echo -n "${STATIC_HASH}-${SALT}" | shasum -a 256 | cut -d' ' -f1)
echo "Final Hash: $FINAL_HASH"

# 更新数据库
sqlite3 "$DB_FILE" "UPDATE x_users SET pwd_hash = '$FINAL_HASH' WHERE username = 'admin';"

# 验证更新
echo "密码已重置，验证用户信息:"
sqlite3 "$DB_FILE" "SELECT username, pwd_hash, salt FROM x_users WHERE username='admin';"

echo ""
echo "✅ 管理员密码已成功重置为: $NEW_PASSWORD"
echo "请重启OpenList容器使更改生效:"
echo "docker restart openlist"