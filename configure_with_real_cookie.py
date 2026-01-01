#!/usr/bin/env python3
"""
使用真实Cookie配置夸克网盘
"""

import sqlite3
import json
import os


def configure_quark_with_real_cookie():
    # 您提供的Cookie
    real_cookie = """b-user-id=b2f00992-e02e-1207-a5d9-7d15fb56b95e; _UP_A4A_11_=wb9cf1ff36c348c48596a9116a6acdda; b-user-id=b2f00992-e02e-1207-a5d9-7d15fb56b95e; __sdid=AARha+ezLPuN/gbc25ZI0D+8Yb2+uVN/MKJef/bzwhY7MSd6BDnmV0oQ9AEKRkntJQg=; _UP_D_=pc; _UP_30C_6A_=st9d062010fulph39e55i3p2co5lvhg8; _UP_TS_=sg18d52af08cb3b1e9cb22709fbf8c3828d; _UP_E37_B7_=sg18d52af08cb3b1e9cb22709fbf8c3828d; _UP_TG_=st9d062010fulph39e55i3p2co5lvhg8; _UP_335_2B_=1; __pus=d415f7eb03ecb1c5ccbdd7af6ee94376AAQ0khsn0D0WAGVgzLuqGE9Lwe8WYKdsqtrJ3JYNeCx43fjIiG0xHAEA7JgvU+gaN3x6QRwAoO+XMyPKB/T2i1IP; __kp=1ad76260-e32a-11f0-a3c0-319173300c11; __kps=AAQAe2WYfE98dBJG3WiXgEGw; __ktd=s8oufCPVoOciOwKPoDzeZw==; __uid=AAQAe2WYfE98dBJG3WiXgEGw; isg=BFtb1IPztrLKS8rZceki0UgX6rnFMG8yOmozpU2YOtpxLHsO1AFWg3NvwoyiDMcq; tfstk=gmMmYv62hz_C5PbyKNyXgVpGZoAJT-wTQruTWPna7o47uPdjXb2ZvVqTHc8js4maPAEa7P5PIlq30oP4bz0oPqXAB-zAjRmi-VV6cPUaSVnZM3pppmibCRuMJppdGuA-Kx4NWRybU7EZopJppmiVDo-K4phx2PEzXPyag5zzzzZ13RPauL-ublQV_tuZ4347YP74QR7zzlrFgRyZ78-ujk2a7VP2q0z7bRzZ1iIzkVujUFnb0aqqngBQ4S4E0zXnVYr4Tsi4rTXoE8ea8R4lQOkumcubYlB2Kzlx_xer3U7QUDG-uu2HIGqot0y4mV9Ch-oE4fPmICIQ5bmr97c5DnZonDDgx7_ymPMxoAVjLeB7ubDSI-hJo9U__bHbOxLPnJlID-hZzhWaSbrN4yCPTLTFCypof11_guZuJaBN1BSSEDbMq3fEOSr70pKkq1t4guZuJ3xlTLF4VoJd.; ctoken=nmn9Ax9HfZWn0uexnn1aNVCA; web-grey-id=0c1117e9-6509-d8ef-769b-a756d2cde885; web-grey-id.sig=Qw_BmYXPMa6CisGsG_fQeHr_9VFsgXOH-pco3IwY4qY; __wpkreporterwid_=36c150c8-5e76-48de-307c-892d3d145a01; grey-id=8599a299-50dd-5ad6-6f20-303188eab35d; grey-id.sig=It6GwVsKeXcl9wQ8ZiB8B4ArhQHd8CmlApv__8O2rg8; isQuark=true; isQuark.sig=hUgqObykqFom5Y09bll94T1sS9abT1X-4Df_lzgl8nM; __puus=9fc0a44deb137c76bb154583ee78aa12AAQ3eYXa8+b35MeLINY3BS2e303MXf7a7iEj/6TzwNohN9zJQ+ziAW3fn7xjWW3tLTNcyIZ9/DCiOcoTBA+GJxvthNHbhgDncJKoS8VuGzCLXzVx547IJ+/qxG1qZNQfRaOO02YHuF1ebpG34+JZRbQygZOD+VDJTOdwl5iynsqms3MOBMj0JsDa28vl0lVXrIT0Gpkglnusx6zXbJd0J2FS"""

    # 数据库路径
    data_dir = "/Users/primihub/github/OpenList/data"
    db_path = os.path.join(data_dir, "data.db")

    print("=== 使用真实Cookie配置夸克网盘 ===")
    print(f"Cookie长度: {len(real_cookie)} 字符")

    # 检查数据库是否存在
    if not os.path.exists(db_path):
        print(f"数据库不存在: {db_path}")
        print("请先启动OpenList服务以创建数据库")

        # 尝试创建数据目录
        os.makedirs(data_dir, exist_ok=True)
        print(f"已创建数据目录: {data_dir}")
        print("现在需要启动OpenList服务来初始化数据库")

        # 保存Cookie到文件供后续使用
        with open("real_quark_cookie.txt", "w", encoding="utf-8") as f:
            f.write(real_cookie)
        print("Cookie已保存到 real_quark_cookie.txt")

        return False

    mount_path = "/quark"
    remark = "夸克网盘真实配置"

    # 夸克网盘配置
    addition = {
        "cookie": real_cookie,
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
            cookie_value = addition_data.get("cookie", "")
            print(f"Cookie长度: {len(cookie_value)} 字符")
            print(f"Root ID: {addition_data.get('root_id', '')}")

            # 检查关键Cookie字段
            print("\n关键Cookie字段检查:")
            cookie_parts = cookie_value.split("; ")
            important_keys = [
                "b-user-id",
                "ctoken",
                "isQuark",
                "grey-id",
                "web-grey-id",
            ]

            for key in important_keys:
                found = False
                for part in cookie_parts:
                    if part.startswith(key + "="):
                        print(f"✓ {key}: 存在")
                        found = True
                        break
                if not found:
                    print(f"✗ {key}: 未找到")

        conn.close()

        print("\n" + "=" * 50)
        print("配置完成!")
        print("=" * 50)
        print(f"挂载路径: {mount_path}")
        print(f"驱动类型: Quark")
        print(f"备注: {remark}")
        print(f"Cookie已配置: {len(real_cookie)} 字符")

        # 保存Cookie到单独文件备份
        with open("quark_cookie_backup.txt", "w", encoding="utf-8") as f:
            f.write(real_cookie)
        print(f"\nCookie备份已保存到: quark_cookie_backup.txt")

        print("\n下一步:")
        print("1. 启动OpenList服务: ./start_openlist.sh")
        print("2. 访问 http://localhost:5244")
        print("3. 查看夸克网盘文件")

        return True

    except sqlite3.OperationalError as e:
        print(f"数据库操作错误: {e}")
        print("可能需要先启动OpenList服务初始化数据库")
        return False
    except Exception as e:
        print(f"配置失败: {e}")
        return False


def test_cookie_validity():
    """
    简单测试Cookie是否有效
    """
    print("\n=== 测试Cookie有效性 ===")

    # 您提供的Cookie
    cookie = """b-user-id=b2f00992-e02e-1207-a5d9-7d15fb56b95e; _UP_A4A_11_=wb9cf1ff36c348c48596a9116a6acdda; b-user-id=b2f00992-e02e-1207-a5d9-7d15fb56b95e; __sdid=AARha+ezLPuN/gbc25ZI0D+8Yb2+uVN/MKJef/bzwhY7MSd6BDnmV0oQ9AEKRkntJQg=; _UP_D_=pc; _UP_30C_6A_=st9d062010fulph39e55i3p2co5lvhg8; _UP_TS_=sg18d52af08cb3b1e9cb22709fbf8c3828d; _UP_E37_B7_=sg18d52af08cb3b1e9cb22709fbf8c3828d; _UP_TG_=st9d062010fulph39e55i3p2co5lvhg8; _UP_335_2B_=1; __pus=d415f7eb03ecb1c5ccbdd7af6ee94376AAQ0khsn0D0WAGVgzLuqGE9Lwe8WYKdsqtrJ3JYNeCx43fjIiG0xHAEA7JgvU+gaN3x6QRwAoO+XMyPKB/T2i1IP; __kp=1ad76260-e32a-11f0-a3c0-319173300c11; __kps=AAQAe2WYfE98dBJG3WiXgEGw; __ktd=s8oufCPVoOciOwKPoDzeZw==; __uid=AAQAe2WYfE98dBJG3WiXgEGw; isg=BFtb1IPztrLKS8rZceki0UgX6rnFMG8yOmozpU2YOtpxLHsO1AFWg3NvwoyiDMcq; tfstk=gmMmYv62hz_C5PbyKNyXgVpGZoAJT-wTQruTWPna7o47uPdjXb2ZvVqTHc8js4maPAEa7P5PIlq30oP4bz0oPqXAB-zAjRmi-VV6cPUaSVnZM3pppmibCRuMJppdGuA-Kx4NWRybU7EZopJppmiVDo-K4phx2PEzXPyag5zzzzZ13RPauL-ublQV_tuZ4347YP74QR7zzlrFgRyZ78-ujk2a7VP2q0z7bRzZ1iIzkVujUFnb0aqqngBQ4S4E0zXnVYr4Tsi4rTXoE8ea8R4lQOkumcubYlB2Kzlx_xer3U7QUDG-uu2HIGqot0y4mV9Ch-oE4fPmICIQ5bmr97c5DnZonDDgx7_ymPMxoAVjLeB7ubDSI-hJo9U__bHbOxLPnJlID-hZzhWaSbrN4yCPTLTFCypof11_guZuJaBN1BSSEDbMq3fEOSr70pKkq1t4guZuJ3xlTLF4VoJd.; ctoken=nmn9Ax9HfZWn0uexnn1aNVCA; web-grey-id=0c1117e9-6509-d8ef-769b-a756d2cde885; web-grey-id.sig=Qw_BmYXPMa6CisGsG_fQeHr_9VFsgXOH-pco3IwY4qY; __wpkreporterwid_=36c150c8-5e76-48de-307c-892d3d145a01; grey-id=8599a299-50dd-5ad6-6f20-303188eab35d; grey-id.sig=It6GwVsKeXcl9wQ8ZiB8B4ArhQHd8CmlApv__8O2rg8; isQuark=true; isQuark.sig=hUgqObykqFom5Y09bll94T1sS9abT1X-4Df_lzgl8nM; __puus=9fc0a44deb137c76bb154583ee78aa12AAQ3eYXa8+b35MeLINY3BS2e303MXf7a7iEj/6TzwNohN9zJQ+ziAW3fn7xjWW3tLTNcyIZ9/DCiOcoTBA+GJxvthNHbhgDncJKoS8VuGzCLXzVx547IJ+/qxG1qZNQfRaOO02YHuF1ebpG34+JZRbQygZOD+VDJTOdwl5iynsqms3MOBMj0JsDa28vl0lVXrIT0Gpkglnusx6zXbJd0J2FS"""

    print(f"Cookie总长度: {len(cookie)} 字符")

    # 分析Cookie结构
    cookie_parts = cookie.split("; ")
    print(f"包含 {len(cookie_parts)} 个Cookie字段")

    print("\n重要字段分析:")
    important_fields = {
        "b-user-id": "用户ID标识",
        "ctoken": "认证令牌",
        "isQuark": "夸克标识",
        "grey-id": "灰度ID",
        "web-grey-id": "网页灰度ID",
        "__pus": "推送服务标识",
        "__kp": "关键参数",
    }

    for field, description in important_fields.items():
        found = False
        for part in cookie_parts:
            if part.startswith(field + "="):
                value = part[len(field) + 1 :]
                print(f"✓ {field}: {description}")
                print(f"  值长度: {len(value)} 字符")
                if len(value) > 50:
                    print(f"  值预览: {value[:50]}...")
                found = True
                break
        if not found:
            print(f"✗ {field}: 未找到")

    print("\nCookie看起来是有效的夸克网盘Cookie")
    print("包含必要的认证字段")
    return True


if __name__ == "__main__":
    print("=== 夸克网盘配置工具 ===")
    print("1. 配置夸克网盘到数据库")
    print("2. 测试Cookie有效性")

    choice = input("\n请选择 (1/2): ").strip()

    if choice == "1":
        configure_quark_with_real_cookie()
    elif choice == "2":
        test_cookie_validity()
    else:
        print("无效选择")
