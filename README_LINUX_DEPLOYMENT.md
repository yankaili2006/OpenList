# OpenList Linux Server 部署指南

## 概述

本文档提供 OpenList 在 Linux Server 上的完整部署方案，包括自动化部署脚本、系统服务配置、Nginx 反向代理、SSL 证书配置等。

## 目录

1. [系统要求](#系统要求)
2. [快速部署](#快速部署)
3. [详细部署步骤](#详细部署步骤)
4. [Nginx 配置](#nginx-配置)
5. [SSL 证书配置](#ssl-证书配置)
6. [备份和恢复](#备份和恢复)
7. [监控和维护](#监控和维护)
8. [故障排除](#故障排除)
9. [高级配置](#高级配置)

## 系统要求

### 最低要求
- **操作系统**: Ubuntu 20.04+, Debian 11+, CentOS 8+, Rocky Linux 8+
- **CPU**: 1 核心
- **内存**: 512 MB RAM
- **存储**: 10 GB 可用空间
- **网络**: 稳定的网络连接

### 推荐配置
- **操作系统**: Ubuntu 22.04 LTS
- **CPU**: 2+ 核心
- **内存**: 2 GB RAM
- **存储**: 50 GB+ 可用空间（根据存储需求）
- **网络**: 100 Mbps+ 带宽

### 支持的架构
- x86_64 (amd64)
- aarch64 (arm64)
- armv7
- armv6
- i386 (386)

## 快速部署

### 方法一：使用自动化部署脚本（推荐）

```bash
# 下载部署脚本
wget https://raw.githubusercontent.com/OpenListTeam/OpenList/main/deploy_linux.sh

# 添加执行权限
chmod +x deploy_linux.sh

# 运行部署脚本（需要 root 权限）
sudo ./deploy_linux.sh
```

部署脚本会自动完成以下操作：
1. 检测系统信息
2. 安装系统依赖
3. 创建专用用户和目录
4. 下载最新版 OpenList
5. 创建配置文件
6. 配置 systemd 服务
7. 配置防火墙
8. 创建备份和监控脚本
9. 启动服务

### 方法二：Docker 部署

```bash
# 创建数据目录
sudo mkdir -p /etc/openlist
sudo chmod 750 /etc/openlist

# 下载 docker-compose.yml
wget https://raw.githubusercontent.com/OpenListTeam/OpenList/main/docker-compose.yml

# 启动服务
docker-compose up -d
```

## 详细部署步骤

### 1. 系统准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y curl wget git vim htop
```

### 2. 运行部署脚本

```bash
# 克隆仓库或下载脚本
git clone https://github.com/OpenListTeam/OpenList.git
cd OpenList

# 运行部署脚本
sudo ./deploy_linux.sh
```

### 3. 验证部署

```bash
# 检查服务状态
sudo systemctl status openlist

# 查看日志
sudo journalctl -u openlist -f

# 健康检查
sudo /opt/openlist/healthcheck.sh
```

### 4. 访问 OpenList

1. 获取初始管理员密码：
   ```bash
   sudo grep "initial password" /opt/openlist/data/logs/openlist.log
   ```

2. 在浏览器中访问：
   ```
   http://你的服务器IP:5244
   ```

3. 使用初始密码登录并立即修改密码

## Nginx 配置

### 安装 Nginx

```bash
# Ubuntu/Debian
sudo apt install -y nginx

# CentOS/Rocky Linux
sudo yum install -y nginx
```

### 配置反向代理

1. 复制配置文件：
   ```bash
   sudo cp nginx_openlist.conf /etc/nginx/sites-available/openlist
   ```

2. 修改配置文件中的域名：
   ```bash
   sudo sed -i 's/your-domain.com/你的域名/g' /etc/nginx/sites-available/openlist
   ```

3. 启用站点：
   ```bash
   sudo ln -s /etc/nginx/sites-available/openlist /etc/nginx/sites-enabled/
   sudo rm -f /etc/nginx/sites-enabled/default
   ```

4. 测试配置：
   ```bash
   sudo nginx -t
   ```

5. 重启 Nginx：
   ```bash
   sudo systemctl reload nginx
   ```

### 修改 OpenList 配置

更新 OpenList 配置以支持反向代理：

```bash
sudo nano /opt/openlist/data/config.json
```

修改以下配置：
```json
{
  "site_url": "https://你的域名",
  "scheme": {
    "https": true
  }
}
```

重启 OpenList：
```bash
sudo systemctl restart openlist
```

## SSL 证书配置

### 使用 Let's Encrypt

```bash
# 安装 certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d 你的域名 -d www.你的域名

# 自动续期测试
sudo certbot renew --dry-run
```

### 手动配置 SSL

如果你有自己的 SSL 证书：

1. 将证书文件复制到安全位置：
   ```bash
   sudo mkdir -p /etc/ssl/your-domain
   sudo cp your-cert.pem /etc/ssl/your-domain/fullchain.pem
   sudo cp your-key.pem /etc/ssl/your-domain/privkey.pem
   sudo chmod 600 /etc/ssl/your-domain/*
   ```

2. 更新 Nginx 配置中的证书路径

## 备份和恢复

### 自动备份

部署脚本已配置每日自动备份，备份文件保存在 `/backup/openlist/`。

手动执行备份：
```bash
sudo /opt/openlist/backup.sh
```

### 恢复备份

```bash
# 停止服务
sudo systemctl stop openlist

# 解压备份文件
sudo tar -xzf /backup/openlist/openlist_backup_YYYYMMDD_HHMMSS.tar.gz -C /opt/openlist/data/

# 恢复权限
sudo chown -R openlist:openlist /opt/openlist/data

# 启动服务
sudo systemctl start openlist
```

### 备份策略建议

1. **每日备份**：保留最近 30 天
2. **每周完整备份**：保留最近 12 周
3. **每月归档**：保留最近 12 个月
4. **异地备份**：重要数据建议同步到其他存储

## 监控和维护

### 健康检查

```bash
# 手动检查
sudo /opt/openlist/healthcheck.sh

# 添加到 crontab（每小时检查）
sudo crontab -l | { cat; echo "0 * * * * /opt/openlist/healthcheck.sh > /dev/null 2>&1"; } | sudo crontab -
```

### 日志管理

- 服务日志：`journalctl -u openlist`
- 访问日志：`/var/log/nginx/openlist_access.log`
- 错误日志：`/var/log/nginx/openlist_error.log`
- OpenList 日志：`/opt/openlist/data/logs/openlist.log`

### 性能监控

```bash
# 查看资源使用
htop
sudo df -h
sudo free -h

# 查看连接数
sudo netstat -an | grep :5244 | wc -l

# 查看进程状态
sudo ps aux | grep openlist
```

### 定期维护任务

1. **每周**：
   ```bash
   # 清理临时文件
   sudo find /opt/openlist/data/temp -type f -mtime +7 -delete
   
   # 更新系统
   sudo apt update && sudo apt upgrade -y
   ```

2. **每月**：
   ```bash
   # 检查磁盘空间
   sudo df -h
   
   # 检查日志文件大小
   sudo du -sh /var/log/nginx/* /opt/openlist/data/logs/*
   
   # 重启服务（应用更新）
   sudo systemctl restart openlist nginx
   ```

## 故障排除

### 常见问题

#### 1. 服务无法启动

```bash
# 查看详细错误信息
sudo journalctl -u openlist --no-pager -n 50

# 检查端口占用
sudo netstat -tlnp | grep :5244

# 检查配置文件
sudo /opt/openlist/openlist check --data /opt/openlist/data
```

#### 2. 无法访问 Web 界面

```bash
# 检查防火墙
sudo ufw status
# 或
sudo firewall-cmd --list-all

# 检查 Nginx 配置
sudo nginx -t

# 测试本地访问
curl -v http://localhost:5244/ping
```

#### 3. 忘记管理员密码

```bash
# 使用重置脚本
sudo /opt/openlist/reset_admin_password.sh

# 或手动重置
cd /opt/openlist
sudo -u openlist ./openlist admin --data /opt/openlist/data --reset
```

#### 4. 磁盘空间不足

```bash
# 查看磁盘使用
sudo df -h

# 清理临时文件
sudo rm -rf /opt/openlist/data/temp/*

# 清理旧日志
sudo find /var/log/nginx -name "*.log.*" -mtime +30 -delete
sudo find /opt/openlist/data/logs -name "*.log.*" -mtime +30 -delete
```

### 日志分析

```bash
# 查看错误日志
sudo tail -100 /opt/openlist/data/logs/openlist.log | grep -i error

# 查看最近的活动
sudo tail -50 /var/log/nginx/openlist_access.log

# 监控实时日志
sudo tail -f /opt/openlist/data/logs/openlist.log
```

## 高级配置

### 多实例部署

```bash
# 创建第二个实例
sudo cp -r /opt/openlist /opt/openlist2
sudo chown -R openlist:openlist /opt/openlist2

# 修改端口
sudo sed -i 's/"port": 5244/"port": 5246/' /opt/openlist2/data/config.json
sudo sed -i 's/"api_port": 5245/"api_port": 5247/' /opt/openlist2/data/config.json

# 创建第二个 systemd 服务
sudo cp /etc/systemd/system/openlist.service /etc/systemd/system/openlist2.service
sudo sed -i 's/openlist/openlist2/g' /etc/systemd/system/openlist2.service
sudo sed -i 's/5244/5246/g' /etc/systemd/system/openlist2.service
sudo sed -i 's/\/opt\/openlist/\/opt\/openlist2/g' /etc/systemd/system/openlist2.service

# 启动第二个实例
sudo systemctl daemon-reload
sudo systemctl enable openlist2
sudo systemctl start openlist2
```

### 数据库优化

#### 使用 PostgreSQL（推荐用于生产环境）

1. 安装 PostgreSQL：
   ```bash
   sudo apt install -y postgresql postgresql-contrib
   ```

2. 创建数据库和用户：
   ```sql
   CREATE DATABASE openlist;
   CREATE USER openlist WITH ENCRYPTED PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE openlist TO openlist;
   ```

3. 修改 OpenList 配置：
   ```json
   {
     "database": {
       "type": "postgres",
       "host": "localhost",
       "port": 5432,
       "user": "openlist",
       "password": "your_password",
       "name": "openlist",
       "ssl_mode": "disable"
     }
   }
   ```

#### SQLite 性能优化

```bash
# 在 .env 文件中添加
SQLITE_BUSY_TIMEOUT=5000
SQLITE_CACHE_SIZE=-20000  # 20MB 缓存
SQLITE_JOURNAL_MODE=WAL
```

### 内存和性能优化

#### 调整 Go 运行时参数

```bash
# 在 systemd 服务文件中添加
Environment=GOGC=100
Environment=GOMAXPROCS=2
Environment=GODEBUG=gctrace=1
```

#### 调整 Nginx 参数

```nginx
# 在 nginx.conf 的 http 块中添加
proxy_buffer_size 128k;
proxy_buffers 4 256k;
proxy_busy_buffers_size 256k;

# 连接池
upstream openlist_backend {
    server 127.0.0.1:5244;
    keepalive 32;
}
```

### 安全加固

#### 1. 防火墙规则

```bash
# 只允许特定 IP 访问管理端口
sudo ufw allow from 192.168.1.0/24 to any port 5244
sudo ufw deny 5244

# 或使用 fail2ban
sudo apt install -y fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
```

#### 2. 文件权限

```bash
# 限制配置文件权限
sudo chmod 640 /opt/openlist/data/config.json
sudo chmod 600 /opt/openlist/.env

# 设置不可变标志（谨慎使用）
sudo chattr +i /opt/openlist/data/config.json
```

#### 3. 定期安全更新

```bash
# 设置自动安全更新
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

### 高可用部署

#### 使用负载均衡器

```nginx
# Nginx 负载均衡配置
upstream openlist_cluster {
    least_conn;
    server 192.168.1.10:5244;
    server 192.168.1.11:5244;
    server 192.168.1.12:5244 backup;
    
    # 健康检查
    check interval=3000 rise=2 fall=5 timeout=1000;
}

server {
    location / {
        proxy_pass http://openlist_cluster;
        # ... 其他配置
    }
}
```

#### 共享存储配置

```bash
# 使用 NFS 共享数据目录
# 服务器端
sudo apt install -y nfs-kernel-server
sudo echo "/opt/openlist/data 192.168.1.0/24(rw,sync,no_subtree_check)" >> /etc/exports
sudo systemctl restart nfs-kernel-server

# 客户端
sudo apt install -y nfs-common
sudo mount -t nfs 192.168.1.100:/opt/openlist/data /opt/openlist/data
```

## 更新 OpenList

### 自动更新脚本

```bash
#!/bin/bash
# update_openlist.sh

set -e

echo "开始更新 OpenList..."

# 备份当前版本
BACKUP_DIR="/backup/openlist/updates"
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/openlist_$(date +%Y%m%d_%H%M%S).tar.gz /opt/openlist/openlist

# 停止服务
systemctl stop openlist

# 下载最新版本
cd /opt/openlist
ARCH=$(uname -m)
case $ARCH in
    x86_64) ARCH="amd64" ;;
    aarch64) ARCH="arm64" ;;
    armv7l) ARCH="armv7" ;;
    *) echo "不支持的架构"; exit 1 ;;
esac

LATEST_TAG=$(curl -s https://api.github.com/repos/OpenListTeam/OpenList/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
DOWNLOAD_URL="https://github.com/OpenListTeam/OpenList/releases/download/${LATEST_TAG}/openlist-linux-${ARCH}.tar.gz"

wget -O openlist.tar.gz "$DOWNLOAD_URL"
tar -xzf openlist.tar.gz
rm openlist.tar.gz
chmod +x openlist
chown openlist:openlist openlist

# 启动服务
systemctl start openlist

echo "OpenList 更新完成，当前版本: $LATEST_TAG"
```

### 手动更新

```bash
# 查看当前版本
/opt/openlist/openlist version

# 下载新版本
cd /opt/openlist
sudo systemctl stop openlist
sudo wget -O openlist.tar.gz "下载链接"
sudo tar -xzf openlist.tar.gz
sudo rm openlist.tar.gz
sudo chmod +x openlist
sudo systemctl start openlist
```

## 卸载 OpenList

```bash
# 停止服务
sudo systemctl stop openlist
sudo systemctl disable openlist

# 删除服务文件
sudo rm -f /etc/systemd/system/openlist.service
sudo systemctl daemon-reload

# 删除用户和组
sudo userdel openlist
sudo groupdel openlist

# 删除文件（谨慎操作！先备份数据）
sudo rm -rf /opt/openlist
sudo rm -rf /backup/openlist
sudo rm -f /etc/logrotate.d/openlist

# 删除 Nginx 配置
sudo rm -f /etc/nginx/sites-available/openlist
sudo rm -f /etc/nginx/sites-enabled/openlist
sudo systemctl reload nginx
```

## 获取帮助

### 官方资源
- **文档**: https://doc.oplist.org
- **GitHub**: https://github.com/OpenListTeam/OpenList
- **讨论区**: https://github.com/OpenListTeam/OpenList/discussions
- **Telegram 群组**: https://t.me/OpenListTeam

### 社区支持
- 在 GitHub Issues 报告问题
- 在 Discussions 提问
- 加入 Telegram 群组交流

### 故障诊断命令

```bash
# 系统状态
sudo systemctl status openlist nginx
sudo journalctl -u openlist --since "1 hour ago"
sudo netstat -tlnp | grep -E '(5244|5245)'

# 配置检查
sudo /opt/openlist/openlist check --data /opt/openlist/data
sudo nginx -t

# 性能检查
sudo /opt/openlist/healthcheck.sh
sudo df -h /opt/openlist/data
sudo free -h
```

---

**注意**: 生产环境部署前请务必进行充分测试，并确保有完整的数据备份方案。

**最后更新**: 2025年12月28日
**版本**: 1.0.0