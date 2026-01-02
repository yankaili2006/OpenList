#!/usr/bin/env python3
"""
百度网盘简单配置工具
"""

import sqlite3
import json
import os


def configure_baidu():
    print("=== 配置百度网盘 ===")

    # 数据库路径
    data_dir = "/Users/primihub/github/OpenList/data"
    db_path = os.path.join(data_dir, "data.db")

    if not os.path.exists(db_path):
        print(f"数据库不存在: {db_path}")
        print("请先启动OpenList服务以创建数据库")
        os.makedirs(data_dir, exist_ok=True)
        print(f"已创建数据目录: {data_dir}")
        return False

    print("\n百度网盘配置说明:")
    print("需要获取 refresh_token，可以通过以下方式:")
    print("1. 使用第三方工具获取")
    print("2. 通过百度官方API申请")
    print("3. 参考: https://alist.nn.ci/zh/guide/drivers/baidu.html")

    # 使用示例refresh_token
    example_refresh_token = "123.456abc789def0123456789abcdef0123456789abcdef"

    print(f"\n示例refresh_token格式: {example_refresh_token}")
    print("长度通常为 40-50 个字符")

    # 在实际使用中，这里应该让用户输入
    # refresh_token = input("请输入百度网盘refresh_token: ").strip()
    # 这里使用示例值
    refresh_token = example_refresh_token

    mount_path = "/baidu"
    remark = "百度网盘示例配置"

    # 百度网盘配置
    addition = {
        "refresh_token": refresh_token,
        "root_path": "/",
        "order_by": "name",
        "order_direction": "asc",
        "download_api": "official",
        "use_online_api": True,
        "api_url_address": "https://api.oplist.org/baiduyun/renewapi",
        "client_id": "",
        "client_secret": "",
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

        # 检查是否已存在相同挂载路径
        cursor.execute("SELECT id FROM x_storages WHERE mount_path = ?", (mount_path,))
        existing = cursor.fetchone()

        if existing:
            print(f"挂载路径 '{mount_path}' 已存在，ID: {existing[0]}")
            print("更新现有配置...")
            cursor.execute(
                """
                UPDATE x_storages 
                SET driver = ?, addition = ?, remark = ?
                WHERE mount_path = ?
            """,
                ("BaiduNetdisk", json.dumps(addition), remark, mount_path),
            )
            print(f"已更新百度网盘配置，挂载路径: {mount_path}")
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
            print(f"已添加百度网盘配置，挂载路径: {mount_path}")

        conn.commit()

        # 验证配置
        cursor.execute(
            """
            SELECT id, mount_path, driver, addition, remark 
            FROM x_storages 
            WHERE mount_path = ?
        """,
            (mount_path,),
        )

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
            print(f"Root Path: {addition_data.get('root_path', '')}")

        conn.close()

        print("\n配置完成!")
        print(f"挂载路径: {mount_path}")
        print(f"驱动类型: BaiduNetdisk")
        print(f"备注: {remark}")

        print("\n注意: 使用的是示例refresh_token")
        print("需要替换为真实的百度网盘refresh_token才能正常工作")

        return True

    except Exception as e:
        print(f"配置失败: {e}")
        return False


def list_storages():
    """列出所有存储配置"""
    print("\n=== 当前存储配置 ===")

    db_path = "/Users/primihub/github/OpenList/data/data.db"
    if not os.path.exists(db_path):
        print("数据库不存在")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, mount_path, driver, remark FROM x_storages")
        storages = cursor.fetchall()

        if storages:
            print(f"共有 {len(storages)} 个存储配置:")
            for storage in storages:
                print(f"\nID: {storage[0]}")
                print(f"挂载路径: {storage[1]}")
                print(f"驱动类型: {storage[2]}")
                print(f"备注: {storage[3]}")
        else:
            print("没有存储配置")

        conn.close()

    except Exception as e:
        print(f"查询失败: {e}")


if __name__ == "__main__":
    print("1. 配置百度网盘")
    print("2. 查看当前存储配置")

    # 默认选择1
    choice = "1"

    if choice == "1":
        configure_baidu()
    elif choice == "2":
        list_storages()
