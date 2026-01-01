#!/usr/bin/env python3
"""
使用开源工具获取云盘token
集成多个开源项目的token获取功能
"""

import os
import sys
import subprocess
import json
import requests

def check_dependencies():
    """检查依赖"""
    dependencies = ['curl', 'wget', 'git']
    missing = []
    
    for dep in dependencies:
        if subprocess.run(['which', dep], capture_output=True).returncode != 0:
            missing.append(dep)
    
    if missing:
        print(f"缺少依赖: {', '.join(missing)}")
        print("请先安装这些工具")
        return False
    return True

def get_aliyun_token_opensource():
    """使用开源工具获取阿里云盘token"""
    print("\n=== 获取阿里云盘Token ===")
    
    # 方法1: 使用在线工具
    print("方法1: 使用AList在线工具")
    print("访问: https://alist.nn.ci/tool/aliyundrive/request.html")
    print("扫码授权即可获取refresh_token")
    
    # 方法2: 使用命令行工具
    print("\n方法2: 使用aliyundrive-token工具")
    print("运行以下命令:")
    print("""
git clone https://github.com/mrabit/aliyundrive-token.git
cd aliyundrive-token
python3 get_token.py
""")
    
    # 方法3: 直接API调用
    print("\n方法3: 手动获取")
    print("1. 访问: https://www.aliyundrive.com/developer")
    print("2. 创建应用")
    print("3. 使用以下URL授权:")
    print("https://auth.aliyundrive.com/v2/oauth/authorize?client_id=4d7bcac4e5b14c68a4a1c7b8f82f6b1f&redirect_uri=https://www.aliyundrive.com/sign/callback&response_type=code&scope=user:base,file:all:read,file:all:write")
    
    refresh_token = input("\n请输入获取到的阿里云盘refresh_token: ").strip()
    return refresh_token

def get_baidu_token_opensource():
    """使用开源工具获取百度网盘token"""
    print("\n=== 获取百度网盘Token ===")
    
    # 方法1: 使用bypy
    print("方法1: 使用bypy工具")
    print("运行以下命令:")
    print("""
pip install bypy
bypy info
""")
    print("按提示授权，然后在 ~/.bypy/bypy.json 中找到refresh_token")
    
    # 方法2: 使用BaiduPCS-Go
    print("\n方法2: 使用BaiduPCS-Go")
    print("运行以下命令:")
    print("""
wget https://github.com/qjfoidnh/BaiduPCS-Go/releases/latest/download/BaiduPCS-Go-v3.9.2-linux-amd64.zip
unzip BaiduPCS-Go-v3.9.2-linux-amd64.zip
./BaiduPCS-Go login
""")
    
    # 方法3: 在线工具替代
    print("\n方法3: 使用其他在线工具")
    print("搜索: '百度网盘refresh_token在线获取'")
    print("或访问: https://openapi.baidu.com/oauth/2.0/authorize?response_type=code&client_id=iYCeC9g08h5vuP9UqvPHKKSVrKFXGa1v&redirect_uri=oob&scope=basic,netdisk")
    
    refresh_token = input("\n请输入获取到的百度网盘refresh_token: ").strip()
    return refresh_token

def get_quark_cookie_manual():
    """获取夸克网盘cookie"""
    print("\n=== 获取夸克网盘Cookie ===")
    print("夸克网盘目前没有很好的开源工具，需要手动获取:")
    print("""
1. 访问: https://pan.quark.cn
2. 登录账号
3. 按F12打开开发者工具
4. 切换到 Network 标签
5. 刷新页面
6. 找到任意请求，复制Request Headers中的Cookie

关键cookie字段:
- QUTHK
- QUTHKL  
- QUTHKS
- QUTHKM
- QUTOKEN
""")
    
    cookie = input("请输入获取到的夸克网盘cookie: ").strip()
    return cookie

def install_alist():
    """安装AList"""
    print("\n=== 安装AList ===")
    print("AList是一个支持多种存储的文件列表程序")
    print("内置了方便的token获取工具")
    
    if input("是否安装AList? (y/n): ").lower() == 'y':
        try:
            # 下载安装脚本
            subprocess.run([
                'curl', '-fsSL', 'https://alist.nn.ci/v3.sh'
            ], check=True)
            
            # 安装AList
            subprocess.run([
                'bash', '-c', 'curl -fsSL "https://alist.nn.ci/v3.sh" | bash -s install'
            ], check=True)
            
            print("\nAList安装完成!")
            print("启动命令: ./alist server")
            print("访问地址: http://127.0.0.1:5244")
            print("在管理后台可以方便地获取各种云盘token")
            
        except subprocess.CalledProcessError as e:
            print(f"安装失败: {e}")

def generate_openlist_config(tokens):
    """生成OpenList配置"""
    storages = []
    
    if tokens.get('aliyun'):
        storages.append({
            "mount_path": "/aliyun",
            "driver": "Aliyundrive",
            "order": len(storages) + 1,
            "addition": {
                "refresh_token": tokens['aliyun'],
                "root_id": "root"
            }
        })
    
    if tokens.get('baidu'):
        storages.append({
            "mount_path": "/baidu", 
            "driver": "BaiduNetdisk",
            "order": len(storages) + 1,
            "addition": {
                "refresh_token": tokens['baidu'],
                "root_path": "/"
            }
        })
    
    if tokens.get('quark'):
        storages.append({
            "mount_path": "/quark",
            "driver": "Quark", 
            "order": len(storages) + 1,
            "addition": {
                "cookie": tokens['quark'],
                "root_id": "0"
            }
        })
    
    config = {"storages": storages}
    
    with open('opensource_tokens_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ OpenList配置已生成到 opensource_tokens_config.json")
    return config

def main():
    """主函数"""
    print("开源云盘Token获取工具")
    print("=" * 50)
    
    if not check_dependencies():
        return
    
    tokens = {}
    
    while True:
        print("\n选择操作:")
        print("1. 获取阿里云盘Token")
        print("2. 获取百度网盘Token") 
        print("3. 获取夸克网盘Cookie")
        print("4. 安装AList(推荐)")
        print("5. 生成OpenList配置")
        print("6. 退出")
        
        choice = input("\n请选择 (1-6): ").strip()
        
        if choice == '1':
            token = get_aliyun_token_opensource()
            if token:
                tokens['aliyun'] = token
        elif choice == '2':
            token = get_baidu_token_opensource()
            if token:
                tokens['baidu'] = token
        elif choice == '3':
            cookie = get_quark_cookie_manual()
            if cookie:
                tokens['quark'] = cookie
        elif choice == '4':
            install_alist()
        elif choice == '5':
            if tokens:
                generate_openlist_config(tokens)
            else:
                print("没有获取到任何token")
        elif choice == '6':
            break
        else:
            print("无效选择")
    
    print("\n使用说明:")
    print("1. 将生成的配置文件导入OpenList")
    print("2. 启动OpenList服务")
    print("3. 通过Web界面管理云盘文件")

if __name__ == "__main__":
    main()