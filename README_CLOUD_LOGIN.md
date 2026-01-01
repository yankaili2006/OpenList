# 云盘平台自动登录脚本

本脚本提供简化的方式配置多个云盘平台的登录信息，支持百度网盘、阿里云盘、夸克网盘等。

## 脚本说明

### 1. 交互式配置脚本 (`cloud_disk_login.py`)

功能全面的交互式配置工具：

```bash
python3 cloud_disk_login.py
```

**特点：**
- 菜单驱动的交互界面
- 支持单独配置每个平台
- 查看和管理现有配置
- 生成OpenList兼容的存储配置
- 配置持久化保存

### 2. 批量配置脚本 (`batch_cloud_login.py`)

简化的一次性批量配置工具：

```bash
python3 batch_cloud_login.py
```

**特点：**
- 一次性配置所有平台
- 极简操作流程
- 自动生成OpenList配置
- 适合快速部署

## 支持的云盘平台

| 平台 | 所需凭证 | 获取方式 |
|------|----------|----------|
| 百度网盘 | refresh_token | 参考官方API文档或使用第三方工具 |
| 阿里云盘 | refresh_token | 使用官方APP扫码或第三方工具 |
| 夸克网盘 | cookie | 登录网页版后在开发者工具中复制 |

## 使用方法

### 快速开始

1. **运行批量配置脚本**
   ```bash
   python3 batch_cloud_login.py
   ```

2. **按提示输入各平台的登录凭证**
   - 百度网盘: refresh_token
   - 阿里云盘: refresh_token  
   - 夸克网盘: cookie

3. **生成配置文件**
   - `cloud_disk_config.json`: 原始配置
   - `openlist_storages.json`: OpenList存储配置

4. **导入到OpenList**
   - 将 `openlist_storages.json` 导入到OpenList
   - 启动OpenList服务
   - 通过Web界面管理云盘文件

### 详细配置

如需更详细的配置管理，使用交互式脚本：

```bash
python3 cloud_disk_login.py
```

## 文件说明

- `cloud_disk_config.json`: 保存云盘登录配置
- `openlist_storages.json`: OpenList存储配置文件
- `cloud_disk_login.py`: 交互式配置脚本
- `batch_cloud_login.py`: 批量配置脚本

## 注意事项

1. **凭证安全**: 配置文件包含敏感信息，请妥善保管
2. **凭证有效期**: refresh_token和cookie都有有效期，过期需要重新获取
3. **平台限制**: 各平台API可能有调用频率限制
4. **网络要求**: 需要能够访问各云盘平台的API服务器

## 故障排除

- **凭证无效**: 检查凭证是否正确，是否已过期
- **网络问题**: 检查网络连接，确认可以访问云盘API
- **配置错误**: 验证生成的JSON配置文件格式是否正确

## 扩展支持

如需支持更多云盘平台，可以参考现有驱动实现，添加对应的登录逻辑和配置生成。