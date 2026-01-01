#!/usr/bin/env python3
"""
简化版云盘Token获取工具
使用AList获取阿里云盘/百度网盘token + 手动获取夸克cookie
"""

import os
import json
import subprocess
import time

def install_and_run_alist():
    """安装并运行AList"""
    print("\n=== 安装和运行AList ===")
    
    # 检查是否已安装
    if os.path.exists("./alist"):
        print("检测到已安装的AList")
    else:
        print("正在安装AList...")
        try:
            # 下载安装脚本
            result = subprocess.run([
                'curl', '-fsSL', 'https://alist.nn.ci/v3.sh', '-o', 'alist_install.sh'
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print("下载安装脚本失败，请检查网络连接")
                return False
            
            # 安装AList
            result = subprocess.run([
                'bash', 'alist_install.sh', 'install'
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print("安装失败:", result.stderr)
                return False
            
            print("✓ AList安装完成")
            
        except Exception as e:
            print(f"安装过程中出错: {e}")
            return False
    
    # 获取管理员密码
    print("\n获取AList管理员密码...")
    result = subprocess.run(['./alist', 'admin'], capture_output=True, text=True)
    if result.returncode == 0:
        print(result.stdout)
    
    # 启动AList
    print("\n启动AList服务...")
    print("AList将在后台运行，访问 http://127.0.0.1:5244")
    print("用户名: admin，密码见上方输出")
    
    # 在后台启动AList
    subprocess.Popen(['./alist', 'server'])
    
    print("\n等待服务启动...")
    time.sleep(3)
    
    return True

def get_tokens_with_alist():
    """使用AList获取token"""
    print("\n=== 使用AList获取云盘Token ===")
    print("请按以下步骤操作:")
    print("""
1. 访问: http://127.0.0.1:5244
2. 使用admin账号登录
3. 进入'管理' -> '存储' -> '添加'
4. 选择对应云盘:
   - 阿里云盘: 点击'获取令牌'按钮，扫码授权
   - 百度网盘: 点击'获取令牌'按钮，按提示操作
5. 复制获取到的token
""")
    
    tokens = {}
    
    # 阿里云盘
    aliyun_token = input("\n请输入从AList获取的阿里云盘refresh_token: ").strip()
    if aliyun_token:
        tokens['aliyun'] = aliyun_token
    
    # 百度网盘  
    baidu_token = input("请输入从AList获取的百度网盘refresh_token: ").strip()
    if baidu_token:
        tokens['baidu'] = baidu_token
    
    return tokens

def get_quark_cookie_simple():
    """简化版夸克cookie获取"""
    print("\n=== 获取夸克网盘Cookie ===")
    print("请按以下步骤操作:")
    print("""
1. 打开Chrome/Edge浏览器
2. 访问: https://pan.quark.cn
3. 登录您的夸克账号
4. 按F12打开开发者工具
5. 按F5刷新页面
6. 在Network标签中找到第一个请求
7. 在Headers中找到Cookie并复制

或者使用更简单的方法:
1. 登录夸克网盘后
2. 在地址栏输入: javascript:alert(document.cookie)
3. 复制弹出的cookie内容
""")
    
    cookie = input("\n请输入获取到的夸克网盘cookie: ").strip()
    return cookie

def generate_final_config(tokens):
    """生成最终配置文件"""
    print("\n=== 生成配置文件 ===")
    
    storages = []
    
    if tokens.get('aliyun'):
        storages.append({
            "mount_path": "/aliyun",
            "driver": "Aliyundrive", 
            "order": 1,
            "addition": {
                "refresh_token": tokens['aliyun'],
                "root_id": "root"
            }
        })
        print("✓ 已添加阿里云盘配置")
    
    if tokens.get('baidu'):
        storages.append({
            "mount_path": "/baidu",
            "driver": "BaiduNetdisk",
            "order": 2, 
            "addition": {
                "refresh_token": tokens['baidu'],
                "root_path": "/"
            }
        })
        print("✓ 已添加百度网盘配置")
    
    if tokens.get('quark'):
        storages.append({
            "mount_path": "/quark", 
            "driver": "Quark",
            "order": 3,
            "addition": {
                "cookie": tokens['quark'],
                "root_id": "0"
            }
        })
        print("✓ 已添加夸克网盘配置")
    
    if not storages:
        print("⚠ 没有添加任何存储配置")
        return
    
    # 生成OpenList配置
    openlist_config = {"storages": storages}
    
    with open('final_openlist_config.json', 'w', encoding='utf-8') as f:
        json.dump(openlist_config, f, ensure_ascii=False, indent=2)
    
    # 生成原始token配置
    token_config = {}
    for platform, token in tokens.items():
        token_config[platform] = {
            "driver": storages[0]['driver'] if storages else "",
            "mount_path": f"/{platform}",
            "token": token
        }
    
    with open('cloud_tokens_backup.json', 'w', encoding='utf-8') as f:
        json.dump(token_config, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 配置文件已生成:")
    print(f"  - final_openlist_config.json (用于OpenList)")
    print(f"  - cloud_tokens_backup.json (token备份)")
    
    return openlist_config

def show_usage():
    """显示使用说明"""
    print("\n" + "="*50)
    print("使用说明")
    print("="*50)
    print("""
1. 将 final_openlist_config.json 导入OpenList:
   - 在OpenList管理界面导入存储配置
   - 或直接替换OpenList的配置文件

2. 启动OpenList服务

3. 访问OpenList Web界面管理文件

4. 如果token过期:
   - 重新运行此脚本获取新token
   - 更新配置文件
   - 重启OpenList服务
""")

def main():
    """主函数"""
    print("云盘Token一键获取工具")
    print("使用AList + 手动获取夸克cookie")
    print("=" * 50)
    
    tokens = {}
    
    # 步骤1: 安装运行AList
    print("\n步骤1: 设置AList")
    if install_and_run_alist():
        input("\nAList已启动，按回车继续获取token...")
        
        # 步骤2: 使用AList获取token
        print("\n步骤2: 获取阿里云盘和百度网盘token")
        alist_tokens = get_tokens_with_alist()
        tokens.update(alist_tokens)
    else:
        print("AList设置失败，跳过AList获取方式")
    
    # 步骤3: 获取夸克cookie
    print("\n步骤3: 获取夸克网盘cookie")
    quark_cookie = get_quark_cookie_simple()
    if quark_cookie:
        tokens['quark'] = quark_cookie
    
    # 步骤4: 生成配置
    if tokens:
        print("\n步骤4: 生成配置文件")
        generate_final_config(tokens)
        show_usage()
    else:
        print("\n⚠ 没有获取到任何token，请重新运行脚本")
    
    # 清理
    if os.path.exists("alist_install.sh"):
        os.remove("alist_install.sh")

if __name__ == "__main__":
    main()