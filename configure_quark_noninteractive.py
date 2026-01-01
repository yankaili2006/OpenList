#!/usr/bin/env python3
"""
非交互式配置夸克网盘存储
使用示例配置
"""

import sqlite3
import json
import os


def configure_quark_example():
    # 数据库路径
    data_dir = "/Users/primihub/github/OpenList/data"
    db_path = os.path.join(data_dir, "data.db")

    # 检查数据库是否存在
    if not os.path.exists(db_path):
        print(f"数据库不存在: {db_path}")
        print("请先启动OpenList服务以创建数据库")

        # 尝试创建数据目录
        os.makedirs(data_dir, exist_ok=True)
        print(f"已创建数据目录: {data_dir}")
        print("现在需要启动OpenList服务来初始化数据库")
        return False

    print("=== 配置夸克网盘 (示例) ===")

    # 示例Cookie - 实际使用时需要替换为真实的Cookie
    # 格式: "QUTH=xxx; QUTH.sig=xxx; _uc_sso_token=xxx; ..."
    example_cookie = "QUTH=example_token_value; QUTH.sig=example_sig_value; _uc_sso_token=example_sso_token"

    mount_path = "/quark"
    remark = "夸克网盘示例配置"

    # 夸克网盘配置
    addition = {
        "cookie": example_cookie,
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
            print("更新现有配置...")
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

            # 解析addition
            addition_data = json.loads(result[3])
            print(f"Cookie长度: {len(addition_data.get('cookie', ''))} 字符")
            print(f"Root ID: {addition_data.get('root_id', '')}")

        conn.close()

        print("\n配置完成!")
        print("注意: 使用的是示例Cookie，需要替换为真实的夸克网盘Cookie")
        print("获取真实Cookie的方法:")
        print("1. 登录 https://pan.quark.cn")
        print("2. 按F12打开开发者工具")
        print("3. 刷新页面")
        print("4. 在Network标签中找到任意请求，复制Request Headers中的Cookie")
        print("\n重启OpenList服务后配置生效")

        return True

    except sqlite3.OperationalError as e:
        print(f"数据库操作错误: {e}")
        print("可能需要先启动OpenList服务初始化数据库")
        return False
    except Exception as e:
        print(f"配置失败: {e}")
        return False


if __name__ == "__main__":
    configure_quark_example()
