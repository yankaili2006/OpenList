#!/usr/bin/env python3
"""
测试夸克网盘API
使用OpenList驱动中的配置
"""

import requests
import json
import time


def test_quark_api():
    # 从备份文件读取Cookie
    with open("quark_cookie_backup.txt", "r", encoding="utf-8") as f:
        cookie = f.read().strip()

    print("=== 测试夸克网盘API ===")
    print(f"Cookie长度: {len(cookie)} 字符")

    # OpenList夸克驱动使用的配置
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) quark-cloud-drive/2.5.20 Chrome/100.0.4896.160 Electron/18.3.5.4-b478491100 Safari/537.36 Channel/pckk_other_ch",
        "Referer": "https://pan.quark.cn",
        "Cookie": cookie,
        "Content-Type": "application/json",
    }

    base_url = "https://drive.quark.cn/1/clouddrive"

    # 测试1: 获取配置信息
    print("\n1. 测试 /config (GET)")
    try:
        response = requests.get(f"{base_url}/config", headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"响应: {json.dumps(data, ensure_ascii=False)[:200]}...")
                print("✓ /config API 工作正常")
            except:
                print(f"响应: {response.text[:200]}...")
        else:
            print(f"HTTP错误: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
    except Exception as e:
        print(f"请求失败: {e}")

    # 测试2: 获取容量信息
    print("\n2. 测试 /capacity (GET)")
    try:
        response = requests.get(f"{base_url}/capacity", headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"响应: {json.dumps(data, ensure_ascii=False)[:200]}...")

                if data.get("status") == 200:
                    capacity = data.get("data", {})
                    total = capacity.get("total_capacity", 0)
                    used = capacity.get("use_capacity", 0)

                    # 格式化
                    def format_size(bytes_size):
                        if bytes_size >= 1024**3:
                            return f"{bytes_size / 1024**3:.2f} GB"
                        elif bytes_size >= 1024**2:
                            return f"{bytes_size / 1024**2:.2f} MB"
                        elif bytes_size >= 1024:
                            return f"{bytes_size / 1024:.2f} KB"
                        else:
                            return f"{bytes_size} B"

                    print(f"✓ 容量信息:")
                    print(f"  总容量: {format_size(total)}")
                    print(f"  已使用: {format_size(used)}")

                    if total > 0:
                        used_percent = (used / total) * 100
                        print(f"  使用率: {used_percent:.1f}%")
                else:
                    print(f"API错误: {data.get('message', '未知错误')}")

            except json.JSONDecodeError:
                print(f"响应: {response.text[:200]}...")
        else:
            print(f"HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"请求失败: {e}")

    # 测试3: 获取文件列表 (使用POST)
    print("\n3. 测试 /file/sort (POST)")
    try:
        # 准备请求数据
        payload = {
            "pr": "ucpro",
            "fr": "pc",
            "uc_param_str": "",
            "__dt": int(time.time() * 1000),
            "__t": int(time.time() * 1000),
            "pdir_fid": "0",
            "_page": 1,
            "_size": 20,
            "_fetch_total": 1,
            "_fetch_sub_dirs": 0,
            "_sort": "file_type",
            "_order": "asc",
            "force": 0,
            "web": 1,
        }

        response = requests.post(
            f"{base_url}/file/sort", headers=headers, json=payload, timeout=15
        )
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"响应状态: {data.get('status', '未知')}")
                print(f"响应消息: {data.get('message', '无')}")

                if data.get("status") == 200:
                    file_list = data.get("data", {}).get("list", [])
                    metadata = data.get("metadata", {})

                    total = metadata.get("_total", 0)
                    count = metadata.get("_count", 0)

                    print(f"✓ 文件列表获取成功!")
                    print(f"  总文件数: {total}")
                    print(f"  本页数量: {count}")

                    if file_list:
                        print(f"\n前5个文件/文件夹:")
                        for i, file_item in enumerate(file_list[:5], 1):
                            name = file_item.get("file_name", "未知")
                            fid = file_item.get("fid", "")
                            is_file = file_item.get("file", True)
                            size = file_item.get("size", 0)

                            file_type = "文件" if is_file else "文件夹"
                            size_str = (
                                f"{size / 1024**2:.2f} MB"
                                if size >= 1024**2
                                else f"{size / 1024:.2f} KB"
                            )

                            print(
                                f"  {i}. {name} ({file_type}, ID: {fid}, 大小: {size_str})"
                            )
                    else:
                        print("  当前目录为空")

                else:
                    print(f"API错误: {data.get('message', '未知错误')}")
                    print(f"完整响应: {json.dumps(data, ensure_ascii=False)[:300]}...")

            except json.JSONDecodeError:
                print(f"响应: {response.text[:200]}...")
        else:
            print(f"HTTP错误: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            print(f"响应体: {response.text[:200]}...")
    except Exception as e:
        print(f"请求失败: {e}")

    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_quark_api()
