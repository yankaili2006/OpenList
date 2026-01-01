#!/usr/bin/env python3
"""
OpenList云盘Token管理工具
用于现有OpenList实例的token获取和配置更新
"""

import json
import os
import sqlite3
import subprocess
import time
from pathlib import Path

def find_openlist_config():
    """查找OpenList配置文件"""
    print("\n=== 查找OpenList配置 ===")
    
    # 常见的OpenList配置路径
    config_paths = [
        "./data/config.db",  # 当前目录
        "./config.db",
        "~/.openlist/config.db",
        "/etc/openlist/config.db",
        "/usr/local/openlist/config.db"
    ]
    
    for path in config_paths:
        expanded_path = os.path.expanduser(path)
        if os.path.exists(expanded_path):
            print(f"✓ 找到配置文件: {expanded_path}")
            return expanded_path
    
    # 如果没找到，询问用户
    custom_path = input("未找到配置文件，请输入OpenList配置数据库路径: ").strip()
    if custom_path and os.path.exists(custom_path):
        return custom_path
    
    return None

def get_current_storages(config_path):
    """获取当前存储配置"""
    try:
        conn = sqlite3.connect(config_path)
        cursor = conn.cursor()
        
        # 查询存储配置
        cursor.execute("SELECT id, mount_path, driver, addition FROM storages")
        storages = cursor.fetchall()
        
        conn.close()
        
        current_config = {}
        for storage_id, mount_path, driver, addition in storages:
            addition_json = json.loads(addition) if addition else {}
            current_config[storage_id] = {
                "mount_path": mount_path,
                "driver": driver,
                "addition": addition_json
            }
        
        return current_config
    except Exception as e:
        print(f"读取配置失败: {e}")
        return {}

def update_storage_token(config_path, storage_id, new_addition):
    """更新存储配置的token"""
    try:
        conn = sqlite3.connect(config_path)
        cursor = conn.cursor()
        
        # 更新配置
        cursor.execute(
            "UPDATE storages SET addition = ? WHERE id = ?",
            (json.dumps(new_addition), storage_id)
        )
        
        conn.commit()
        conn.close()
        
        print(f"✓ 已更新存储 {storage_id} 的配置")
        return True
    except Exception as e:
        print(f"更新配置失败: {e}")
        return False

def add_new_storage(config_path, storage_config):
    """添加新的存储配置"""
    try:
        conn = sqlite3.connect(config_path)
        cursor = conn.cursor()
        
        # 获取最大order值
        cursor.execute("SELECT MAX(\"order\") FROM storages")
        max_order = cursor.fetchone()[0] or 0
        
        # 插入新存储
        cursor.execute("""
            INSERT INTO storages (mount_path, driver, addition, \"order\", status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            storage_config["mount_path"],
            storage_config["driver"],
            json.dumps(storage_config["addition"]),
            max_order + 1,
            "work"
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✓ 已添加新存储: {storage_config['mount_path']}")
        return True
    except Exception as e:
        print(f"添加存储失败: {e}")
        return False

def get_aliyun_token_with_alist():
    """使用AList获取阿里云盘token"""
    print("\n=== 获取阿里云盘Token ===")
    print("推荐使用AList在线工具:")
    print("1. 访问: https://alist.nn.ci/tool/aliyundrive/request.html")
    print("2. 扫码授权")
    print("3. 复制refresh_token")
    
    refresh_token = input("\n请输入阿里云盘refresh_token: ").strip()
    return refresh_token

def get_baidu_token_with_alist():
    """使用AList获取百度网盘token"""
    print("\n=== 获取百度网盘Token ===")
    print("推荐方法:")
    print("1. 访问AList管理界面 (如果已安装)")
    print("2. 或使用: pip install bypy && bypy info")
    print("3. 在 ~/.bypy/bypy.json 中找到refresh_token")
    
    refresh_token = input("\n请输入百度网盘refresh_token: ").strip()
    return refresh_token

def get_quark_cookie():
    """获取夸克网盘cookie"""
    print("\n=== 获取夸克网盘Cookie ===")
    print("手动获取步骤:")
    print("1. 访问: https://pan.quark.cn")
    print("2. 登录账号")
    print("3. 按F12 → Network → 复制Cookie")
    
    cookie = input("\n请输入夸克网盘cookie: ").strip()
    return cookie

def restart_openlist():
    """重启OpenList服务"""
    print("\n=== 重启OpenList服务 ===")
    
    # 尝试常见的重启命令
    restart_commands = [
        ["systemctl", "restart", "openlist"],
        ["service", "openlist", "restart"],
        ["pkill", "-f", "openlist"],
        ["./openlist", "restart"]
    ]
    
    for cmd in restart_commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ OpenList服务已重启")
                return True
        except:
            continue
    
    print("⚠ 无法自动重启OpenList，请手动重启服务")
    return False

def manage_existing_storage(config_path, storage_id, storage_info):
    """管理现有存储"""
    print(f"\n管理存储: {storage_info['mount_path']} ({storage_info['driver']})")
    
    current_addition = storage_info['addition']
    
    if storage_info['driver'] == 'Aliyundrive':
        current_token = current_addition.get('refresh_token', '')
        if current_token:
            print(f"当前token: {current_token[:10]}...{current_token[-4:]}")
        
        if input("是否更新阿里云盘token? (y/n): ").lower() == 'y':
            new_token = get_aliyun_token_with_alist()
            if new_token:
                current_addition['refresh_token'] = new_token
                update_storage_token(config_path, storage_id, current_addition)
                return True
    
    elif storage_info['driver'] == 'BaiduNetdisk':
        current_token = current_addition.get('refresh_token', '')
        if current_token:
            print(f"当前token: {current_token[:10]}...{current_token[-4:]}")
        
        if input("是否更新百度网盘token? (y/n): ").lower() == 'y':
            new_token = get_baidu_token_with_alist()
            if new_token:
                current_addition['refresh_token'] = new_token
                update_storage_token(config_path, storage_id, current_addition)
                return True
    
    elif storage_info['driver'] == 'Quark':
        current_cookie = current_addition.get('cookie', '')
        if current_cookie:
            print(f"当前cookie: {current_cookie[:20]}...")
        
        if input("是否更新夸克网盘cookie? (y/n): ").lower() == 'y':
            new_cookie = get_quark_cookie()
            if new_cookie:
                current_addition['cookie'] = new_cookie
                update_storage_token(config_path, storage_id, current_addition)
                return True
    
    return False

def add_new_cloud_storage(config_path):
    """添加新的云盘存储"""
    print("\n=== 添加新云盘存储 ===")
    
    print("选择云盘类型:")
    print("1. 阿里云盘")
    print("2. 百度网盘")
    print("3. 夸克网盘")
    
    choice = input("请选择 (1-3): ").strip()
    
    mount_path = input("请输入挂载路径 (例如: /aliyun): ").strip()
    if not mount_path.startswith('/'):
        mount_path = '/' + mount_path
    
    if choice == '1':
        token = get_aliyun_token_with_alist()
        if token:
            storage_config = {
                "mount_path": mount_path,
                "driver": "Aliyundrive",
                "addition": {
                    "refresh_token": token,
                    "root_id": "root"
                }
            }
            return add_new_storage(config_path, storage_config)
    
    elif choice == '2':
        token = get_baidu_token_with_alist()
        if token:
            storage_config = {
                "mount_path": mount_path,
                "driver": "BaiduNetdisk",
                "addition": {
                    "refresh_token": token,
                    "root_path": "/"
                }
            }
            return add_new_storage(config_path, storage_config)
    
    elif choice == '3':
        cookie = get_quark_cookie()
        if cookie:
            storage_config = {
                "mount_path": mount_path,
                "driver": "Quark",
                "addition": {
                    "cookie": cookie,
                    "root_id": "0"
                }
            }
            return add_new_storage(config_path, storage_config)
    
    return False

def main():
    """主函数"""
    print("OpenList云盘Token管理工具")
    print("=" * 50)
    
    # 查找配置文件
    config_path = find_openlist_config()
    if not config_path:
        print("❌ 未找到OpenList配置文件，请确保OpenList已正确安装")
        return
    
    # 获取当前配置
    current_storages = get_current_storages(config_path)
    
    while True:
        print("\n" + "="*50)
        print("OpenList存储管理")
        print("="*50)
        
        if current_storages:
            print("当前存储配置:")
            for storage_id, info in current_storages.items():
                print(f"  [{storage_id}] {info['mount_path']} - {info['driver']}")
        else:
            print("暂无存储配置")
        
        print("\n操作选项:")
        print("1. 管理现有存储 (更新token)")
        print("2. 添加新云盘存储")
        print("3. 重启OpenList服务")
        print("4. 退出")
        
        choice = input("\n请选择 (1-4): ").strip()
        
        if choice == '1' and current_storages:
            storage_id = input("请输入要管理的存储ID: ").strip()
            if storage_id in current_storages:
                if manage_existing_storage(config_path, storage_id, current_storages[storage_id]):
                    # 更新后重新加载配置
                    current_storages = get_current_storages(config_path)
                    if input("是否重启OpenList服务? (y/n): ").lower() == 'y':
                        restart_openlist()
            else:
                print("无效的存储ID")
        
        elif choice == '2':
            if add_new_cloud_storage(config_path):
                # 更新后重新加载配置
                current_storages = get_current_storages(config_path)
                if input("是否重启OpenList服务? (y/n): ").lower() == 'y':
                    restart_openlist()
        
        elif choice == '3':
            restart_openlist()
        
        elif choice == '4':
            break
        
        else:
            print("无效选择")

if __name__ == "__main__":
    main()