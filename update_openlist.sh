#!/bin/bash
# OpenList 更新脚本
# 自动下载并更新到最新版本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
OPENLIST_HOME="/opt/openlist"
OPENLIST_USER="openlist"
OPENLIST_GROUP="openlist"
BACKUP_DIR="/backup/openlist/updates"

# 检测架构
detect_architecture() {
    ARCH=$(uname -m)
    case $ARCH in
        x86_64)
            echo "amd64"
            ;;
        aarch64)
            echo "arm64"
            ;;
        armv7l)
            echo "armv7"
            ;;
        armv6l)
            echo "armv6"
            ;;
        i386|i686)
            echo "386"
            ;;
        *)
            echo -e "${RED}[ERROR]${NC} 不支持的架构: $ARCH"
            exit 1
            ;;
    esac
}

# 获取最新版本
get_latest_version() {
    echo -e "${BLUE}[INFO]${NC} 获取最新版本信息..."
    
    # 尝试从 GitHub API 获取
    LATEST_TAG=$(curl -s --max-time 10 \
        -H "Accept: application/vnd.github.v3+json" \
        https://api.github.com/repos/OpenListTeam/OpenList/releases/latest | \
        grep '"tag_name":' | \
        sed -E 's/.*"([^"]+)".*/\1/')
    
    if [ -z "$LATEST_TAG" ]; then
        # 备用方法：从 releases 页面获取
        LATEST_TAG=$(curl -s --max-time 10 \
            https://github.com/OpenListTeam/OpenList/releases/latest | \
            grep -o 'tag/[^"]*' | \
            cut -d'/' -f2)
    fi
    
    if [ -z "$LATEST_TAG" ]; then
        echo -e "${RED}[ERROR]${NC} 无法获取最新版本信息"
        exit 1
    fi
    
    echo "$LATEST_TAG"
}

# 获取当前版本
get_current_version() {
    if [ -f "$OPENLIST_HOME/openlist" ]; then
        CURRENT_VERSION=$($OPENLIST_HOME/openlist version 2>/dev/null | grep -o 'v[0-9]\+\.[0-9]\+\.[0-9]\+' || echo "unknown")
        echo "$CURRENT_VERSION"
    else
        echo "not_installed"
    fi
}

# 备份当前版本
backup_current_version() {
    echo -e "${BLUE}[INFO]${NC} 备份当前版本..."
    
    mkdir -p "$BACKUP_DIR"
    
    if [ -f "$OPENLIST_HOME/openlist" ]; then
        BACKUP_FILE="$BACKUP_DIR/openlist_$(date +%Y%m%d_%H%M%S).tar.gz"
        tar -czf "$BACKUP_FILE" \
            "$OPENLIST_HOME/openlist" \
            "$OPENLIST_HOME/.env" \
            "$OPENLIST_HOME/backup.sh" \
            "$OPENLIST_HOME/healthcheck.sh" 2>/dev/null || true
        
        BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        echo -e "${GREEN}[SUCCESS]${NC} 备份完成: $BACKUP_FILE ($BACKUP_SIZE)"
    else
        echo -e "${YELLOW}[WARNING]${NC} 未找到当前版本，跳过备份"
    fi
}

# 下载新版本
download_new_version() {
    local VERSION=$1
    local ARCH=$2
    
    echo -e "${BLUE}[INFO]${NC} 下载版本: $VERSION (架构: $ARCH)"
    
    # 构建下载 URL
    DOWNLOAD_URL="https://github.com/OpenListTeam/OpenList/releases/download/${VERSION}/openlist-linux-${ARCH}.tar.gz"
    
    # 临时文件
    TEMP_FILE="/tmp/openlist-${VERSION}-${ARCH}.tar.gz"
    
    # 下载
    echo -e "${BLUE}[INFO]${NC} 下载中: $DOWNLOAD_URL"
    if wget -q --show-progress -O "$TEMP_FILE" "$DOWNLOAD_URL"; then
        echo -e "${GREEN}[SUCCESS]${NC} 下载完成"
        echo "$TEMP_FILE"
    else
        echo -e "${RED}[ERROR]${NC} 下载失败"
        
        # 尝试备用下载链接
        echo -e "${YELLOW}[INFO]${NC} 尝试备用下载链接..."
        DOWNLOAD_URL="https://github.com/OpenListTeam/OpenList/releases/download/${VERSION}/openlist-linux-${ARCH}"
        if wget -q --show-progress -O "$TEMP_FILE" "$DOWNLOAD_URL"; then
            echo -e "${GREEN}[SUCCESS]${NC} 备用下载完成"
            echo "$TEMP_FILE"
        else
            echo -e "${RED}[ERROR]${NC} 所有下载尝试都失败"
            exit 1
        fi
    fi
}

# 验证下载文件
verify_download() {
    local FILE=$1
    
    echo -e "${BLUE}[INFO]${NC} 验证下载文件..."
    
    # 检查文件大小
    FILE_SIZE=$(stat -c%s "$FILE" 2>/dev/null || stat -f%z "$FILE")
    if [ "$FILE_SIZE" -lt 1000000 ]; then  # 小于 1MB 可能是错误
        echo -e "${RED}[ERROR]${NC} 文件大小异常: $FILE_SIZE 字节"
        return 1
    fi
    
    # 检查文件类型
    FILE_TYPE=$(file -b "$FILE")
    if echo "$FILE_TYPE" | grep -q "gzip compressed data"; then
        echo -e "${GREEN}[SUCCESS]${NC} 文件验证通过"
        return 0
    elif echo "$FILE_TYPE" | grep -q "ELF"; then
        echo -e "${GREEN}[SUCCESS]${NC} 文件验证通过 (二进制文件)"
        return 0
    else
        echo -e "${YELLOW}[WARNING]${NC} 未知文件类型: $FILE_TYPE"
        return 0  # 继续尝试
    fi
}

# 安装新版本
install_new_version() {
    local TEMP_FILE=$1
    
    echo -e "${BLUE}[INFO]${NC} 安装新版本..."
    
    # 停止服务
    echo -e "${BLUE}[INFO]${NC} 停止 OpenList 服务..."
    systemctl stop openlist 2>/dev/null || true
    
    # 备份当前二进制文件
    if [ -f "$OPENLIST_HOME/openlist" ]; then
        mv "$OPENLIST_HOME/openlist" "$OPENLIST_HOME/openlist.bak"
    fi
    
    # 解压或复制新版本
    cd "$OPENLIST_HOME"
    
    if echo "$TEMP_FILE" | grep -q "\.tar\.gz$"; then
        # 解压 tar.gz 文件
        tar -xzf "$TEMP_FILE"
        rm -f "$TEMP_FILE"
    else
        # 直接复制二进制文件
        mv "$TEMP_FILE" "./openlist"
    fi
    
    # 设置权限
    chmod +x openlist
    chown "$OPENLIST_USER:$OPENLIST_GROUP" openlist
    
    # 清理备份文件
    rm -f "$OPENLIST_HOME/openlist.bak" 2>/dev/null || true
    
    echo -e "${GREEN}[SUCCESS]${NC} 新版本安装完成"
}

# 启动服务
start_service() {
    echo -e "${BLUE}[INFO]${NC} 启动 OpenList 服务..."
    
    if systemctl start openlist; then
        echo -e "${GREEN}[SUCCESS]${NC} 服务启动成功"
        
        # 等待服务完全启动
        sleep 3
        
        # 检查服务状态
        if systemctl is-active --quiet openlist; then
            echo -e "${GREEN}[SUCCESS]${NC} 服务运行正常"
            return 0
        else
            echo -e "${RED}[ERROR]${NC} 服务启动后停止"
            return 1
        fi
    else
        echo -e "${RED}[ERROR]${NC} 服务启动失败"
        return 1
    fi
}

# 回滚到旧版本
rollback_version() {
    echo -e "${RED}[ERROR]${NC} 新版本安装失败，尝试回滚..."
    
    # 恢复备份
    if [ -f "$OPENLIST_HOME/openlist.bak" ]; then
        mv "$OPENLIST_HOME/openlist.bak" "$OPENLIST_HOME/openlist"
        chmod +x "$OPENLIST_HOME/openlist"
        chown "$OPENLIST_USER:$OPENLIST_GROUP" "$OPENLIST_HOME/openlist"
        
        # 启动服务
        systemctl start openlist 2>/dev/null || true
        
        echo -e "${YELLOW}[WARNING]${NC} 已回滚到旧版本"
    else
        echo -e "${RED}[ERROR]${NC} 找不到备份文件，无法回滚"
    fi
}

# 显示更新摘要
show_summary() {
    local OLD_VERSION=$1
    local NEW_VERSION=$2
    
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}        OpenList 更新完成              ${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${BLUE}更新信息:${NC}"
    echo "  • 旧版本: $OLD_VERSION"
    echo "  • 新版本: $NEW_VERSION"
    echo "  • 架构: $(detect_architecture)"
    echo ""
    echo -e "${BLUE}服务状态:${NC}"
    echo "  • 状态: $(systemctl is-active openlist)"
    echo "  • 启动时间: $(systemctl show -p ActiveEnterTimestamp openlist | cut -d= -f2)"
    echo ""
    echo -e "${BLUE}备份信息:${NC}"
    echo "  • 备份目录: $BACKUP_DIR"
    echo "  • 最新备份: $(ls -t $BACKUP_DIR/openlist_*.tar.gz 2>/dev/null | head -1 | xargs basename 2>/dev/null || echo '无')"
    echo ""
    echo -e "${YELLOW}建议操作:${NC}"
    echo "1. 检查服务日志: journalctl -u openlist --since '5 minutes ago'"
    echo "2. 验证功能: 访问 Web 界面测试"
    echo "3. 检查健康状态: $OPENLIST_HOME/healthcheck.sh"
    echo ""
    echo -e "${GREEN}更新完成!${NC}"
}

# 主函数
main() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}        OpenList 更新脚本              ${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    
    # 检查 root 权限
    if [ "$EUID" -ne 0 ]; then 
        echo -e "${RED}[ERROR]${NC} 请使用 root 用户或 sudo 运行此脚本"
        exit 1
    fi
    
    # 检查 OpenList 是否安装
    if [ ! -d "$OPENLIST_HOME" ]; then
        echo -e "${RED}[ERROR]${NC} OpenList 未安装，请先运行部署脚本"
        exit 1
    fi
    
    # 获取当前版本
    CURRENT_VERSION=$(get_current_version)
    echo -e "${BLUE}[INFO]${NC} 当前版本: $CURRENT_VERSION"
    
    # 获取最新版本
    LATEST_VERSION=$(get_latest_version)
    echo -e "${BLUE}[INFO]${NC} 最新版本: $LATEST_VERSION"
    
    # 检查是否需要更新
    if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
        echo -e "${GREEN}[INFO]${NC} 已经是最新版本，无需更新"
        exit 0
    fi
    
    if [ "$CURRENT_VERSION" = "not_installed" ]; then
        echo -e "${YELLOW}[WARNING]${NC} 未检测到当前版本，继续更新..."
    fi
    
    # 确认更新
    echo ""
    echo -e "${YELLOW}[确认]${NC} 即将更新 OpenList:"
    echo "  从: $CURRENT_VERSION"
    echo "  到: $LATEST_VERSION"
    echo ""
    read -p "是否继续? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}[INFO]${NC} 更新已取消"
        exit 0
    fi
    
    # 执行更新步骤
    ARCH=$(detect_architecture)
    backup_current_version
    
    # 下载新版本
    DOWNLOADED_FILE=$(download_new_version "$LATEST_VERSION" "$ARCH")
    
    # 验证下载
    if ! verify_download "$DOWNLOADED_FILE"; then
        echo -e "${RED}[ERROR]${NC} 文件验证失败"
        exit 1
    fi
    
    # 安装新版本
    if install_new_version "$DOWNLOADED_FILE"; then
        # 启动服务
        if start_service; then
            show_summary "$CURRENT_VERSION" "$LATEST_VERSION"
        else
            rollback_version
            exit 1
        fi
    else
        rollback_version
        exit 1
    fi
}

# 执行主函数
main "$@"