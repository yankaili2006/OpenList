#!/usr/bin/env python3
"""
获取百度网盘refresh_token的详细指南和工具
"""

import webbrowser
import json
import os


def method1_third_party_tool():
    """方法一：使用第三方工具（最简单）"""
    print("\n=== 方法一：使用第三方工具（推荐） ===")
    print("\n1. 访问以下网站获取refresh_token:")
    print("   - https://alist.nn.ci/tool/baidu")
    print("   - https://tool.nn.ci/baidu/")
    print("   - https://openapi.baidu.com/oauth/2.0/authorize")

    print("\n2. 操作步骤:")
    print("   a. 打开上述任意一个网站")
    print("   b. 点击'获取授权'或'登录'按钮")
    print("   c. 使用百度账号登录")
    print("   d. 授权应用访问百度网盘")
    print("   e. 复制获取到的refresh_token")

    print("\n3. refresh_token格式示例:")
    print("   123.abc456def789ghi012jkl345mno678pqr901stu234")
    print("   通常以'123.'开头，长度约40-50个字符")

    # 尝试打开网页
    open_browser = input("\n是否打开获取页面? (y/n): ").strip().lower()
    if open_browser == "y":
        webbrowser.open("https://alist.nn.ci/tool/baidu")


def method2_official_api():
    """方法二：使用官方API（需要开发者账号）"""
    print("\n=== 方法二：使用官方API ===")
    print("\n需要百度开发者账号，适合开发者使用")

    print("\n1. 注册百度开发者:")
    print("   访问: https://developer.baidu.com/")
    print("   创建应用，获取API Key和Secret Key")

    print("\n2. 配置OAuth2.0:")
    print("   - 应用类型: 选择'服务端应用'")
    print("   - 回调地址: http://localhost:8080 或自定义")
    print("   - 权限: 选择'网盘相关权限'")

    print("\n3. 获取refresh_token流程:")
    print("   a. 构造授权URL:")
    print("      https://openapi.baidu.com/oauth/2.0/authorize")
    print("      ?response_type=code")
    print("      &client_id=YOUR_API_KEY")
    print("      &redirect_uri=YOUR_REDIRECT_URI")
    print("      &scope=basic,netdisk")
    print("      &display=page")

    print("\n   b. 用户授权后获取code")
    print("   c. 使用code换取access_token和refresh_token:")
    print("      POST https://openapi.baidu.com/oauth/2.0/token")
    print("      grant_type=authorization_code")
    print("      &code=授权码")
    print("      &client_id=API_KEY")
    print("      &client_secret=SECRET_KEY")
    print("      &redirect_uri=回调地址")


def method3_browser_developer_tools():
    """方法三：使用浏览器开发者工具"""
    print("\n=== 方法三：浏览器开发者工具 ===")
    print("\n1. 登录百度网盘网页版:")
    print("   访问: https://pan.baidu.com")
    print("   使用百度账号登录")

    print("\n2. 打开开发者工具:")
    print("   - 按F12键")
    print("   - 或右键 -> 检查")

    print("\n3. 查找refresh_token:")
    print("   a. 切换到'Network'(网络)标签")
    print("   b. 刷新页面(F5)")
    print("   c. 在请求列表中查找包含'token'的请求")
    print("   d. 查看请求头或响应体中的refresh_token")

    print("\n4. 常见位置:")
    print("   - Local Storage: pan.baidu.com -> bduss 或 token")
    print("   - Cookie: BDUSS, STOKEN")
    print("   - API响应: /api/ 开头的请求")


def method4_use_existing_tools():
    """方法四：使用现有开源工具"""
    print("\n=== 方法四：使用开源工具 ===")

    print("\n1. Alist相关工具:")
    print("   - alist-org/alist: 包含百度网盘驱动")
    print("   - 使用命令: ./alist admin 可查看现有token")

    print("\n2. 百度网盘助手:")
    print("   - 浏览器扩展: '百度网盘直链下载助手'")
    print("   - 有些扩展会显示refresh_token")

    print("\n3. 命令行工具:")
    print("   - bypy: Python百度网盘客户端")
    print("   - baidupcs-go: Go语言百度网盘客户端")
    print("   这些工具在配置时会引导获取refresh_token")


def save_refresh_token():
    """保存获取到的refresh_token"""
    print("\n=== 保存refresh_token ===")

    refresh_token = input("\n请输入获取到的refresh_token: ").strip()

    if not refresh_token:
        print("refresh_token不能为空")
        return

    # 验证格式
    if not refresh_token.startswith("123."):
        print("⚠ 注意: refresh_token通常以'123.'开头")
        continue_anyway = input("是否继续保存? (y/n): ").strip().lower()
        if continue_anyway != "y":
            return

    if len(refresh_token) < 40 or len(refresh_token) > 100:
        print(f"⚠ 注意: refresh_token长度异常 ({len(refresh_token)}字符)")
        print("正常长度通常在40-60字符之间")

    # 保存到文件
    token_file = "baidu_refresh_token.txt"
    with open(token_file, "w", encoding="utf-8") as f:
        f.write(refresh_token)

    print(f"\n✅ refresh_token已保存到: {token_file}")
    print(f"长度: {len(refresh_token)} 字符")
    print(f"内容: {refresh_token[:30]}...")

    # 更新数据库配置
    update_database = input("\n是否更新数据库中的配置? (y/n): ").strip().lower()
    if update_database == "y":
        update_baidu_config(refresh_token)


def update_baidu_config(refresh_token):
    """更新数据库中的百度网盘配置"""
    import sqlite3
    import json

    db_path = "/Users/primihub/github/OpenList/data/data.db"

    if not os.path.exists(db_path):
        print("数据库不存在，请先启动OpenList服务")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 检查是否有百度网盘配置
        cursor.execute("SELECT id FROM x_storages WHERE driver = 'BaiduNetdisk'")
        baidu_config = cursor.fetchone()

        if baidu_config:
            config_id = baidu_config[0]

            # 获取现有配置
            cursor.execute("SELECT addition FROM x_storages WHERE id = ?", (config_id,))
            old_addition = cursor.fetchone()[0]
            config = json.loads(old_addition)

            # 更新refresh_token
            config["refresh_token"] = refresh_token

            # 更新数据库
            cursor.execute(
                """
                UPDATE x_storages 
                SET addition = ?, remark = ?
                WHERE id = ?
            """,
                (json.dumps(config), "百度网盘真实配置", config_id),
            )

            conn.commit()
            print("✅ 数据库配置已更新")

            # 验证更新
            cursor.execute("SELECT addition FROM x_storages WHERE id = ?", (config_id,))
            new_config = json.loads(cursor.fetchone()[0])
            new_token = new_config.get("refresh_token", "")
            print(f"新的refresh_token长度: {len(new_token)} 字符")

        else:
            print("数据库中没有百度网盘配置，将创建新配置")

            # 创建新配置
            addition = {
                "refresh_token": refresh_token,
                "root_path": "/",
                "order_by": "name",
                "order_direction": "asc",
                "download_api": "official",
                "use_online_api": True,
                "api_url_address": "https://api.oplist.org/baiduyun/renewapi",
                "client_id": "",
                "client_secret": "",
                "custom_crack_ua": "netdisk",
                "upload_thread": "3",
                "upload_timeout": 60,
                "upload_api": "https://d.pcs.baidu.com",
                "use_dynamic_upload_api": True,
                "custom_upload_part_size": 0,
                "low_bandwith_upload_mode": False,
                "only_list_video_file": False,
            }

            cursor.execute(
                """
                INSERT INTO x_storages 
                (mount_path, driver, addition, status, disabled, remark) 
                VALUES (?, ?, ?, 'work', 0, ?)
            """,
                ("/baidu", "BaiduNetdisk", json.dumps(addition), "百度网盘真实配置"),
            )

            conn.commit()
            print("✅ 新的百度网盘配置已创建")

        conn.close()

    except Exception as e:
        print(f"更新数据库失败: {e}")


def test_refresh_token():
    """测试refresh_token有效性"""
    print("\n=== 测试refresh_token ===")

    # 从文件读取或输入
    token_file = "baidu_refresh_token.txt"
    if os.path.exists(token_file):
        with open(token_file, "r", encoding="utf-8") as f:
            refresh_token = f.read().strip()
        print(f"从文件读取refresh_token: {len(refresh_token)} 字符")
    else:
        refresh_token = input("请输入要测试的refresh_token: ").strip()

    if not refresh_token:
        print("refresh_token为空")
        return

    print(f"\nrefresh_token信息:")
    print(f"长度: {len(refresh_token)} 字符")
    print(f"前30字符: {refresh_token[:30]}...")
    print(f"后30字符: ...{refresh_token[-30:]}")

    # 基本格式检查
    if refresh_token.startswith("123."):
        print("✅ 格式正确: 以'123.'开头")
    else:
        print("⚠ 格式异常: 通常应以'123.'开头")

    if 40 <= len(refresh_token) <= 60:
        print("✅ 长度正常")
    else:
        print(f"⚠ 长度异常: {len(refresh_token)}字符 (正常40-60)")

    print("\n注意: 完整测试需要调用百度API")
    print("需要client_id和client_secret才能验证token有效性")


def main():
    print("=== 百度网盘refresh_token获取工具 ===")
    print("\n选择获取方法:")
    print("1. 使用第三方工具（最简单，推荐）")
    print("2. 使用官方API（需要开发者账号）")
    print("3. 使用浏览器开发者工具")
    print("4. 使用开源工具")
    print("5. 保存refresh_token到配置")
    print("6. 测试refresh_token")
    print("7. 查看当前配置")

    try:
        choice = input("\n请选择 (1-7): ").strip()
    except:
        choice = "1"

    if choice == "1":
        method1_third_party_tool()
    elif choice == "2":
        method2_official_api()
    elif choice == "3":
        method3_browser_developer_tools()
    elif choice == "4":
        method4_use_existing_tools()
    elif choice == "5":
        save_refresh_token()
    elif choice == "6":
        test_refresh_token()
    elif choice == "7":
        # 查看当前配置
        import sqlite3

        db_path = "/Users/primihub/github/OpenList/data/data.db"
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, mount_path, driver, remark FROM x_storages WHERE driver = 'BaiduNetdisk'"
            )
            baidu_config = cursor.fetchone()
            conn.close()

            if baidu_config:
                print(f"\n当前百度网盘配置:")
                print(f"ID: {baidu_config[0]}")
                print(f"挂载路径: {baidu_config[1]}")
                print(f"驱动类型: {baidu_config[2]}")
                print(f"备注: {baidu_config[3]}")
            else:
                print("没有百度网盘配置")
        else:
            print("数据库不存在")
    else:
        print("无效选择")


if __name__ == "__main__":
    main()
