#!/usr/bin/env python3
"""
查看百度网盘文件列表
由于需要真实的refresh_token和API配置，这里显示模拟数据
"""

import json
import os
from datetime import datetime


def get_baidu_config():
    """从数据库获取百度网盘配置"""
    db_path = "/Users/primihub/github/OpenList/data/data.db"

    if not os.path.exists(db_path):
        print("数据库不存在")
        return None

    try:
        import sqlite3

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT addition FROM x_storages WHERE driver = 'BaiduNetdisk'")
        result = cursor.fetchone()

        conn.close()

        if result:
            return json.loads(result[0])
        else:
            print("数据库中没有百度网盘配置")
            return None

    except Exception as e:
        print(f"读取数据库失败: {e}")
        return None


def show_baidu_info():
    """显示百度网盘信息"""
    print("=== 百度网盘信息 ===")

    config = get_baidu_config()
    if config:
        refresh_token = config.get("refresh_token", "")
        print(f"refresh_token长度: {len(refresh_token)} 字符")
        print(f"API地址: {config.get('api_url_address', '默认')}")
        print(f"下载API: {config.get('download_api', '默认')}")

        # 检查是否是示例token
        if refresh_token == "123.456abc789def0123456789abcdef0123456789abcdef":
            print("\n⚠ 使用的是示例refresh_token")
            print("需要替换为真实的百度网盘refresh_token才能访问实际文件")
            return False
        else:
            print("\n✓ 配置了自定义refresh_token")
            return True
    else:
        print("未找到百度网盘配置")
        return False


def simulate_baidu_files():
    """模拟百度网盘文件列表"""
    print("\n=== 百度网盘模拟文件列表 ===")
    print("由于缺少真实的refresh_token，显示模拟数据")
    print("获取真实refresh_token后可以访问实际文件")

    # 模拟文件数据
    files = [
        {
            "name": "我的文档",
            "type": "folder",
            "size": 0,
            "time": "2024-12-01 10:30:00",
            "items": 15,
        },
        {
            "name": "工作资料",
            "type": "folder",
            "size": 0,
            "time": "2024-12-05 14:20:00",
            "items": 8,
        },
        {
            "name": "个人照片",
            "type": "folder",
            "size": 0,
            "time": "2024-12-10 09:15:00",
            "items": 23,
        },
        {
            "name": "项目报告.pdf",
            "type": "file",
            "size": 5242880,  # 5MB
            "time": "2024-12-15 16:45:00",
            "category": "文档",
        },
        {
            "name": "会议记录.docx",
            "type": "file",
            "size": 2097152,  # 2MB
            "time": "2024-12-16 11:20:00",
            "category": "文档",
        },
        {
            "name": "产品演示.mp4",
            "type": "file",
            "size": 104857600,  # 100MB
            "time": "2024-12-17 15:30:00",
            "category": "视频",
        },
        {
            "name": "数据备份.zip",
            "type": "file",
            "size": 536870912,  # 512MB
            "time": "2024-12-18 20:10:00",
            "category": "压缩包",
        },
        {
            "name": "截图合集",
            "type": "folder",
            "size": 0,
            "time": "2024-12-20 13:45:00",
            "items": 42,
        },
    ]

    print(f"\n共 {len(files)} 个文件/文件夹:")

    total_size = 0
    file_count = 0
    folder_count = 0

    for i, item in enumerate(files, 1):
        if item["type"] == "folder":
            icon = "📁"
            size_str = f"{item['items']} 个项目"
            folder_count += 1
        else:
            icon = "📄"
            # 格式化大小
            size = item["size"]
            if size >= 1024**3:  # GB
                size_str = f"{size / 1024**3:.1f} GB"
            elif size >= 1024**2:  # MB
                size_str = f"{size / 1024**2:.1f} MB"
            elif size >= 1024:  # KB
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size} B"

            total_size += size
            file_count += 1

        print(f"\n{i}. {icon} {item['name']}")
        print(f"   类型: {item['type']}")
        print(f"   大小: {size_str}")
        print(f"   时间: {item['time']}")

        if item["type"] == "file":
            print(f"   分类: {item.get('category', '其他')}")

    # 统计信息
    print("\n" + "=" * 50)
    print("统计信息:")
    print(f"文件夹: {folder_count} 个")
    print(f"文件: {file_count} 个")

    # 格式化总大小
    if total_size >= 1024**3:
        total_str = f"{total_size / 1024**3:.2f} GB"
    elif total_size >= 1024**2:
        total_str = f"{total_size / 1024**2:.2f} MB"
    elif total_size >= 1024:
        total_str = f"{total_size / 1024:.2f} KB"
    else:
        total_str = f"{total_size} B"

    print(f"总大小: {total_str}")

    # 分类统计
    print("\n文件分类:")
    categories = {}
    for item in files:
        if item["type"] == "file":
            category = item.get("category", "其他")
            categories[category] = categories.get(category, 0) + 1

    for category, count in categories.items():
        print(f"  {category}: {count} 个")


def get_refresh_token_guide():
    """获取refresh_token的指南"""
    print("\n=== 获取百度网盘refresh_token指南 ===")
    print("\n方法一：使用第三方工具")
    print("1. 访问: https://alist.nn.ci/tool/baidu")
    print("2. 按照页面指引获取refresh_token")

    print("\n方法二：通过官方API")
    print("1. 注册百度开发者账号")
    print("2. 创建应用获取client_id和client_secret")
    print("3. 使用OAuth2.0授权获取refresh_token")

    print("\n方法三：使用浏览器开发者工具")
    print("1. 登录百度网盘网页版")
    print("2. 按F12打开开发者工具")
    print("3. 在Network标签中查找API请求")
    print("4. 从请求头或响应中提取refresh_token")

    print("\n参考文档:")
    print("- https://alist.nn.ci/zh/guide/drivers/baidu.html")
    print("- https://pan.baidu.com/union/document/entrance")


def main():
    print("=== 百度网盘文件查看工具 ===")
    print("1. 查看百度网盘配置")
    print("2. 查看模拟文件列表")
    print("3. 获取refresh_token指南")
    print("4. 查看所有存储配置")

    # 默认选择2
    choice = "2"

    if choice == "1":
        show_baidu_info()
    elif choice == "2":
        simulate_baidu_files()
    elif choice == "3":
        get_refresh_token_guide()
    elif choice == "4":
        # 导入list_storages函数
        import sqlite3

        db_path = "/Users/primihub/github/OpenList/data/data.db"
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, mount_path, driver, remark FROM x_storages")
            storages = cursor.fetchall()
            conn.close()

            print("\n=== 所有存储配置 ===")
            if storages:
                for storage in storages:
                    print(f"\nID: {storage[0]}")
                    print(f"挂载路径: {storage[1]}")
                    print(f"驱动类型: {storage[2]}")
                    print(f"备注: {storage[3]}")
            else:
                print("没有存储配置")
        else:
            print("数据库不存在")


if __name__ == "__main__":
    main()
