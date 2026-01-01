#!/usr/bin/env python3
"""
批量云盘登录脚本 - 简化操作版本
一次性配置多个云盘平台
"""

import json
import os

def create_simple_config():
    """创建简化的配置向导"""
    print("批量云盘登录配置向导")
    print("=" * 50)
    
    config = {}
    
    # 百度网盘配置
    print("\n1. 百度网盘配置")
    print("提示: 需要获取 refresh_token")
    baidu_refresh = input("百度网盘 refresh_token (留空跳过): ").strip()
    if baidu_refresh:
        config['baidu'] = {
            "driver": "BaiduNetdisk",
            "mount_path": "/baidu",
            "refresh_token": baidu_refresh
        }
    
    # 阿里云盘配置
    print("\n2. 阿里云盘配置")
    print("提示: 需要获取 refresh_token")
    aliyun_refresh = input("阿里云盘 refresh_token (留空跳过): ").strip()
    if aliyun_refresh:
        config['aliyun'] = {
            "driver": "Aliyundrive",
            "mount_path": "/aliyun",
            "refresh_token": aliyun_refresh
        }
    
    # 夸克网盘配置
    print("\n3. 夸克网盘配置")
    print("提示: 需要获取登录cookie")
    quark_cookie = input("夸克网盘 cookie (留空跳过): ").strip()
    if quark_cookie:
        config['quark'] = {
            "driver": "Quark",
            "mount_path": "/quark",
            "cookie": quark_cookie
        }
    
    return config

def generate_openlist_config(config):
    """生成OpenList存储配置"""
    storages = []
    
    for platform, cfg in config.items():
        storage = {
            "mount_path": cfg["mount_path"],
            "driver": cfg["driver"],
            "order": len(storages) + 1,
            "addition": {}
        }
        
        if platform == 'baidu':
            storage["addition"] = {
                "refresh_token": cfg["refresh_token"],
                "root_path": "/"
            }
        elif platform == 'aliyun':
            storage["addition"] = {
                "refresh_token": cfg["refresh_token"],
                "root_id": "root"
            }
        elif platform == 'quark':
            storage["addition"] = {
                "cookie": cfg["cookie"],
                "root_id": "0"
            }
        
        storages.append(storage)
    
    return {"storages": storages}

def main():
    """主函数"""
    print("批量云盘登录配置工具")
    print("支持: 百度网盘 | 阿里云盘 | 夸克网盘")
    print()
    
    # 创建配置
    config = create_simple_config()
    
    if not config:
        print("\n没有配置任何云盘，退出")
        return
    
    # 显示配置摘要
    print("\n" + "=" * 50)
    print("配置摘要:")
    for platform in config:
        print(f"  ✓ {platform}")
    
    # 生成OpenList配置
    openlist_config = generate_openlist_config(config)
    
    # 保存配置
    config_file = "cloud_disk_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    openlist_file = "openlist_storages.json"
    with open(openlist_file, 'w', encoding='utf-8') as f:
        json.dump(openlist_config, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 配置已保存到 {config_file}")
    print(f"✓ OpenList存储配置已生成到 {openlist_file}")
    print("\n使用说明:")
    print("1. 将 openlist_storages.json 导入到OpenList")
    print("2. 启动OpenList服务")
    print("3. 通过Web界面管理云盘文件")
    
    # 显示获取token的帮助信息
    print("\n获取帮助:")
    print("• 百度网盘 refresh_token: 参考官方API文档或使用第三方工具")
    print("• 阿里云盘 refresh_token: 使用官方APP扫码或第三方工具")
    print("• 夸克网盘 cookie: 登录网页版后在开发者工具中复制")

if __name__ == "__main__":
    main()