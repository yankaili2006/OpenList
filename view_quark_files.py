#!/usr/bin/env python3
"""
查看夸克网盘文件列表
使用Cookie直接调用夸克网盘API
"""

import requests
import json
import sqlite3
import os
from datetime import datetime


def get_quark_config_from_db():
    """从数据库获取夸克网盘配置"""
    db_path = "/Users/primihub/github/OpenList/data/data.db"

    if not os.path.exists(db_path):
        print(f"数据库不存在: {db_path}")
        return None

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT addition FROM x_storages WHERE driver = 'Quark'")
        result = cursor.fetchone()

        conn.close()

        if result:
            return json.loads(result[0])
        else:
            print("数据库中没有夸克网盘配置")
            return None

    except Exception as e:
        print(f"读取数据库失败: {e}")
        return None


def get_quark_files(cookie, root_id="0", page=1, size=100):
    """获取夸克网盘文件列表"""

    # 夸克网盘API配置
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) quark-cloud-drive/2.5.20 Chrome/100.0.4896.160 Electron/18.3.5.4-b478491100 Safari/537.36 Channel/pckk_other_ch",
        "Referer": "https://pan.quark.cn",
        "Cookie": cookie,
        "Content-Type": "application/json",
        "Origin": "https://pan.quark.cn",
    }

    # API端点
    api_url = "https://drive.quark.cn/1/clouddrive/file/sort"

    # 请求参数
    payload = {
        "pr": "ucpro",
        "fr": "pc",
        "uc_param_str": "",
        "__dt": int(datetime.now().timestamp() * 1000),
        "__t": int(datetime.now().timestamp() * 1000),
        "pdir_fid": root_id,
        "_page": page,
        "_size": size,
        "_fetch_total": 1,
        "_fetch_sub_dirs": 0,
        "_sort": "file_type",
        "_order": "asc",
        "force": 0,
        "web": 1,
    }

    print(f"请求夸克网盘API: {api_url}")
    print(f"根目录ID: {root_id}")
    print(f"页码: {page}, 每页大小: {size}")

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)

        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # 检查响应结构
            if data.get("status") == 200:
                print("✓ API请求成功")

                # 解析文件列表
                file_list = data.get("data", {}).get("list", [])
                metadata = data.get("metadata", {})

                total = metadata.get("_total", 0)
                count = metadata.get("_count", 0)
                page_num = metadata.get("_page", 1)
                size_num = metadata.get("_size", 100)

                print(f"\n=== 文件列表 (第{page_num}页，共{total}个文件) ===")
                print(f"本页显示: {count} 个文件/文件夹")

                if file_list:
                    for i, file_item in enumerate(file_list, 1):
                        file_name = file_item.get("file_name", "未知")
                        fid = file_item.get("fid", "")
                        is_file = file_item.get("file", True)
                        size_bytes = file_item.get("size", 0)
                        updated_at = file_item.get("updated_at", 0)

                        # 格式化文件大小
                        if size_bytes >= 1024**3:  # GB
                            size_str = f"{size_bytes / 1024**3:.2f} GB"
                        elif size_bytes >= 1024**2:  # MB
                            size_str = f"{size_bytes / 1024**2:.2f} MB"
                        elif size_bytes >= 1024:  # KB
                            size_str = f"{size_bytes / 1024:.2f} KB"
                        else:
                            size_str = f"{size_bytes} B"

                        # 格式化时间
                        if updated_at:
                            dt = datetime.fromtimestamp(updated_at / 1000)
                            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            time_str = "未知时间"

                        file_type = "📄 文件" if is_file else "📁 文件夹"

                        print(f"\n{i}. {file_name}")
                        print(f"   {file_type}")
                        print(f"   ID: {fid}")
                        print(f"   大小: {size_str}")
                        print(f"   修改时间: {time_str}")

                        # 显示前5个文件的详细信息
                        if i <= 5:
                            print(
                                f"   原始数据: {json.dumps(file_item, ensure_ascii=False)[:100]}..."
                            )

                else:
                    print("当前目录为空")

                # 显示分页信息
                if total > size_num:
                    total_pages = (total + size_num - 1) // size_num
                    print(f"\n分页信息: 共 {total} 个项目，{total_pages} 页")
                    print(f"当前第 {page_num} 页，每页 {size_num} 项")

                return data

            else:
                print(f"API返回错误: {data.get('message', '未知错误')}")
                print(f"错误代码: {data.get('code', '未知')}")
                return None

        elif response.status_code == 401:
            print("✗ 认证失败，Cookie可能无效或过期")
            return None
        elif response.status_code == 403:
            print("✗ 访问被拒绝，可能需要更新Cookie")
            return None
        else:
            print(f"HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text[:200]}...")
            return None

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        try:
            print(f"响应内容: {response.text[:200]}...")
        except:
            print("无法获取响应内容")
        return None


def get_quark_capacity(cookie):
    """获取夸克网盘容量信息"""

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) quark-cloud-drive/2.5.20 Chrome/100.0.4896.160 Electron/18.3.5.4-b478491100 Safari/537.36 Channel/pckk_other_ch",
        "Referer": "https://pan.quark.cn",
        "Cookie": cookie,
        "Content-Type": "application/json",
    }

    api_url = "https://drive.quark.cn/1/clouddrive/capacity"

    try:
        response = requests.get(api_url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()

            if data.get("status") == 200:
                capacity_data = data.get("data", {})

                total = capacity_data.get("total_capacity", 0)
                used = capacity_data.get("use_capacity", 0)
                secret_total = capacity_data.get("secret_total_capacity", 0)
                secret_used = capacity_data.get("secret_use_capacity", 0)

                # 格式化容量
                def format_size(bytes_size):
                    if bytes_size >= 1024**3:  # GB
                        return f"{bytes_size / 1024**3:.2f} GB"
                    elif bytes_size >= 1024**2:  # MB
                        return f"{bytes_size / 1024**2:.2f} MB"
                    elif bytes_size >= 1024:  # KB
                        return f"{bytes_size / 1024:.2f} KB"
                    else:
                        return f"{bytes_size} B"

                print("\n=== 夸克网盘容量信息 ===")
                print(f"总容量: {format_size(total)}")
                print(f"已使用: {format_size(used)}")

                if total > 0:
                    used_percent = (used / total) * 100
                    print(f"使用率: {used_percent:.1f}%")

                if secret_total > 0:
                    print(f"\n私密空间:")
                    print(f"  总容量: {format_size(secret_total)}")
                    print(f"  已使用: {format_size(secret_used)}")

                return capacity_data

        return None

    except Exception as e:
        print(f"获取容量信息失败: {e}")
        return None


def main():
    print("=== 夸克网盘文件查看工具 ===")

    # 从数据库获取配置
    config = get_quark_config_from_db()

    if not config:
        print("未找到夸克网盘配置")

        # 尝试从备份文件读取Cookie
        backup_file = "quark_cookie_backup.txt"
        if os.path.exists(backup_file):
            with open(backup_file, "r", encoding="utf-8") as f:
                cookie = f.read().strip()
                config = {"cookie": cookie, "root_id": "0"}
                print(f"从备份文件读取Cookie: {len(cookie)} 字符")
        else:
            print("请先配置夸克网盘")
            return

    cookie = config.get("cookie", "")
    root_id = config.get("root_id", "0")

    if not cookie:
        print("Cookie为空")
        return

    print(f"使用Cookie长度: {len(cookie)} 字符")
    print(f"根目录ID: {root_id}")

    # 测试Cookie有效性
    print("\n正在测试Cookie有效性...")
    capacity_info = get_quark_capacity(cookie)

    if capacity_info:
        print("✓ Cookie有效")

        # 获取文件列表
        print("\n正在获取文件列表...")
        files_data = get_quark_files(cookie, root_id)

        if files_data:
            print("\n✓ 文件列表获取成功")

            # 提供交互选项
            print("\n=== 操作选项 ===")
            print("1. 查看下一页")
            print("2. 查看特定目录")
            print("3. 查看容量详情")
            print("4. 退出")

            try:
                choice = input("\n请选择 (1-4): ").strip()

                if choice == "1":
                    # 获取下一页
                    metadata = files_data.get("metadata", {})
                    current_page = metadata.get("_page", 1)
                    get_quark_files(cookie, root_id, current_page + 1)

                elif choice == "2":
                    folder_id = input("请输入目录ID (默认为0): ").strip() or "0"
                    get_quark_files(cookie, folder_id)

                elif choice == "3":
                    get_quark_capacity(cookie)

            except:
                print("使用默认选项")

        else:
            print("✗ 获取文件列表失败")
    else:
        print("✗ Cookie无效或网络错误")


if __name__ == "__main__":
    main()
