# OpenList Linux Server 快速部署指南

## 一分钟快速部署

### 方法一：一键部署脚本（推荐）

```bash
# 下载并运行部署脚本
wget -O - https://raw.githubusercontent.com/OpenListTeam/OpenList/main/deploy_linux.sh | sudo bash
```

### 方法二：分步执行

```bash
# 1. 下载脚本
wget https://raw.githubusercontent.com/OpenListTeam/OpenList/main/deploy_linux.sh

# 2. 添加执行权限
chmod +x deploy_linux.sh

# 3. 运行部署
sudo ./deploy_linux.sh
```

## 部署后操作

### 1. 获取初始密码
```bash
# 查看初始管理员密码
sudo grep "initial password" /opt/openlist/data/logs/openlist.log
```

### 2. 访问 OpenList
- **地址**: `http://你的服务器IP:5244`
- **用户名**: `admin`
- **密码**: 上一步获取的初始密码

### 3. 基本管理命令
```bash
# 查看服务状态
sudo systemctl status openlist

# 重启服务
sudo systemctl restart openlist

# 查看日志
sudo journalctl -u openlist -f

# 健康检查
sudo /opt/openlist/healthcheck.sh
```

## 进阶配置（可选）

### 配置域名和 SSL
```bash
# 1. 安装 Nginx 和 Certbot
sudo apt install -y nginx certbot python3-certbot-nginx

# 2. 配置 Nginx
sudo cp nginx_openlist.conf /etc/nginx/sites-available/openlist
sudo sed -i 's/your-domain.com/你的域名/g' /etc/nginx/sites-available/openlist
sudo ln -s /etc/nginx/sites-available/openlist /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 3. 获取 SSL 证书
sudo certbot --nginx -d 你的域名
```

### 配置自动备份
```bash
# 查看备份配置
sudo crontab -l | grep backup

# 手动执行备份
sudo /opt/openlist/backup.sh
```

## 故障排除

### 常见问题

#### 1. 无法访问
```bash
# 检查防火墙
sudo ufw status

# 检查端口
sudo netstat -tlnp | grep :5244

# 测试本地访问
curl http://localhost:5244/ping
```

#### 2. 服务无法启动
```bash
# 查看详细错误
sudo journalctl -u openlist --no-pager -n 50

# 检查配置文件
sudo /opt/openlist/openlist check --data /opt/openlist/data
```

#### 3. 忘记密码
```bash
# 重置管理员密码
cd /opt/openlist
sudo -u openlist ./openlist admin --data /opt/openlist/data --reset
```

## 更新 OpenList

```bash
# 使用更新脚本
sudo /opt/openlist/update_openlist.sh

# 或手动更新
cd /opt/openlist
sudo systemctl stop openlist
sudo wget -O openlist.tar.gz "最新版本下载链接"
sudo tar -xzf openlist.tar.gz
sudo systemctl start openlist
```

## 卸载 OpenList

```bash
# 停止服务
sudo systemctl stop openlist
sudo systemctl disable openlist

# 删除文件（谨慎操作！先备份数据）
sudo rm -rf /opt/openlist
sudo userdel openlist
sudo groupdel openlist
```

## 获取帮助

- **完整文档**: [README_LINUX_DEPLOYMENT.md](README_LINUX_DEPLOYMENT.md)
- **官方文档**: https://doc.oplist.org
- **GitHub**: https://github.com/OpenListTeam/OpenList
- **讨论区**: https://github.com/OpenListTeam/OpenList/discussions

---

**提示**: 生产环境部署前请务必测试并备份数据！