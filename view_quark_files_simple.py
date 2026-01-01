#!/usr/bin/env python3
"""
简单查看夸克网盘文件列表
直接使用Cookie调用API
"""

import requests
import json
import os
from datetime import datetime


def load_cookie():
    """加载Cookie"""
    # 首先尝试从备份文件
    backup_file = "quark_cookie_backup.txt"
    if os.path.exists(backup_file):
        with open(backup_file, "r", encoding="utf-8") as f:
            cookie = f.read().strip()
            print(f"从备份文件读取Cookie: {len(cookie)} 字符")
            return cookie

    # 使用硬编码的Cookie
    cookie = """b-user-id=b2f00992-e02e-1207-a5d9-7d15fb56b95e; _UP_A4A_11_=wb9cf1ff36c348c48596a9116a6acdda; b-user-id=b2f00992-e02e-1207-a5d9-7d15fb56b95e; __sdid=AARha+ezLPuN/gbc25ZI0D+8Yb2+uVN/MKJef/bzwhY7MSd6BDnmV0oQ9AEKRkntJQg=; _UP_D_=pc; _UP_30C_6A_=st9d062010fulph39e55i3p2co5lvhg8; _UP_TS_=sg18d52af08cb3b1e9cb22709fbf8c3828d; _UP_E37_B7_=sg18d52af08cb3b1e9cb22709fbf8c3828d; _UP_TG_=st9d062010fulph39e55i3p2co5lvhg8; _UP_335_2B_=1; __pus=d415f7eb03ecb1c5ccbdd7af6ee94376AAQ0khsn0D0WAGVgzLuqGE9Lwe8WYKdsqtrJ3JYNeCx43fjIiG0xHAEA7JgvU+gaN3x6QRwAoO+XMyPKB/T2i1IP; __kp=1ad76260-e32a-11f0-a3c0-319173300c11; __kps=AAQAe2WYfE98dBJG3WiXgEGw; __ktd=s8oufCPVoOciOwKPoDzeZw==; __uid=AAQAe2WYfE98dBJG3WiXgEGw; isg=BFtb1IPztrLKS8rZceki0UgX6rnFMG8yOmozpU2YOtpxLHsO1AFWg3NvwoyiDMcq; tfstk=gmMmYv62hz_C5PbyKNyXgVpGZoAJT-wTQruTWPna7o47uPdjXb2ZvVqTHc8js4maPAEa7P5PIlq30oP4bz0oPqXAB-zAjRmi-VV6cPUaSVnZM3pppmibCRuMJppdGuA-Kx4NWRybU7EZopJppmiVDo-K4phx2PEzXPyag5zzzzZ13RPauL-ublQV_tuZ4347YP74QR7zzlrFgRyZ78-ujk2a7VP2q0z7bRzZ1iIzkVujUFnb0aqqngBQ4S4E0zXnVYr4Tsi4rTXoE8ea8R4lQOkumcubYlB2Kzlx_xer3U7QUDG-uu2HIGqot0y4mV9Ch-oE4fPmICIQ5bmr97c5DnZonDDgx7_ymPMxoAVjLeB7ubDSI-hJo9U__bHbOxLPnJlID-hZzhWaSbrN4yCPTLTFCypof11_guZuJaBN1BSSEDbMq3fEOSr70pKkq1t4guZuJ3xlTLF4VoJd.; ctoken=nmn9Ax9HfZWn0uexnn1aNVCA; web-grey-id=0c1117e9-6509-d8ef-769b-a756d2cde885; web-grey-id.sig=Qw_BmYXPMa6CisGsG_fQeHr_9VFsgXOH-pco3IwY4qY; __wpkreporterwid_=36c150c8-5e76-48de-307c-892d3d145a01; grey-id=8599a299-50dd-5ad6-6f20-303188eab35d; grey-id.sig=It6GwVsKeXcl9wQ8ZiB8B4ArhQHd8CmlApv__8O2rg8; isQuark=true; isQuark.sig=hUgqObykqFom5Y09bll94T1sS9abT1X-4Df_lzgl8nM; __puus=9fc0a44deb137c76bb154583ee78aa12AAQ3eYXa8+b35MeLINY3BS2e303MXf7a7iEj/6TzwNohN9zJQ+ziAW3fn7xjWW3tLTNcyIZ9/DCiOcoTBA+GJxvthNHbhgDncJKoS8VuGzCLXzVx547IJ+/qxG1qZNQfRaOO02YHuF1ebpG34+JZRbQygZOD+VDJTOdwl5iynsqms3MOBMj0JsDa28vl0lVXrIT0Gpkglnusx6zXbJd0J2FS"""

    print(f"使用硬编码Cookie: {len(cookie)} 字符")
    return cookie


def test_cookie(cookie):
    """测试Cookie有效性"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://pan.quark.cn",
        "Cookie": cookie,
    }

    # 测试容量API
    url = "https://drive.quark.cn/1/clouddrive/capacity"

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == 200:
                capacity = data.get("data", {})
                total = capacity.get("total_capacity", 0)
                used = capacity.get("use_capacity", 0)

                # 格式化容量
                def format_size(bytes_size):
                    if bytes_size >= 1024**3:
                        return f"{bytes_size / 1024**3:.2f} GB"
                    elif bytes_size >= 1024**2:
                        return f"{bytes_size / 1024**2:.2f} MB"
                    elif bytes_size >= 1024:
                        return f"{bytes_size / 1024:.2f} KB"
                    else:
                        return f"{bytes_size} B"

                print(f"✓ Cookie有效")
                print(f"总容量: {format_size(total)}")
                print(f"已使用: {format_size(used)}")

                if total > 0:
                    used_percent = (used / total) * 100
                    print(f"使用率: {used_percent:.1f}%")

                return True
            else:
                print(f"✗ API错误: {data.get('message', '未知错误')}")
                return False
        else:
            print(f"✗ HTTP错误: {response.status_code}")
            return False

    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False


def list_files(cookie, folder_id="0"):
    """列出文件"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) quark-cloud-drive/2.5.20 Chrome/100.0.4896.160 Electron/18.3.5.4-b478491100 Safari/537.36 Channel/pckk_other_ch",
        "Referer": "https://pan.quark.cn",
        "Cookie": cookie,
        "Content-Type": "application/json",
    }

    url = "https://drive.quark.cn/1/clouddrive/file/sort"

    payload = {
        "pr": "ucpro",
        "fr": "pc",
        "pdir_fid": folder_id,
        "_page": 1,
        "_size": 50,
        "_fetch_total": 1,
        "_fetch_sub_dirs": 0,
        "_sort": "file_type",
        "_order": "asc",
        "force": 0,
        "web": 1,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            data = response.json()

            if data.get("status") == 200:
                files = data.get("data", {}).get("list", [])
                metadata = data.get("metadata", {})

                total = metadata.get("_total", 0)
                count = metadata.get("_count", 0)

                print(f"\n=== 文件列表 (共{total}个) ===")
                print(f"显示 {count} 个文件/文件夹")

                if not files:
                    print("当前目录为空")
                    return []

                for i, file_item in enumerate(files, 1):
                    name = file_item.get("file_name", "未知")
                    fid = file_item.get("fid", "")
                    is_file = file_item.get("file", True)
                    size = file_item.get("size", 0)

                    # 格式化
                    if size >= 1024**3:
                        size_str = f"{size / 1024**3:.2f} GB"
                    elif size >= 1024**2:
                        size_str = f"{size / 1024**2:.2f} MB"
                    elif size >= 1024:
                        size_str = f"{size / 1024:.2f} KB"
                    else:
                        size_str = f"{size} B"

                    file_type = "📄 文件" if is_file else "📁 文件夹"

                    print(f"\n{i}. {name}")
                    print(f"   {file_type}")
                    print(f"   ID: {fid}")
                    print(f"   大小: {size_str}")

                    # 显示前3个的详细信息
                    if i <= 3:
                        print(
                            f"   原始数据: {json.dumps(file_item, ensure_ascii=False)[:80]}..."
                        )

                return files
            else:
                print(f"API错误: {data.get('message', '未知错误')}")
                return []
        else:
            print(f"HTTP错误: {response.status_code}")
            return []

    except Exception as e:
        print(f"请求失败: {e}")
        return []


def main():
    print("=== 夸克网盘文件查看工具 ===")

    # 加载Cookie
    cookie = load_cookie()

    if not cookie:
        print("无法加载Cookie")
        return

    # 测试Cookie
    print("\n测试Cookie有效性...")
    if not test_cookie(cookie):
        print("Cookie无效，请检查或重新获取")
        return

    # 列出文件
    print("\n获取文件列表...")
    files = list_files(cookie)

    if files:
        print(f"\n✓ 成功获取 {len(files)} 个文件/文件夹")

        # 简单统计
        file_count = sum(1 for f in files if f.get("file", True))
        folder_count = len(files) - file_count

        print(f"文件: {file_count} 个，文件夹: {folder_count} 个")

        # 显示文件类型统计
        print("\n文件类型统计:")
        extensions = {}
        for file_item in files:
            if file_item.get("file", True):
                name = file_item.get("file_name", "")
                if "." in name:
                    ext = name.split(".")[-1].lower()
                    extensions[ext] = extensions.get(ext, 0) + 1

        for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]:
            print(f"  .{ext}: {count} 个")

    else:
        print("✗ 获取文件列表失败")


if __name__ == "__main__":
    main()
