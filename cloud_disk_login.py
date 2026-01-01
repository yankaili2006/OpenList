#!/usr/bin/env python3
"""
云盘平台自动登录脚本
支持百度网盘、阿里云盘、夸克网盘等平台的简化登录
"""

import json
import os
import sys
import requests
import time
from typing import Dict, Any, Optional

class CloudDiskLogin:
    def __init__(self):
        self.config_file = "cloud_disk_config.json"
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
        return {}
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            print(f"配置已保存到 {self.config_file}")
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def baidu_netdisk_login(self) -> bool:
        """百度网盘登录"""
        print("\n=== 百度网盘登录 ===")
        
        if 'baidu' in self.config and self.config['baidu'].get('access_token'):
            print("检测到已保存的百度网盘配置")
            if input("是否使用现有配置? (y/n): ").lower() == 'y':
                return True
        
        print("""
百度网盘登录说明:
1. 需要获取 refresh_token
2. 可以通过以下方式获取:
   - 使用浏览器开发者工具
   - 使用第三方工具获取
   - 参考官方API文档
""")
        
        refresh_token = input("请输入百度网盘 refresh_token: ").strip()
        if not refresh_token:
            print("refresh_token 不能为空")
            return False
            
        # 这里可以添加实际的登录验证逻辑
        # 目前只是保存配置
        if 'baidu' not in self.config:
            self.config['baidu'] = {}
        
        self.config['baidu']['refresh_token'] = refresh_token
        self.config['baidu']['driver'] = 'BaiduNetdisk'
        self.config['baidu']['mount_path'] = '/baidu'
        
        print("百度网盘配置已保存")
        return True
    
    def aliyundrive_login(self) -> bool:
        """阿里云盘登录"""
        print("\n=== 阿里云盘登录 ===")
        
        if 'aliyun' in self.config and self.config['aliyun'].get('refresh_token'):
            print("检测到已保存的阿里云盘配置")
            if input("是否使用现有配置? (y/n): ").lower() == 'y':
                return True
        
        print("""
阿里云盘登录说明:
1. 需要获取 refresh_token
2. 可以通过以下方式获取:
   - 使用阿里云盘官方APP扫码
   - 使用第三方工具获取refresh_token
   - 参考官方API文档
""")
        
        refresh_token = input("请输入阿里云盘 refresh_token: ").strip()
        if not refresh_token:
            print("refresh_token 不能为空")
            return False
            
        if 'aliyun' not in self.config:
            self.config['aliyun'] = {}
        
        self.config['aliyun']['refresh_token'] = refresh_token
        self.config['aliyun']['driver'] = 'Aliyundrive'
        self.config['aliyun']['mount_path'] = '/aliyun'
        
        print("阿里云盘配置已保存")
        return True
    
    def quark_login(self) -> bool:
        """夸克网盘登录"""
        print("\n=== 夸克网盘登录 ===")
        
        if 'quark' in self.config and self.config['quark'].get('cookie'):
            print("检测到已保存的夸克网盘配置")
            if input("是否使用现有配置? (y/n): ").lower() == 'y':
                return True
        
        print("""
夸克网盘登录说明:
1. 需要获取登录cookie
2. 可以通过以下方式获取:
   - 登录夸克网盘网页版
   - 在浏览器开发者工具中复制cookie
   - 注意cookie的有效期
""")
        
        cookie = input("请输入夸克网盘 cookie: ").strip()
        if not cookie:
            print("cookie 不能为空")
            return False
            
        if 'quark' not in self.config:
            self.config['quark'] = {}
        
        self.config['quark']['cookie'] = cookie
        self.config['quark']['driver'] = 'Quark'
        self.config['quark']['mount_path'] = '/quark'
        
        print("夸克网盘配置已保存")
        return True
    
    def generate_openlist_config(self):
        """生成OpenList配置文件"""
        if not self.config:
            print("没有可用的配置")
            return
            
        print("\n=== 生成OpenList配置 ===")
        
        storages = []
        for platform, config in self.config.items():
            if platform in ['baidu', 'aliyun', 'quark']:
                storage = {
                    "mount_path": config.get('mount_path', f'/{platform}'),
                    "driver": config.get('driver', ''),
                    "addition": {}
                }
                
                if platform == 'baidu':
                    storage["addition"] = {
                        "refresh_token": config.get('refresh_token', ''),
                        "root_path": "/"
                    }
                elif platform == 'aliyun':
                    storage["addition"] = {
                        "refresh_token": config.get('refresh_token', ''),
                        "root_id": "root"
                    }
                elif platform == 'quark':
                    storage["addition"] = {
                        "cookie": config.get('cookie', ''),
                        "root_id": "0"
                    }
                
                storages.append(storage)
        
        if storages:
            config_output = {
                "storages": storages
            }
            
            output_file = "openlist_storages.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(config_output, f, ensure_ascii=False, indent=2)
            print(f"OpenList存储配置已生成到 {output_file}")
            print("您可以将此配置导入到OpenList中使用")
        else:
            print("没有有效的存储配置")
    
    def show_menu(self):
        """显示主菜单"""
        while True:
            print("\n" + "="*50)
            print("云盘平台登录管理")
            print("="*50)
            print("1. 百度网盘登录")
            print("2. 阿里云盘登录") 
            print("3. 夸克网盘登录")
            print("4. 查看当前配置")
            print("5. 生成OpenList配置")
            print("6. 保存配置")
            print("7. 退出")
            print("="*50)
            
            choice = input("请选择操作 (1-7): ").strip()
            
            if choice == '1':
                self.baidu_netdisk_login()
            elif choice == '2':
                self.aliyundrive_login()
            elif choice == '3':
                self.quark_login()
            elif choice == '4':
                self.show_current_config()
            elif choice == '5':
                self.generate_openlist_config()
            elif choice == '6':
                self.save_config()
            elif choice == '7':
                if input("是否保存配置? (y/n): ").lower() == 'y':
                    self.save_config()
                print("再见!")
                break
            else:
                print("无效选择，请重新输入")
    
    def show_current_config(self):
        """显示当前配置"""
        print("\n=== 当前配置 ===")
        if not self.config:
            print("暂无配置")
            return
            
        for platform, config in self.config.items():
            print(f"\n{platform.upper()}:")
            for key, value in config.items():
                if key in ['refresh_token', 'cookie']:
                    # 敏感信息只显示部分
                    if value:
                        masked = value[:8] + "****" + value[-4:] if len(value) > 12 else "****"
                        print(f"  {key}: {masked}")
                    else:
                        print(f"  {key}: (未设置)")
                else:
                    print(f"  {key}: {value}")

def main():
    """主函数"""
    print("云盘平台自动登录脚本")
    print("支持百度网盘、阿里云盘、夸克网盘")
    
    login_manager = CloudDiskLogin()
    login_manager.show_menu()

if __name__ == "__main__":
    main()