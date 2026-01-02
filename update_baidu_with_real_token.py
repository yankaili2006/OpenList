#!/usr/bin/env python3
"""
使用真实的百度网盘refresh_token更新配置
"""

import sqlite3
import json
import os


def update_baidu_with_real_token():
    # 读取真实的refresh_token
    token_file = "baidu_real_refresh_token.txt"
    if not os.path.exists(token_file):
        print(f"文件不存在: {token_file}")
        return False

    with open(token_file, "r", encoding="utf-8") as f:
        refresh_token = f.read().strip()

    print("=== 使用真实refresh_token更新百度网盘配置 ===")
    print(f"refresh_token长度: {len(refresh_token)} 字符")
    print(f"token预览: {refresh_token[:50]}...")

    # 数据库路径
    data_dir = "/Users/primihub/github/OpenList/data"
    db_path = os.path.join(data_dir, "data.db")

    if not os.path.exists(db_path):
        print(f"数据库不存在: {db_path}")
        return False

    mount_path = "/baidu"
    remark = "百度网盘真实配置"

    # 百度网盘完整配置
    addition = {
        "refresh_token": refresh_token,
        "root_path": "/",
        "order_by": "name",
        "order_direction": "asc",
        "download_api": "official",
        "use_online_api": True,
        "api_url_address": "https://api.oplist.org/baiduyun/renewapi",
        "client_id": "iYCeC9g08h5vuP9UqvPHKKSVrKFXGa1v",  # 示例client_id，可能需要替换
        "client_secret": "jXiFMOPVPCWlO2M5CwWQzffpNPaGTRBG",  # 示例client_secret，可能需要替换
        "custom_crack_ua": "netdisk",
        "upload_thread": "3",
        "upload_timeout": 60,
        "upload_api": "https://d.pcs.baidu.com",
        "use_dynamic_upload_api": True,
        "custom_upload_part_size": 0,
        "low_bandwith_upload_mode": False,
        "only_list_video_file": False,
    }

    # 连接数据库
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 检查是否已存在百度网盘配置
        cursor.execute("SELECT id FROM x_storages WHERE driver = 'BaiduNetdisk'")
        existing = cursor.fetchone()

        if existing:
            print(f"百度网盘配置已存在，ID: {existing[0]}")
            print("更新现有配置...")
            cursor.execute(
                """
                UPDATE x_storages 
                SET addition = ?, remark = ?
                WHERE driver = 'BaiduNetdisk'
            """,
                (json.dumps(addition), remark),
            )
            print("✅ 已更新百度网盘配置")
        else:
            # 添加新的存储
            cursor.execute(
                """
                INSERT INTO x_storages 
                (mount_path, driver, addition, status, disabled, remark) 
                VALUES (?, ?, ?, 'work', 0, ?)
            """,
                (mount_path, "BaiduNetdisk", json.dumps(addition), remark),
            )
            print(f"✅ 已添加百度网盘配置，挂载路径: {mount_path}")

        conn.commit()

        # 验证配置
        cursor.execute("""
            SELECT id, mount_path, driver, addition, remark 
            FROM x_storages 
            WHERE driver = 'BaiduNetdisk'
        """)

        result = cursor.fetchone()
        if result:
            print("\n=== 配置验证 ===")
            print(f"ID: {result[0]}")
            print(f"挂载路径: {result[1]}")
            print(f"驱动类型: {result[2]}")
            print(f"备注: {result[4]}")

            addition_data = json.loads(result[3])
            token = addition_data.get("refresh_token", "")
            print(f"refresh_token长度: {len(token)} 字符")
            print(f"client_id: {addition_data.get('client_id', '未设置')}")
            print(f"client_secret: {'*' * len(addition_data.get('client_secret', ''))}")
            print(f"API地址: {addition_data.get('api_url_address', '')}")

        conn.close()

        print("\n" + "=" * 50)
        print("配置更新完成!")
        print("=" * 50)
        print(f"挂载路径: {mount_path}")
        print(f"驱动类型: BaiduNetdisk")
        print(f"备注: {remark}")
        print(f"refresh_token已配置")

        # 测试配置
        print("\n下一步:")
        print("1. 启动OpenList服务: ./start_openlist.sh")
        print("2. 访问 http://localhost:5244")
        print("3. 登录管理后台")
        print("4. 查看百度网盘文件")

        return True

    except Exception as e:
        print(f"配置失败: {e}")
        return False


def test_baidu_api():
    """测试百度网盘API（需要client_id和client_secret）"""
    print("\n=== 测试百度网盘API ===")

    # 读取配置
    db_path = "/Users/primihub/github/OpenList/data/data.db"
    if not os.path.exists(db_path):
        print("数据库不存在")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT addition FROM x_storages WHERE driver = 'BaiduNetdisk'")
        result = cursor.fetchone()
        conn.close()

        if not result:
            print("没有百度网盘配置")
            return

        config = json.loads(result[0])
        refresh_token = config.get("refresh_token", "")
        client_id = config.get("client_id", "")
        client_secret = config.get("client_secret", "")

        if not client_id or not client_secret:
            print("⚠ 缺少client_id或client_secret")
            print("需要完整的OAuth2.0配置才能调用百度API")
            print("\n获取client_id和client_secret:")
            print("1. 注册百度开发者: https://developer.baidu.com/")
            print("2. 创建应用")
            print("3. 获取API Key和Secret Key")
            return

        print(f"client_id: {client_id}")
        print(f"client_secret: {'*' * len(client_secret)}")
        print(f"refresh_token长度: {len(refresh_token)} 字符")

        # 这里可以添加实际的API测试代码
        # 需要实现OAuth2.0的token刷新和API调用

    except Exception as e:
        print(f"测试失败: {e}")


def main():
    print("1. 更新百度网盘配置")
    print("2. 测试API配置")

    # 默认选择1
    choice = "1"

    if choice == "1":
        update_baidu_with_real_token()
    elif choice == "2":
        test_baidu_api()


if __name__ == "__main__":
    main()
