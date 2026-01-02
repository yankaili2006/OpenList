#!/usr/bin/env python3
"""
测试百度网盘API
"""

import requests
import json
import time
import sqlite3
import os


def get_baidu_config():
    """从数据库获取百度网盘配置"""
    db_path = "data/data.db"
    if not os.path.exists(db_path):
        return None

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT addition FROM x_storages WHERE driver = 'BaiduNetdisk'")
        result = cursor.fetchone()
        conn.close()

        return json.loads(result[0]) if result else None
    except Exception as e:
        print(f"读取数据库失败: {e}")
        return None


def refresh_access_token(refresh_token, client_id, client_secret):
    """使用refresh_token获取新的access_token"""
    print("尝试刷新access_token...")

    url = "https://openapi.baidu.com/oauth/2.0/token"
    params = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"刷新token状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False)}")

            if "access_token" in data:
                new_access_token = data["access_token"]
                new_refresh_token = data.get("refresh_token", refresh_token)
                expires_in = data.get("expires_in", 2592000)

                print(f"✅ 获取到新的access_token")
                print(f"access_token: {new_access_token[:30]}...")
                print(f"refresh_token: {new_refresh_token[:30]}...")
                print(f"有效期: {expires_in}秒 ({expires_in / 86400:.1f}天)")

                return new_access_token, new_refresh_token
            else:
                print(f"❌ 响应中没有access_token: {data}")
                return None, None
        else:
            print(f"❌ 刷新token失败: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None, None


def list_files(access_token, dir="/"):
    """列出百度网盘文件"""
    print(f"\n尝试列出目录: {dir}")

    url = "https://pan.baidu.com/rest/2.0/xpan/file"
    params = {
        "method": "list",
        "access_token": access_token,
        "dir": dir,
        "order": "name",
        "desc": "0",
        "start": "0",
        "limit": "100",
        "web": "web",
        "folder": "0",
        "showempty": "0",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"列出文件状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if "list" in data:
                files = data["list"]
                print(f"✅ 找到 {len(files)} 个文件/文件夹")

                for i, file in enumerate(files[:10]):  # 只显示前10个
                    is_dir = file.get("isdir", 0) == 1
                    size = file.get("size", 0)
                    if size > 1024 * 1024 * 1024:
                        size_str = f"{size / (1024 * 1024 * 1024):.2f}GB"
                    elif size > 1024 * 1024:
                        size_str = f"{size / (1024 * 1024):.2f}MB"
                    elif size > 1024:
                        size_str = f"{size / 1024:.2f}KB"
                    else:
                        size_str = f"{size}B"

                    print(
                        f"  {i + 1:2d}. {'📁' if is_dir else '📄'} {file.get('server_filename', '未知')}"
                    )
                    print(f"      大小: {size_str}, 路径: {file.get('path', '未知')}")

                if len(files) > 10:
                    print(f"  ... 还有 {len(files) - 10} 个文件未显示")

                return files
            else:
                print(f"❌ 响应中没有文件列表: {data}")
                return []
        else:
            print(f"❌ 列出文件失败: {response.text}")
            return []
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return []


def get_quota_info(access_token):
    """获取网盘容量信息"""
    print("\n获取网盘容量信息...")

    url = "https://pan.baidu.com/api/quota"
    params = {"access_token": access_token, "checkfree": "1", "checkexpire": "1"}

    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"容量查询状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False)}")

            if "total" in data and "used" in data:
                total = data["total"]
                used = data["used"]
                free = total - used

                print(f"✅ 容量信息:")
                print(f"   总容量: {total / (1024**3):.2f}GB")
                print(f"   已使用: {used / (1024**3):.2f}GB")
                print(f"   剩余空间: {free / (1024**3):.2f}GB")
                print(f"   使用率: {used / total * 100:.1f}%")

                if "expire" in data:
                    expire_time = data["expire"]
                    if expire_time > 0:
                        from datetime import datetime

                        expire_date = datetime.fromtimestamp(expire_time)
                        print(f"   会员到期: {expire_date}")

                return data
            else:
                print(f"❌ 响应中没有容量信息")
                return None
        else:
            print(f"❌ 容量查询失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None


def main():
    print("=== 百度网盘API测试 ===")

    # 获取配置
    config = get_baidu_config()
    if not config:
        print("❌ 没有找到百度网盘配置")
        return

    print("📋 当前配置:")
    refresh_token = config.get("refresh_token", "")
    client_id = config.get("client_id", "")
    client_secret = config.get("client_secret", "")

    print(f"refresh_token: {refresh_token[:30]}... (长度: {len(refresh_token)})")
    print(f"client_id: {client_id}")
    print(f"client_secret: {'*' * len(client_secret) if client_secret else '空'}")

    if not client_id or not client_secret:
        print("❌ 缺少client_id或client_secret，无法调用API")
        print("请从百度开发者平台获取并更新配置")
        return

    if not refresh_token:
        print("❌ 缺少refresh_token")
        return

    # 刷新access_token
    access_token, new_refresh_token = refresh_access_token(
        refresh_token, client_id, client_secret
    )

    if not access_token:
        print("❌ 无法获取access_token，测试终止")
        return

    # 获取容量信息
    quota_info = get_quota_info(access_token)

    # 列出根目录文件
    files = list_files(access_token, "/")

    # 如果有新的refresh_token，更新数据库
    if new_refresh_token and new_refresh_token != refresh_token:
        print(f"\n🔄 检测到新的refresh_token，更新数据库...")
        try:
            config["refresh_token"] = new_refresh_token
            new_config_json = json.dumps(config)

            conn = sqlite3.connect("data/data.db")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE x_storages SET addition = ? WHERE driver = 'BaiduNetdisk'",
                (new_config_json,),
            )
            conn.commit()
            conn.close()

            print(f"✅ 数据库已更新")
            print(f"新的refresh_token: {new_refresh_token[:30]}...")
        except Exception as e:
            print(f"❌ 更新数据库失败: {e}")

    print("\n✅ 测试完成")


if __name__ == "__main__":
    main()
