#!/usr/bin/env python3
"""
调试夸克网盘Cookie有效性
"""

import requests
import json


def test_quark_cookie():
    # 您的Cookie
    cookie = """b-user-id=b2f00992-e02e-1207-a5d9-7d15fb56b95e; _UP_A4A_11_=wb9cf1ff36c348c48596a9116a6acdda; b-user-id=b2f00992-e02e-1207-a5d9-7d15fb56b95e; __sdid=AARha+ezLPuN/gbc25ZI0D+8Yb2+uVN/MKJef/bzwhY7MSd6BDnmV0oQ9AEKRkntJQg=; _UP_D_=pc; _UP_30C_6A_=st9d062010fulph39e55i3p2co5lvhg8; _UP_TS_=sg18d52af08cb3b1e9cb22709fbf8c3828d; _UP_E37_B7_=sg18d52af08cb3b1e9cb22709fbf8c3828d; _UP_TG_=st9d062010fulph39e55i3p2co5lvhg8; _UP_335_2B_=1; __pus=d415f7eb03ecb1c5ccbdd7af6ee94376AAQ0khsn0D0WAGVgzLuqGE9Lwe8WYKdsqtrJ3JYNeCx43fjIiG0xHAEA7JgvU+gaN3x6QRwAoO+XMyPKB/T2i1IP; __kp=1ad76260-e32a-11f0-a3c0-319173300c11; __kps=AAQAe2WYfE98dBJG3WiXgEGw; __ktd=s8oufCPVoOciOwKPoDzeZw==; __uid=AAQAe2WYfE98dBJG3WiXgEGw; isg=BFtb1IPztrLKS8rZceki0UgX6rnFMG8yOmozpU2YOtpxLHsO1AFWg3NvwoyiDMcq; tfstk=gmMmYv62hz_C5PbyKNyXgVpGZoAJT-wTQruTWPna7o47uPdjXb2ZvVqTHc8js4maPAEa7P5PIlq30oP4bz0oPqXAB-zAjRmi-VV6cPUaSVnZM3pppmibCRuMJppdGuA-Kx4NWRybU7EZopJppmiVDo-K4phx2PEzXPyag5zzzzZ13RPauL-ublQV_tuZ4347YP74QR7zzlrFgRyZ78-ujk2a7VP2q0z7bRzZ1iIzkVujUFnb0aqqngBQ4S4E0zXnVYr4Tsi4rTXoE8ea8R4lQOkumcubYlB2Kzlx_xer3U7QUDG-uu2HIGqot0y4mV9Ch-oE4fPmICIQ5bmr97c5DnZonDDgx7_ymPMxoAVjLeB7ubDSI-hJo9U__bHbOxLPnJlID-hZzhWaSbrN4yCPTLTFCypof11_guZuJaBN1BSSEDbMq3fEOSr70pKkq1t4guZuJ3xlTLF4VoJd.; ctoken=nmn9Ax9HfZWn0uexnn1aNVCA; web-grey-id=0c1117e9-6509-d8ef-769b-a756d2cde885; web-grey-id.sig=Qw_BmYXPMa6CisGsG_fQeHr_9VFsgXOH-pco3IwY4qY; __wpkreporterwid_=36c150c8-5e76-48de-307c-892d3d145a01; grey-id=8599a299-50dd-5ad6-6f20-303188eab35d; grey-id.sig=It6GwVsKeXcl9wQ8ZiB8B4ArhQHd8CmlApv__8O2rg8; isQuark=true; isQuark.sig=hUgqObykqFom5Y09bll94T1sS9abT1X-4Df_lzgl8nM; __puus=9fc0a44deb137c76bb154583ee78aa12AAQ3eYXa8+b35MeLINY3BS2e303MXf7a7iEj/6TzwNohN9zJQ+ziAW3fn7xjWW3tLTNcyIZ9/DCiOcoTBA+GJxvthNHbhgDncJKoS8VuGzCLXzVx547IJ+/qxG1qZNQfRaOO02YHuF1ebpG34+JZRbQygZOD+VDJTOdwl5iynsqms3MOBMj0JsDa28vl0lVXrIT0Gpkglnusx6zXbJd0J2FS"""

    print("=== 测试夸克网盘Cookie ===")
    print(f"Cookie长度: {len(cookie)} 字符")

    # 基本请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": cookie,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://pan.quark.cn/",
        "Origin": "https://pan.quark.cn",
    }

    # 测试1: 访问主页
    print("\n1. 测试访问夸克网盘主页...")
    try:
        response = requests.get("https://pan.quark.cn", headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"URL: {response.url}")

        if response.status_code == 200:
            if "login" in response.url or "sign" in response.url:
                print("⚠ 被重定向到登录页，Cookie可能无效")
            else:
                print("✓ 成功访问主页")
                # 检查页面标题
                if "<title>" in response.text:
                    import re

                    title_match = re.search(r"<title>(.*?)</title>", response.text)
                    if title_match:
                        print(f"页面标题: {title_match.group(1)}")
        else:
            print(f"HTTP错误: {response.status_code}")

    except Exception as e:
        print(f"请求失败: {e}")

    # 测试2: 尝试新的API端点
    print("\n2. 测试API端点...")

    # 可能的API端点
    api_endpoints = [
        "https://pan.quark.cn/api/file/list",
        "https://drive-pc.quark.cn/1/clouddrive/file/sort",
        "https://drive.quark.cn/1/clouddrive/file/sort",
        "https://pc-api.quark.cn/1/clouddrive/file/sort",
    ]

    for endpoint in api_endpoints:
        print(f"\n测试端点: {endpoint}")
        try:
            # 准备请求数据
            payload = {
                "pdir_fid": "0",
                "_page": 1,
                "_size": 20,
                "_fetch_total": 1,
                "_sort": "file_type",
                "_order": "asc",
            }

            api_headers = headers.copy()
            api_headers["Content-Type"] = "application/json"

            response = requests.post(
                endpoint, headers=api_headers, json=payload, timeout=15
            )
            print(f"状态码: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"响应类型: JSON")

                    if "data" in data or "list" in data:
                        print("✓ API响应包含数据字段")
                        print(
                            f"响应预览: {json.dumps(data, ensure_ascii=False)[:200]}..."
                        )
                        break  # 找到有效的API端点
                    else:
                        print(
                            f"响应内容: {json.dumps(data, ensure_ascii=False)[:200]}..."
                        )

                except json.JSONDecodeError:
                    print(f"响应内容: {response.text[:200]}...")

            elif response.status_code == 404:
                print("✗ 404 - 端点不存在")
            elif response.status_code == 403:
                print("✗ 403 - 禁止访问")
            elif response.status_code == 401:
                print("✗ 401 - 未授权")

        except Exception as e:
            print(f"请求失败: {e}")

    # 分析Cookie结构
    print("\n3. Cookie结构分析:")
    cookie_parts = cookie.split("; ")
    print(f"总字段数: {len(cookie_parts)}")

    # 分类显示
    print("\n重要字段:")
    important = [
        "b-user-id",
        "ctoken",
        "isQuark",
        "grey-id",
        "web-grey-id",
        "__pus",
        "__kp",
        "__uid",
    ]
    for field in important:
        for part in cookie_parts:
            if part.startswith(field + "="):
                value = part[len(field) + 1 :]
                print(f"  {field}: {'*' * min(20, len(value))} (长度: {len(value)})")
                break

    print("\n其他字段:")
    other_count = 0
    for part in cookie_parts:
        is_important = False
        for field in important:
            if part.startswith(field + "="):
                is_important = True
                break
        if not is_important:
            other_count += 1
            if other_count <= 5:  # 只显示前5个
                print(f"  {part[:50]}...")

    if other_count > 5:
        print(f"  还有 {other_count - 5} 个其他字段...")

    print(f"\n总结: Cookie包含 {len(cookie_parts)} 个字段，{len(cookie)} 个字符")


if __name__ == "__main__":
    test_quark_cookie()
