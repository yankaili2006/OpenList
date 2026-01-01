#!/bin/bash

# OpenList启动脚本

echo "=== 启动OpenList服务 ==="

# 检查openlist二进制文件
if [ ! -f "./openlist" ]; then
    echo "错误: openlist二进制文件不存在"
    echo "请先构建或下载openlist二进制文件"
    exit 1
fi

# 创建必要目录
mkdir -p data
mkdir -p log

# 设置环境变量
export OPENLIST_DATA_DIR="./data"
export OPENLIST_LOG_DIR="./log"

echo "数据目录: $OPENLIST_DATA_DIR"
echo "日志目录: $OPENLIST_LOG_DIR"

# 检查数据库是否存在
if [ ! -f "./data/data.db" ]; then
    echo "数据库不存在，将初始化..."
    # 第一次运行会创建数据库
fi

# 启动服务
echo "启动OpenList服务..."
echo "服务将在 http://localhost:5244 运行"
echo "按 Ctrl+C 停止服务"

# 运行openlist
./openlist server

echo "OpenList服务已停止"