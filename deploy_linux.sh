#!/bin/bash
# OpenList Linux Server 部署脚本
# 版本: 1.0.0
# 作者: OpenList Team
# 描述: 在 Linux Server 上自动化部署 OpenList

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
OPENLIST_VERSION="latest"
OPENLIST_USER="openlist"
OPENLIST_GROUP="openlist"
OPENLIST_HOME="/opt/openlist"
OPENLIST_DATA="/opt/openlist/data"
OPENLIST_LOG="/var/log/openlist"
OPENLIST_PORT="5244"
OPENLIST_API_PORT="5245"
OPENLIST_BACKUP_DIR="/backup/openlist"

# 检测系统信息
detect_system() {
    echo -e "${BLUE}[INFO]${NC} 检测系统信息..."
    
    # 检测发行版
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si)
        VER=$(lsb_release -sr)
    elif [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        OS=$DISTRIB_ID
        VER=$DISTRIB_RELEASE
    elif [ -f /etc/debian_version ]; then
        OS=Debian
        VER=$(cat /etc/debian_version)
    elif [ -f /etc/redhat-release ]; then
        OS=$(cat /etc/redhat-release | cut -d ' ' -f1)
        VER=$(cat /etc/redhat-release | cut -d ' ' -f3)
    else
        OS=$(uname -s)
        VER=$(uname -r)
    fi
    
    # 检测架构
    ARCH=$(uname -m)
    case $ARCH in
        x86_64)
            ARCH="amd64"
            ;;
        aarch64)
            ARCH="arm64"
            ;;
        armv7l)
            ARCH="armv7"
            ;;
        armv6l)
            ARCH="armv6"
            ;;
        i386|i686)
            ARCH="386"
            ;;
        *)
            echo -e "${RED}[ERROR]${NC} 不支持的架构: $ARCH"
            exit 1
            ;;
    esac
    
    echo -e "${GREEN}[SUCCESS]${NC} 系统: $OS $VER"
    echo -e "${GREEN}[SUCCESS]${NC} 架构: $ARCH"
}

# 检查 root 权限
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        echo -e "${RED}[ERROR]${NC} 请使用 root 用户或 sudo 运行此脚本"
        exit 1
    fi
}

# 安装系统依赖
install_dependencies() {
    echo -e "${BLUE}[INFO]${NC} 安装系统依赖..."
    
    case $OS in
        Ubuntu|Debian)
            apt-get update
            apt-get install -y curl wget sqlite3 nginx certbot python3-certbot-nginx \
                ufw fail2ban cron logrotate
            ;;
        CentOS*|RedHat*|Fedora*)
            yum install -y epel-release
            yum install -y curl wget sqlite3 nginx certbot python3-certbot-nginx \
                firewalld fail2ban cronie logrotate
            systemctl enable firewalld
            systemctl start firewalld
            ;;
        *)
            echo -e "${YELLOW}[WARNING]${NC} 不支持的系统发行版，请手动安装依赖"
            echo "需要的依赖: curl, wget, sqlite3, nginx, certbot, fail2ban, cron, logrotate"
            read -p "是否继续? (y/n): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
            ;;
    esac
    
    echo -e "${GREEN}[SUCCESS]${NC} 依赖安装完成"
}

# 创建用户和目录
create_user_and_dirs() {
    echo -e "${BLUE}[INFO]${NC} 创建用户和目录..."
    
    # 创建用户组
    if ! getent group $OPENLIST_GROUP > /dev/null; then
        groupadd --system $OPENLIST_GROUP
    fi
    
    # 创建用户
    if ! id -u $OPENLIST_USER > /dev/null 2>&1; then
        useradd --system --no-create-home --shell /bin/false \
            --gid $OPENLIST_GROUP $OPENLIST_USER
    fi
    
    # 创建目录
    mkdir -p $OPENLIST_HOME
    mkdir -p $OPENLIST_DATA
    mkdir -p $OPENLIST_LOG
    mkdir -p $OPENLIST_BACKUP_DIR
    
    # 设置权限
    chown -R $OPENLIST_USER:$OPENLIST_GROUP $OPENLIST_HOME
    chown -R $OPENLIST_USER:$OPENLIST_GROUP $OPENLIST_DATA
    chown -R $OPENLIST_USER:$OPENLIST_GROUP $OPENLIST_LOG
    chown -R $OPENLIST_USER:$OPENLIST_GROUP $OPENLIST_BACKUP_DIR
    
    chmod 750 $OPENLIST_HOME
    chmod 750 $OPENLIST_DATA
    chmod 750 $OPENLIST_LOG
    chmod 750 $OPENLIST_BACKUP_DIR
    
    echo -e "${GREEN}[SUCCESS]${NC} 用户和目录创建完成"
}

# 下载 OpenList
download_openlist() {
    echo -e "${BLUE}[INFO]${NC} 下载 OpenList..."
    
    cd $OPENLIST_HOME
    
    # 获取最新版本
    if [ "$OPENLIST_VERSION" = "latest" ]; then
        LATEST_TAG=$(curl -s https://api.github.com/repos/OpenListTeam/OpenList/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
        OPENLIST_VERSION=$LATEST_TAG
    fi
    
    echo -e "${BLUE}[INFO]${NC} 下载版本: $OPENLIST_VERSION"
    
    # 构建下载 URL
    DOWNLOAD_URL="https://github.com/OpenListTeam/OpenList/releases/download/${OPENLIST_VERSION}/openlist-linux-${ARCH}.tar.gz"
    
    # 下载并解压
    if wget -q --show-progress -O openlist.tar.gz "$DOWNLOAD_URL"; then
        tar -xzf openlist.tar.gz
        rm openlist.tar.gz
        
        # 设置执行权限
        chmod +x openlist
        chown $OPENLIST_USER:$OPENLIST_GROUP openlist
        
        echo -e "${GREEN}[SUCCESS]${NC} OpenList 下载完成"
    else
        echo -e "${RED}[ERROR]${NC} 下载失败，请检查网络连接或版本号"
        exit 1
    fi
}

# 创建配置文件
create_config() {
    echo -e "${BLUE}[INFO]${NC} 创建配置文件..."
    
    # 生成 JWT 密钥
    JWT_SECRET=$(openssl rand -base64 32)
    
    # 创建环境配置文件
    cat > $OPENLIST_HOME/.env << EOF
# OpenList 环境配置
UMASK=022
TZ=Asia/Shanghai
JWT_SECRET=$JWT_SECRET
RUN_ARIA2=false
RUN_FFMPEG=false
EOF
    
    # 创建默认配置文件
    if [ ! -f $OPENLIST_DATA/config.json ]; then
        cat > $OPENLIST_DATA/config.json << EOF
{
  "force": false,
  "address": "0.0.0.0",
  "port": $OPENLIST_PORT,
  "api_port": $OPENLIST_API_PORT,
  "site_url": "",
  "cdn": "",
  "jwt_secret": "$JWT_SECRET",
  "token_expires_in": 48,
  "database": {
    "type": "sqlite3",
    "host": "",
    "port": 0,
    "user": "",
    "password": "",
    "name": "",
    "db_file": "$OPENLIST_DATA/data.db",
    "table_prefix": "x_",
    "ssl_mode": ""
  },
  "scheme": {
    "https": false,
    "cert_file": "",
    "key_file": ""
  },
  "temp_dir": "$OPENLIST_DATA/temp",
  "log": {
    "enable": true,
    "name": "$OPENLIST_LOG/openlist.log",
    "max_size": 10,
    "max_backups": 5,
    "max_age": 28,
    "compress": true
  },
  "max_connections": 0,
  "tls_insecure_skip_verify": false
}
EOF
    fi
    
    chown $OPENLIST_USER:$OPENLIST_GROUP $OPENLIST_HOME/.env
    chown $OPENLIST_USER:$OPENLIST_GROUP $OPENLIST_DATA/config.json
    chmod 640 $OPENLIST_HOME/.env
    chmod 640 $OPENLIST_DATA/config.json
    
    echo -e "${GREEN}[SUCCESS]${NC} 配置文件创建完成"
}

# 创建 systemd 服务
create_systemd_service() {
    echo -e "${BLUE}[INFO]${NC} 创建 systemd 服务..."
    
    cat > /etc/systemd/system/openlist.service << EOF
[Unit]
Description=OpenList - Multiple cloud storage manager
Documentation=https://doc.oplist.org
After=network.target
Wants=network.target

[Service]
Type=simple
User=$OPENLIST_USER
Group=$OPENLIST_GROUP
WorkingDirectory=$OPENLIST_HOME
EnvironmentFile=$OPENLIST_HOME/.env
ExecStart=$OPENLIST_HOME/openlist server --data $OPENLIST_DATA
ExecReload=/bin/kill -HUP \$MAINPID
Restart=on-failure
RestartSec=5
TimeoutStopSec=30

# 安全配置
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=$OPENLIST_DATA $OPENLIST_LOG
PrivateDevices=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true

# 资源限制
LimitNOFILE=65535
LimitNPROC=65535

# 日志配置
StandardOutput=journal
StandardError=journal
SyslogIdentifier=openlist

[Install]
WantedBy=multi-user.target
EOF
    
    # 创建日志配置文件
    cat > /etc/systemd/system/openlist.service.d/override.conf << EOF
[Service]
# 日志轮转
LogRateLimitIntervalSec=30s
LogRateLimitBurst=10000
EOF
    
    mkdir -p /etc/systemd/system/openlist.service.d
    
    systemctl daemon-reload
    systemctl enable openlist.service
    
    echo -e "${GREEN}[SUCCESS]${NC} systemd 服务创建完成"
}

# 配置防火墙
configure_firewall() {
    echo -e "${BLUE}[INFO]${NC} 配置防火墙..."
    
    case $OS in
        Ubuntu|Debian)
            ufw --force enable
            ufw allow ssh
            ufw allow $OPENLIST_PORT/tcp comment "OpenList Web"
            ufw allow $OPENLIST_API_PORT/tcp comment "OpenList API"
            ufw reload
            ;;
        CentOS*|RedHat*|Fedora*)
            firewall-cmd --permanent --add-service=ssh
            firewall-cmd --permanent --add-port=$OPENLIST_PORT/tcp --zone=public
            firewall-cmd --permanent --add-port=$OPENLIST_API_PORT/tcp --zone=public
            firewall-cmd --reload
            ;;
    esac
    
    echo -e "${GREEN}[SUCCESS]${NC} 防火墙配置完成"
}

# 配置日志轮转
configure_logrotate() {
    echo -e "${BLUE}[INFO]${NC} 配置日志轮转..."
    
    cat > /etc/logrotate.d/openlist << EOF
$OPENLIST_LOG/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 640 $OPENLIST_USER $OPENLIST_GROUP
    postrotate
        systemctl reload openlist > /dev/null 2>&1 || true
    endscript
}
EOF
    
    echo -e "${GREEN}[SUCCESS]${NC} 日志轮转配置完成"
}

# 创建备份脚本
create_backup_script() {
    echo -e "${BLUE}[INFO]${NC} 创建备份脚本..."
    
    cat > $OPENLIST_HOME/backup.sh << 'EOF'
#!/bin/bash
# OpenList 备份脚本

set -e

# 配置
OPENLIST_DATA="/opt/openlist/data"
BACKUP_DIR="/backup/openlist"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# 创建备份目录
mkdir -p $BACKUP_DIR

# 停止服务（可选）
# systemctl stop openlist

# 备份数据库和配置文件
BACKUP_FILE="$BACKUP_DIR/openlist_backup_$DATE.tar.gz"
tar -czf $BACKUP_FILE \
    $OPENLIST_DATA/data.db \
    $OPENLIST_DATA/config.json \
    $OPENLIST_DATA/settings.json 2>/dev/null || true

# 计算备份大小
BACKUP_SIZE=$(du -h $BACKUP_FILE | cut -f1)

# 记录备份日志
echo "$(date '+%Y-%m-%d %H:%M:%S') - 备份完成: $BACKUP_FILE ($BACKUP_SIZE)" >> $BACKUP_DIR/backup.log

# 清理旧备份
find $BACKUP_DIR -name "openlist_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete

# 启动服务（如果停止了）
# systemctl start openlist

echo "备份完成: $BACKUP_FILE ($BACKUP_SIZE)"
EOF
    
    chmod +x $OPENLIST_HOME/backup.sh
    chown $OPENLIST_USER:$OPENLIST_GROUP $OPENLIST_HOME/backup.sh
    
    # 添加到 crontab
    (crontab -l 2>/dev/null; echo "0 2 * * * $OPENLIST_HOME/backup.sh > /dev/null 2>&1") | crontab -
    
    echo -e "${GREEN}[SUCCESS]${NC} 备份脚本创建完成"
}

# 创建监控脚本
create_monitor_script() {
    echo -e "${BLUE}[INFO]${NC} 创建监控脚本..."
    
    cat > $OPENLIST_HOME/healthcheck.sh << 'EOF'
#!/bin/bash
# OpenList 健康检查脚本

HEALTH_URL="http://localhost:5244/ping"
TIMEOUT=5
MAX_RETRIES=3
RETRY_DELAY=2

check_health() {
    for i in $(seq 1 $MAX_RETRIES); do
        response=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT $HEALTH_URL 2>/dev/null)
        
        if [ "$response" = "200" ]; then
            echo "OK"
            return 0
        fi
        
        if [ $i -lt $MAX_RETRIES ]; then
            sleep $RETRY_DELAY
        fi
    done
    
    echo "FAIL (HTTP $response)"
    return 1
}

check_disk_space() {
    USAGE=$(df -h $OPENLIST_DATA | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $USAGE -gt 90 ]; then
        echo "WARNING: 磁盘使用率 $USAGE%"
        return 1
    fi
    return 0
}

check_memory() {
    MEM_FREE=$(free -m | awk 'NR==2 {print $4}')
    if [ $MEM_FREE -lt 100 ]; then
        echo "WARNING: 可用内存不足 $MEM_FREE MB"
        return 1
    fi
    return 0
}

# 执行检查
echo "=== OpenList 健康检查 ==="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"

echo -n "服务状态: "
if systemctl is-active --quiet openlist; then
    echo "运行中"
else
    echo "停止"
    exit 1
fi

echo -n "API 健康: "
check_health

echo -n "磁盘空间: "
check_disk_space

echo -n "内存状态: "
check_memory

echo "=== 检查完成 ==="
EOF
    
    chmod +x $OPENLIST_HOME/healthcheck.sh
    chown $OPENLIST_USER:$OPENLIST_GROUP $OPENLIST_HOME/healthcheck.sh
    
    echo -e "${GREEN}[SUCCESS]${NC} 监控脚本创建完成"
}

# 启动服务
start_service() {
    echo -e "${BLUE}[INFO]${NC} 启动 OpenList 服务..."
    
    systemctl start openlist
    sleep 3
    
    if systemctl is-active --quiet openlist; then
        echo -e "${GREEN}[SUCCESS]${NC} OpenList 服务启动成功"
        
        # 显示初始密码
        if [ -f $OPENLIST_DATA/logs/openlist.log ]; then
            INIT_PASSWORD=$(grep -o "initial password is: [a-zA-Z0-9]*" $OPENLIST_DATA/logs/openlist.log | tail -1 | cut -d' ' -f4)
            if [ ! -z "$INIT_PASSWORD" ]; then
                echo -e "${YELLOW}[IMPORTANT]${NC} 初始管理员密码: $INIT_PASSWORD"
                echo -e "${YELLOW}[IMPORTANT]${NC} 请及时登录并修改密码"
            fi
        fi
        
        echo -e "${GREEN}[SUCCESS]${NC} 服务状态:"
        systemctl status openlist --no-pager -l
        
        echo -e "\n${BLUE}[INFO]${NC} 访问信息:"
        echo "Web 界面: http://$(hostname -I | awk '{print $1}'):$OPENLIST_PORT"
        echo "API 端口: $OPENLIST_API_PORT"
        echo "数据目录: $OPENLIST_DATA"
        echo "日志目录: $OPENLIST_LOG"
        
    else
        echo -e "${RED}[ERROR]${NC} 服务启动失败"
        journalctl -u openlist --no-pager -n 20
        exit 1
    fi
}

# 显示部署摘要
show_summary() {
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}        OpenList 部署完成              ${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${BLUE}部署信息:${NC}"
    echo "  • 版本: $OPENLIST_VERSION"
    echo "  • 架构: $ARCH"
    echo "  • 用户: $OPENLIST_USER"
    echo "  • 数据目录: $OPENLIST_DATA"
    echo "  • 日志目录: $OPENLIST_LOG"
    echo ""
    echo -e "${BLUE}服务信息:${NC}"
    echo "  • Web 端口: $OPENLIST_PORT"
    echo "  • API 端口: $OPENLIST_API_PORT"
    echo "  • 服务状态: $(systemctl is-active openlist)"
    echo ""
    echo -e "${BLUE}管理命令:${NC}"
    echo "  • 启动服务: systemctl start openlist"
    echo "  • 停止服务: systemctl stop openlist"
    echo "  • 重启服务: systemctl restart openlist"
    echo "  • 查看状态: systemctl status openlist"
    echo "  • 查看日志: journalctl -u openlist -f"
    echo ""
    echo -e "${BLUE}工具脚本:${NC}"
    echo "  • 健康检查: $OPENLIST_HOME/healthcheck.sh"
    echo "  • 数据备份: $OPENLIST_HOME/backup.sh"
    echo ""
    echo -e "${YELLOW}重要提示:${NC}"
    echo "1. 首次访问请使用初始管理员密码"
    echo "2. 建议配置 SSL/TLS 证书"
    echo "3. 定期检查备份是否正常执行"
    echo "4. 监控磁盘空间和内存使用"
    echo ""
    echo -e "${GREEN}部署完成! 现在可以通过浏览器访问 OpenList${NC}"
    echo -e "${GREEN}地址: http://$(hostname -I | awk '{print $1}'):$OPENLIST_PORT${NC}"
}

# 主函数
main() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}    OpenList Linux Server 部署脚本     ${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    
    # 执行部署步骤
    check_root
    detect_system
    install_dependencies
    create_user_and_dirs
    download_openlist
    create_config
    create_systemd_service
    configure_firewall
    configure_logrotate
    create_backup_script
    create_monitor_script
    start_service
    show_summary
}

# 执行主函数
main "$@"