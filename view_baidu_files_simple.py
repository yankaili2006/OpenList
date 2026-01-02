#!/usr/bin/env python3
"""
查看百度网盘文件 - 模拟和真实测试结合
"""

import json
import os
import requests
import time


def get_baidu_config():
    """获取百度网盘配置"""
    db_path = "/Users/primihub/github/OpenList/data/data.db"

    if not os.path.exists(db_path):
        return None

    try:
        import sqlite3

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT addition FROM x_storages WHERE driver = 'BaiduNetdisk'")
        result = cursor.fetchone()
        conn.close()

        return json.loads(result[0]) if result else None
    except:
        return None


def simulate_baidu_structure():
    """模拟百度网盘文件夹结构"""
    print("=== 百度网盘模拟文件夹结构 ===")
    print("由于缺少完整的OAuth2.0配置，显示模拟数据")
    print("获取client_id和client_secret后可以访问真实数据")

    # 典型的百度网盘文件夹结构
    folder_structure = {
        "根目录": {
            "我的文档": ["工作报告.pdf", "学习资料.zip", "个人简历.docx"],
            "图片": ["旅行照片/", "家庭相册/", "工作截图.png"],
            "视频": ["电影/", "电视剧/", "自制视频.mp4"],
            "音乐": ["流行歌曲.mp3", "古典音乐.flac", "播客.m4a"],
            "工作资料": ["项目文档/", "会议记录/", "客户资料.xlsx"],
            "下载": ["软件安装包.exe", "文档模板.zip", "临时文件.tmp"],
            "备份": ["系统备份/", "数据备份/", "照片备份/"],
        }
    }

    print("\n📁 百度网盘典型文件夹结构:")
    for main_folder, subfolders in folder_structure.items():
        print(f"\n{main_folder}:")
        if isinstance(subfolders, dict):
            for folder, items in subfolders.items():
                print(f"  ├── 📁 {folder}")
                if items:
                    for item in items[:3]:  # 只显示前3个
                        print(f"  │   ├── 📄 {item}")
                    if len(items) > 3:
                        print(f"  │   └── ... 还有 {len(items) - 3} 个文件")
        else:
            for item in subfolders[:5]:  # 只显示前5个
                print(f"  ├── 📄 {item}")
            if len(subfolders) > 5:
                print(f"  └── ... 还有 {len(subfolders) - 5} 个文件")

    # 文件统计
    print("\n📊 模拟统计信息:")
    print("总文件夹数: 8个")
    print("总文件数: ~50个")
    print("估计占用空间: ~15GB")
    print("最近更新时间: 2024-12-28")


def get_baidu_developer_info():
    """获取百度开发者配置信息"""
    print("\n=== 获取百度API配置 ===")
    print("\n要访问真实的百度网盘文件，需要:")
    print("1. client_id (API Key)")
    print("2. client_secret (Secret Key)")
    print("3. refresh_token (已获取)")

    print("\n📋 获取步骤:")
    print("1. 访问: https://developer.baidu.com/")
    print("2. 注册/登录百度开发者账号")
    print("3. 创建新应用")
    print("4. 选择'服务端应用'类型")
    print("5. 获取API Key和Secret Key")

    print("\n⚙️ 应用配置:")
    print("- 应用名称: OpenList-Baidu (自定义)")
    print("- 应用类型: 服务端应用")
    print("- 回调地址: http://localhost:8080")
    print("- 权限范围: basic,netdisk")

    print("\n🔑 配置示例:")
    print("client_id: iYCeC9g08h5vuP9UqvPHKKSVrKFXGa1v")
    print("client_secret: jXiFMOPVPCWlO2M5CwWQzffpNPaGTRBG")
    print("refresh_token: [您已获取的token]")


def update_config_with_credentials():
    """更新配置添加client_id和client_secret"""
    print("\n=== 更新百度网盘配置 ===")

    # 示例配置（需要替换为真实的）
    sample_config = {
        "client_id": "iYCeC9g08h5vuP9UqvPHKKSVrKFXGa1v",
        "client_secret": "jXiFMOPVPCWlO2M5CwWQzffpNPaGTRBG",
        "refresh_token": "[PlpyR1kwTFE4eEN-Z0Ywc2RNdC00fk95alJUbDIyZlNONmVvSmFUang2bGI0MHRwSVFBQUFBJCQAAAAAAAAAAAEAAACxqJs9eWFua2FpbGkyMDA2AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFtWJGlbViRpQ||a8da34e452ccecc754c2d1243085a5d8dd4a39be29b41db19d672d32a5aa57dc",
    }

    print("请将以下配置添加到百度网盘设置中:")
    print(f"client_id: {sample_config['client_id']}")
    print(f"client_secret: {sample_config['client_secret']}")
    print(f"refresh_token: {sample_config['refresh_token'][:50]}...")

    print("\n💡 提示: 上述client_id和client_secret是示例")
    print("需要替换为您从百度开发者平台获取的真实值")


def test_baidu_api_simple():
    """简单测试百度API（需要完整配置）"""
    print("\n=== 测试百度网盘API ===")

    config = get_baidu_config()
    if not config:
        print("没有百度网盘配置")
        return

    refresh_token = config.get("refresh_token", "")
    client_id = config.get("client_id", "")
    client_secret = config.get("client_secret", "")

    if not client_id or not client_secret:
        print("❌ 缺少client_id或client_secret")
        print("无法调用百度API")
        get_baidu_developer_info()
        return

    print(f"client_id: {client_id}")
    print(f"client_secret: {'*' * len(client_secret)}")
    print(f"refresh_token长度: {len(refresh_token)} 字符")

    # 尝试调用API（这里只是示例，实际需要OAuth2.0流程）
    print("\n尝试调用百度API...")
    print("需要实现OAuth2.0的token刷新流程")
    print("1. 使用refresh_token获取access_token")
    print("2. 使用access_token调用文件列表API")
    print("3. 解析返回的文件数据")


def show_current_storages():
    """显示所有存储配置"""
    print("\n=== 当前所有存储配置 ===")

    db_path = "/Users/primihub/github/OpenList/data/data.db"
    if not os.path.exists(db_path):
        print("数据库不存在")
        return

    try:
        import sqlite3

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, mount_path, driver, remark FROM x_storages")
        storages = cursor.fetchall()
        conn.close()

        if storages:
            for storage in storages:
                print(f"\nID: {storage[0]}")
                print(f"挂载路径: {storage[1]}")
                print(f"驱动类型: {storage[2]}")
                print(f"备注: {storage[3]}")
        else:
            print("没有存储配置")
    except Exception as e:
        print(f"查询失败: {e}")


def main():
    print("=== 百度网盘文件查看工具 ===")
    print("1. 查看模拟文件夹结构")
    print("2. 获取百度API配置指南")
    print("3. 更新配置添加凭证")
    print("4. 测试百度API")
    print("5. 查看所有存储配置")

    # 默认选择1
    choice = "1"

    if choice == "1":
        simulate_baidu_structure()
    elif choice == "2":
        get_baidu_developer_info()
    elif choice == "3":
        update_config_with_credentials()
    elif choice == "4":
        test_baidu_api_simple()
    elif choice == "5":
        show_current_storages()


if __name__ == "__main__":
    main()
