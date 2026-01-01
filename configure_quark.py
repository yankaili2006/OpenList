#!/usr/bin/env python3
"""
配置夸克网盘存储
"""

import sqlite3
import json
import os


def configure_quark():
    # 数据库路径
    data_dir = "/Users/primihub/github/OpenList/data"
    db_path = os.path.join(data_dir, "data.db")

    # 检查数据库是否存在
    if not os.path.exists(db_path):
        print(f"数据库不存在: {db_path}")
        print("请先启动OpenList服务以创建数据库")
        return False

    print("=== 配置夸克网盘 ===")
    print("\n夸克网盘配置说明:")
    print("1. 登录夸克网盘网页版 (https://pan.quark.cn)")
    print("2. 按F12打开开发者工具")
    print("3. 切换到Network标签")
    print("4. 刷新页面")
    print("5. 找到任意请求，复制Cookie值")
    print("6. Cookie格式类似: 'cookie_name1=cookie_value1; cookie_name2=cookie_value2'")

    cookie = input("\n请输入夸克网盘Cookie: ").strip()
    if not cookie:
        print("Cookie不能为空")
        return False

    mount_path = input("请输入挂载路径 (默认: /quark): ").strip()
    if not mount_path:
        mount_path = "/quark"

    remark = input("请输入备注 (可选): ").strip()

    # 夸克网盘配置
    addition = {
        "cookie": cookie,
        "root_id": "0",
        "order_by": "none",
        "order_direction": "asc",
        "use_transcoding_address": False,
        "only_list_video_file": False,
        "addition_version": 0,
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
            update = input("是否更新现有配置? (y/n): ").strip().lower()
            if update == "y":
                cursor.execute(
                    """
                    UPDATE x_storages 
                    SET driver = ?, addition = ?, remark = ?
                    WHERE mount_path = ?
                """,
                    ("Quark", json.dumps(addition), remark, mount_path),
                )
                print(f"已更新夸克网盘配置，挂载路径: {mount_path}")
            else:
                print("配置取消")
                conn.close()
                return False
        else:
            # 添加新的存储
            cursor.execute(
                """
                INSERT INTO x_storages 
                (mount_path, driver, addition, status, disabled, remark) 
                VALUES (?, ?, ?, 'work', 0, ?)
            """,
                (mount_path, "Quark", json.dumps(addition), remark),
            )
            print(f"已添加夸克网盘配置，挂载路径: {mount_path}")

        conn.commit()
        conn.close()

        print("\n配置完成!")
        print(f"挂载路径: {mount_path}")
        print(f"驱动类型: Quark")
        print(f"备注: {remark if remark else '无'}")
        print("\n重启OpenList服务后配置生效")

        return True

    except Exception as e:
        print(f"配置失败: {e}")
        return False


if __name__ == "__main__":
    configure_quark()
