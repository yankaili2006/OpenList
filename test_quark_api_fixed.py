#!/usr/bin/env python3
"""
测试夸克网盘API - 使用正确的参数
"""

import requests
import json
import time


def test_quark_api_fixed():
    # 从备份文件读取Cookie
    with open("quark_cookie_backup.txt", "r", encoding="utf-8") as f:
        cookie = f.read().strip()

    print("=== 测试夸克网盘API (修正版) ===")
    print(f"Cookie长度: {len(cookie)} 字符")

    # OpenList夸克驱动使用的配置
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) quark-cloud-drive/2.5.20 Chrome/100.0.4896.160 Electron/18.3.5.4-b478491100 Safari/537.36 Channel/pckk_other_ch",
        "Referer": "https://pan.quark.cn",
        "Cookie": cookie,
        "Accept": "application/json, text/plain, */*",
    }

    base_url = "https://drive.quark.cn/1/clouddrive"

    # 测试1: 获取配置信息 (带查询参数)
    print("\n1. 测试 /config (GET with query params)")
    try:
        params = {"pr": "ucpro", "fr": "pc"}

        response = requests.get(
            f"{base_url}/config", headers=headers, params=params, timeout=10
        )
        print(f"状态码: {response.status_code}")
        print(f"请求URL: {response.url}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"响应: {json.dumps(data, ensure_ascii=False)[:200]}...")
                print("✓ /config API 工作正常")
            except:
                print(f"响应: {response.text[:200]}...")
        elif response.status_code == 401:
            print("✗ 401 未授权 - Cookie可能无效")
            print(f"响应头: {dict(response.headers)}")
        else:
            print(f"HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"请求失败: {e}")

    # 测试2: 获取文件列表 (使用GET方法，参数在查询字符串中)
    print("\n2. 测试获取文件列表 (GET)")
    try:
        # 构建查询参数
        params = {
            "pr": "ucpro",
            "fr": "pc",
            "pdir_fid": "0",
            "_page": "1",
            "_size": "20",
            "_fetch_total": "1",
            "_fetch_sub_dirs": "0",
            "_sort": "file_type",
            "_order": "asc",
            "force": "0",
            "web": "1",
        }

        response = requests.get(
            f"{base_url}/file/sort", headers=headers, params=params, timeout=15
        )
        print(f"状态码: {response.status_code}")
        print(f"请求URL: {response.url[:100]}...")

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

                    print(f"\n✓ 文件列表获取成功!")
                    print(f"总文件数: {total}")
                    print(f"本页数量: {count}")

                    if file_list:
                        print(f"\n=== 文件列表 (显示前10个) ===")
                        for i, file_item in enumerate(file_list[:10], 1):
                            name = file_item.get("file_name", "未知")
                            fid = file_item.get("fid", "")
                            is_file = file_item.get("file", True)
                            size = file_item.get("size", 0)
                            category = file_item.get("category", 0)

                            file_type = "📄 文件" if is_file else "📁 文件夹"

                            # 格式化大小
                            if size >= 1024**3:
                                size_str = f"{size / 1024**3:.2f} GB"
                            elif size >= 1024**2:
                                size_str = f"{size / 1024**2:.2f} MB"
                            elif size >= 1024:
                                size_str = f"{size / 1024:.2f} KB"
                            else:
                                size_str = f"{size} B"

                            # 分类信息
                            categories = {
                                0: "其他",
                                1: "图片",
                                2: "文档",
                                3: "视频",
                                4: "音频",
                                5: "压缩包",
                            }
                            category_str = categories.get(category, "未知")

                            print(f"\n{i}. {name}")
                            print(f"   {file_type}")
                            print(f"   分类: {category_str}")
                            print(f"   大小: {size_str}")
                            print(f"   ID: {fid}")

                            # 显示时间信息
                            updated_at = file_item.get("updated_at")
                            if updated_at:
                                dt = time.strftime(
                                    "%Y-%m-%d %H:%M:%S",
                                    time.localtime(updated_at / 1000),
                                )
                                print(f"   修改时间: {dt}")
                    else:
                        print("当前目录为空")

                else:
                    print(f"API错误: {data.get('message', '未知错误')}")
                    print(f"错误代码: {data.get('code', '未知')}")

            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
                print(f"响应内容: {response.text[:200]}...")
        elif response.status_code == 401:
            print("✗ 401 未授权")
        elif response.status_code == 403:
            print("✗ 403 禁止访问")
        elif response.status_code == 404:
            print("✗ 404 未找到")
        else:
            print(f"HTTP错误: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")

    except Exception as e:
        print(f"请求失败: {e}")

    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_quark_api_fixed()
