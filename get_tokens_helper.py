#!/usr/bin/env python3
"""
云盘token获取助手
提供获取各平台token的详细指引
"""

def show_baidu_guide():
    print("\n" + "="*60)
    print("百度网盘 refresh_token 获取指南")
    print("="*60)
    print("""
方法一：使用 bypy 工具（推荐）
1. 安装: pip install bypy
2. 运行: bypy info
3. 按提示完成授权
4. 在 ~/.bypy/bypy.json 中找到 refresh_token

方法二：手动获取
1. 访问: https://pan.baidu.com/union/document/entrance
2. 注册开发者账号并创建应用
3. 使用授权URL获取code
4. 使用code换取refresh_token

方法三：使用在线工具
搜索 "百度网盘refresh_token在线获取" 使用现成工具
""")

def show_aliyun_guide():
    print("\n" + "="*60)
    print("阿里云盘 refresh_token 获取指南")
    print("="*60)
    print("""
方法一：官方扫码（推荐）
1. 访问: https://www.aliyundrive.com/developer
2. 创建应用
3. 使用以下授权URL（替换YOUR_CLIENT_ID）:
   https://auth.aliyundrive.com/v2/oauth/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=https://www.aliyundrive.com/sign/callback&response_type=code&scope=user:base,file:all:read,file:all:write

方法二：使用现成工具
搜索 "阿里云盘refresh_token获取" 使用在线工具

方法三：APP内获取
1. 在阿里云盘APP中分享文件
2. 复制分享链接
3. 某些工具可以从分享链接中提取token
""")

def show_quark_guide():
    print("\n" + "="*60)
    print("夸克网盘 cookie 获取指南")
    print("="*60)
    print("""
方法一：浏览器开发者工具
1. 打开: https://pan.quark.cn
2. 按F12打开开发者工具
3. 切换到 Network 标签
4. 登录夸克网盘
5. 找到任意请求，复制Request Headers中的Cookie

关键cookie字段:
- QUTHK
- QUTHKL  
- QUTHKS
- QUTHKM
- QUTOKEN

方法二：使用浏览器插件
1. 安装 EditThisCookie 插件
2. 登录夸克网盘
3. 导出cookie并找到上述关键字段
""")

def show_quick_links():
    print("\n" + "="*60)
    print("快速获取链接")
    print("="*60)
    print("""
百度网盘在线工具:
- https://tool.bitefu.net/baidu/
- https://openapi.baidu.com/oauth/2.0/authorize?response_type=code&client_id=iYCeC9g08h5vuP9UqvPHKKSVrKFXGa1v&redirect_uri=oob&scope=basic,netdisk

阿里云盘在线工具:
- https://alist.nn.ci/tool/aliyundrive/request.html
- https://www.aliyundrive.com/developer

夸克网盘:
- 必须通过网页版手动获取cookie
""")

def main():
    print("云盘平台Token获取助手")
    print("="*60)
    
    while True:
        print("\n选择要获取的平台:")
        print("1. 百度网盘 (refresh_token)")
        print("2. 阿里云盘 (refresh_token)")
        print("3. 夸克网盘 (cookie)")
        print("4. 查看所有快速链接")
        print("5. 退出")
        
        choice = input("\n请选择 (1-5): ").strip()
        
        if choice == '1':
            show_baidu_guide()
        elif choice == '2':
            show_aliyun_guide()
        elif choice == '3':
            show_quark_guide()
        elif choice == '4':
            show_quick_links()
        elif choice == '5':
            print("再见!")
            break
        else:
            print("无效选择，请重新输入")

if __name__ == "__main__":
    main()