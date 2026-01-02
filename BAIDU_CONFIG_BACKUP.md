# 百度网盘配置备份文档

## 📋 配置信息

### 🔑 OAuth2.0 凭证
| 参数 | 值 | 说明 |
|------|-----|------|
| **AppID** | `121688344` | 应用ID |
| **AppKey** | `H3nQzpy7fzdhQxJTdU2IdF3uPGhHhh8c` | 应用密钥 |
| **Secretkey** | `3abco39cmTlgmoU1C2ymGAC9iWsaXlKW` | 密钥 |
| **Signkey** | `*TLfNRcpKORv$MktPlFY13+SG5$pJtfZ` | 签名密钥 |

### 🔐 Refresh Token
```
[PlpyR1kwTFE4eEN-Z0Ywc2RNdC00fk95alJUbDIyZlNONmVvSmFUang2bGI0MHRwSVFBQUFBJCQAAAAAAAAAAAEAAACxqJs9eWFua2FpbGkyMDA2AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFtWJGlbViRpQ||a8da34e452ccecc754c2d1243085a5d8dd4a39be29b41db19d672d32a5aa57dc
```

**长度**: 48字符

## ⚙️ OpenList 配置

### JSON 配置格式
```json
{
  "refresh_token": "[PlpyR1kwTFE4eEN-Z0Ywc2RNdC00fk95alJUbDIyZlNONmVvSmFUang2bGI0MHRwSVFBQUFBJCQAAAAAAAAAAAEAAACxqJs9eWFua2FpbGkyMDA2AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFtWJGlbViRpQ||a8da34e452ccecc754c2d1243085a5d8dd4a39be29b41db19d672d32a5aa57dc",
  "client_id": "121688344",
  "client_secret": "H3nQzpy7fzdhQxJTdU2IdF3uPGhHhh8c",
  "root_path": "/",
  "order_by": "name",
  "order_direction": "asc",
  "download_api": "official",
  "use_online_api": true,
  "api_url_address": "https://api.oplist.org/baiduyun/renewapi",
  "custom_crack_ua": "netdisk",
  "upload_thread": "3",
  "upload_timeout": 60,
  "upload_api": "https://d.pcs.baidu.com",
  "use_dynamic_upload_api": true,
  "custom_upload_part_size": 0,
  "low_bandwith_upload_mode": false,
  "only_list_video_file": false
}
```

### 数据库存储信息
- **挂载路径**: `/baidu`
- **驱动类型**: `BaiduNetdisk`
- **备注**: `百度网盘完整配置`
- **状态**: `work` (正常工作)
- **禁用**: `false`

## 🔧 使用方法

### 1. 手动配置
```bash
# 使用Python脚本更新配置
python3 update_baidu_with_real_token.py
```

### 2. 直接操作数据库
```sql
-- 查看百度网盘配置
SELECT id, mount_path, driver, remark FROM x_storages WHERE driver = 'BaiduNetdisk';

-- 查看详细配置
SELECT addition FROM x_storages WHERE driver = 'BaiduNetdisk';
```

### 3. 配置文件位置
- **数据库**: `/Users/primihub/github/OpenList/data/data.db`
- **备份文件**: `baidu_real_refresh_token.txt`
- **OAuth配置**: `baidu_oauth_config.txt`

## 🚀 测试方法

### API 测试
```python
import requests

# 使用refresh_token获取access_token
params = {
    'grant_type': 'refresh_token',
    'refresh_token': 'YOUR_REFRESH_TOKEN',
    'client_id': '121688344',
    'client_secret': 'H3nQzpy7fzdhQxJTdU2IdF3uPGhHhh8c'
}

response = requests.get('https://openapi.baidu.com/oauth/2.0/token', params=params)
```

### 文件列表测试
```python
# 获取文件列表
headers = {
    'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
    'Content-Type': 'application/json'
}

response = requests.get('https://pan.baidu.com/rest/2.0/xpan/file', params={
    'method': 'list',
    'dir': '/',
    'order': 'name',
    'start': 0,
    'limit': 100,
    'web': 1
}, headers=headers)
```

## 📝 注意事项

### 安全性
1. **不要公开分享**这些凭证
2. **定期检查**token是否有效
3. **备份配置**到安全位置

### 有效期
- **refresh_token**: 通常几个月到一年
- **access_token**: 通常30天（需要refresh_token刷新）

### 更新方法
1. 如果token失效，重新获取refresh_token
2. 更新数据库中的配置
3. 重启OpenList服务

## 🔄 恢复步骤

如果配置丢失，按以下步骤恢复：

1. **重新获取凭证**（如果已失效）：
   ```bash
   # 访问百度开发者平台
   open https://developer.baidu.com/
   ```

2. **更新配置**：
   ```bash
   # 编辑配置文件
   vim baidu_oauth_config.txt
   
   # 运行更新脚本
   python3 update_baidu_with_real_token.py
   ```

3. **重启服务**：
   ```bash
   ./start_openlist.sh
   ```

## 📞 支持信息

### 相关链接
- **百度开发者平台**: https://developer.baidu.com/
- **OpenList文档**: https://github.com/OpenListTeam/OpenList
- **百度网盘API文档**: https://pan.baidu.com/union/document/

### 问题排查
1. **403错误**: 检查client_id和client_secret
2. **401错误**: refresh_token可能已过期
3. **404错误**: API地址可能已变更

---

**最后更新**: 2025-01-01  
**配置状态**: ✅ 完整有效  
**备份位置**: 本文件 + 数据库 + 文本文件备份