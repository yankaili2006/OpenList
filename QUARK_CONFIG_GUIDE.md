# 夸克网盘配置指南

## 概述
本文档介绍如何在OpenList中配置夸克网盘存储。

## 配置步骤

### 1. 获取夸克网盘Cookie
1. 访问夸克网盘网页版: https://pan.quark.cn
2. 登录您的夸克网盘账号
3. 按F12打开浏览器开发者工具
4. 切换到Network（网络）标签
5. 刷新页面
6. 在请求列表中找到任意请求（如`file`、`folder`等）
7. 点击该请求，在Headers（标头）中找到`Cookie`字段
8. 复制完整的Cookie值

**Cookie示例格式:**
```
QUTH=xxx; QUTH.sig=xxx; _uc_sso_token=xxx; other_cookie=value
```

### 2. 配置夸克网盘存储

#### 方法一：使用Python脚本配置
```bash
# 运行配置脚本
python3 configure_quark.py

# 或使用非交互式版本（使用示例配置）
python3 configure_quark_noninteractive.py
```

#### 方法二：使用云盘登录管理工具
```bash
python3 cloud_disk_login.py
```
选择选项3（夸克网盘登录），然后输入Cookie。

#### 方法三：手动配置
1. 启动OpenList服务
2. 访问管理界面: http://localhost:5244
3. 登录管理后台
4. 进入"存储"页面
5. 点击"添加"
6. 选择驱动类型: `Quark`
7. 填写配置:
   - 挂载路径: `/quark`（或其他路径）
   - Cookie: 粘贴获取的Cookie
   - 其他选项保持默认

### 3. 配置参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| cookie | 夸克网盘登录Cookie | 必填 |
| root_id | 根目录ID | "0" |
| order_by | 排序方式 | "none" |
| order_direction | 排序方向 | "asc" |
| use_transcoding_address | 使用转码地址 | false |
| only_list_video_file | 仅列出视频文件 | false |

### 4. 启动OpenList服务
```bash
# 给启动脚本添加执行权限
chmod +x start_openlist.sh

# 启动服务
./start_openlist.sh
```

服务将在 http://localhost:5244 运行。

### 5. 验证配置
1. 访问OpenList界面: http://localhost:5244
2. 在文件管理器中查看是否显示夸克网盘
3. 点击夸克网盘挂载路径，查看文件列表

## 故障排除

### 问题1: Cookie无效或过期
- 重新登录夸克网盘获取新的Cookie
- 确保Cookie完整且未过期

### 问题2: 无法访问文件
- 检查网络连接
- 确认夸克网盘账号正常
- 检查Cookie是否包含所有必要的字段

### 问题3: 数据库错误
- 确保OpenList服务已正确启动
- 检查数据目录权限
- 删除`data/data.db`文件重新初始化

### 问题4: 服务无法启动
- 检查openlist二进制文件是否存在
- 确保有执行权限
- 检查端口5244是否被占用

## 高级配置

### 使用真实Cookie替换示例
编辑`configure_quark_noninteractive.py`文件，将`example_cookie`变量替换为真实的Cookie值。

### 多个夸克网盘账号
可以为不同的夸克网盘账号设置不同的挂载路径，如：
- `/quark1`
- `/quark2`
- `/work_quark`

## 注意事项
1. Cookie具有有效期，过期后需要重新获取
2. 不要分享您的Cookie，它包含账号访问权限
3. 建议定期更新Cookie以确保正常访问
4. 夸克网盘API可能有访问频率限制

## 相关文件
- `configure_quark.py` - 交互式配置脚本
- `configure_quark_noninteractive.py` - 非交互式配置脚本
- `cloud_disk_login.py` - 云盘登录管理工具
- `openlist_api_proxy.py` - API代理工具
- `start_openlist.sh` - 服务启动脚本