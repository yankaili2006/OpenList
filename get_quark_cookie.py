#!/usr/bin/env python3
"""
夸克网盘Cookie获取工具
使用Selenium自动化浏览器获取Cookie
"""

import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_quark_cookie_automated():
    """
    使用Selenium自动获取夸克网盘Cookie
    需要先手动登录一次
    """
    print("=== 夸克网盘Cookie获取工具 ===")
    print("\n注意：此工具需要您手动登录夸克网盘")
    print("工具将打开浏览器，请按提示操作")

    # 检查是否已安装ChromeDriver
    try:
        # 设置Chrome选项
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # 添加用户数据目录，避免每次登录
        user_data_dir = os.path.expanduser("~/.config/chrome_quark")
        options.add_argument(f"user-data-dir={user_data_dir}")

        print("正在启动浏览器...")
        driver = webdriver.Chrome(options=options)

        # 访问夸克网盘
        driver.get("https://pan.quark.cn")

        print("\n请手动完成以下操作：")
        print("1. 如果已登录，直接等待页面加载完成")
        print("2. 如果未登录，请扫码或输入账号密码登录")
        print("3. 登录成功后，页面会显示文件列表")
        print("4. 等待工具自动获取Cookie...")

        # 等待用户登录（最长等待120秒）
        wait = WebDriverWait(driver, 120)
        try:
            # 等待页面加载完成，检查是否有文件列表或登录成功标志
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # 给用户一些时间完成登录
            time.sleep(5)

            # 获取所有Cookie
            cookies = driver.get_cookies()

            # 转换为OpenList需要的格式
            cookie_dict = {}
            cookie_string_parts = []

            for cookie in cookies:
                name = cookie["name"]
                value = cookie["value"]
                cookie_dict[name] = value
                cookie_string_parts.append(f"{name}={value}")

            cookie_string = "; ".join(cookie_string_parts)

            print("\n" + "=" * 50)
            print("成功获取Cookie!")
            print("=" * 50)

            # 显示关键Cookie
            print("\n关键Cookie信息:")
            for key in ["QUTH", "QUTH.sig", "_uc_sso_token"]:
                if key in cookie_dict:
                    print(f"{key}: {cookie_dict[key][:50]}...")
                else:
                    print(f"{key}: 未找到")

            print(f"\n完整Cookie长度: {len(cookie_string)} 字符")

            # 保存到文件
            output_file = "quark_cookie.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "cookie_string": cookie_string,
                        "cookies": cookie_dict,
                        "timestamp": time.time(),
                        "source": "pan.quark.cn",
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )

            print(f"\nCookie已保存到: {output_file}")

            # 也保存为纯文本格式
            txt_file = "quark_cookie.txt"
            with open(txt_file, "w", encoding="utf-8") as f:
                f.write(cookie_string)

            print(f"纯文本格式: {txt_file}")

            print("\n使用说明:")
            print(f"1. 复制以下Cookie字符串:")
            print("-" * 50)
            print(
                cookie_string[:200] + "..."
                if len(cookie_string) > 200
                else cookie_string
            )
            print("-" * 50)
            print(f"\n2. 或使用保存的文件配置OpenList")

            return cookie_string

        except Exception as e:
            print(f"获取Cookie失败: {e}")
            return None

        finally:
            input("\n按回车键关闭浏览器...")
            driver.quit()

    except Exception as e:
        print(f"浏览器启动失败: {e}")
        print("\n请确保已安装:")
        print("1. Google Chrome 浏览器")
        print("2. ChromeDriver (与Chrome版本匹配)")
        print("\n安装ChromeDriver:")
        print("Mac: brew install chromedriver")
        print("Linux: sudo apt-get install chromium-chromedriver")
        print("或从 https://chromedriver.chromium.org/ 下载")
        return None


def get_quark_cookie_manual():
    """
    手动获取Cookie的指导
    """
    print("=== 手动获取夸克网盘Cookie ===")
    print("\n步骤:")
    print("1. 打开Chrome/Firefox浏览器")
    print("2. 访问: https://pan.quark.cn")
    print("3. 登录您的夸克网盘账号")
    print("4. 按F12打开开发者工具")
    print("5. 切换到Network(网络)标签")
    print("6. 刷新页面(F5)")
    print("7. 在请求列表中找到任意请求(如file、folder开头的)")
    print("8. 点击该请求")
    print("9. 在右侧Headers(标头)中找到Cookie字段")
    print("10. 右键复制Cookie值")

    print("\nCookie格式示例:")
    print("QUTH=xxx; QUTH.sig=xxx; _uc_sso_token=xxx; other_cookie=value")

    cookie = input("\n请粘贴您获取的Cookie: ").strip()

    if cookie:
        # 保存Cookie
        with open("quark_cookie_manual.txt", "w", encoding="utf-8") as f:
            f.write(cookie)

        print(f"\nCookie已保存到: quark_cookie_manual.txt")
        print(f"长度: {len(cookie)} 字符")
        return cookie
    else:
        print("Cookie不能为空")
        return None


def main():
    print("选择获取Cookie的方式:")
    print("1. 自动获取 (使用浏览器自动化，需要ChromeDriver)")
    print("2. 手动输入 (您自己从浏览器获取)")
    print("3. 查看帮助文档")

    choice = input("\n请选择 (1/2/3): ").strip()

    if choice == "1":
        get_quark_cookie_automated()
    elif choice == "2":
        get_quark_cookie_manual()
    elif choice == "3":
        print_help()
    else:
        print("无效选择")


def print_help():
    print("\n=== 夸克网盘Cookie获取帮助 ===")
    print("\n为什么需要Cookie?")
    print("OpenList通过Cookie模拟浏览器登录夸克网盘")
    print("Cookie是您的登录凭证，包含身份验证信息")

    print("\nCookie包含哪些信息?")
    print("1. QUTH - 主要认证令牌")
    print("2. QUTH.sig - 签名验证")
    print("3. _uc_sso_token - 单点登录令牌")
    print("4. 其他会话信息")

    print("\nCookie有效期:")
    print("通常为几天到几周，过期后需要重新获取")

    print("\n安全提示:")
    print("1. Cookie包含账号访问权限，请妥善保管")
    print("2. 不要分享给他人")
    print("3. 定期更新Cookie")

    print("\n常见问题:")
    print("Q: Cookie无效怎么办?")
    print("A: 重新登录夸克网盘获取新的Cookie")

    print("\nQ: 如何检查Cookie是否有效?")
    print("A: 使用以下命令测试:")
    print(
        "   curl -H 'Cookie: YOUR_COOKIE' https://drive.quark.cn/1/clouddrive/file/sort"
    )

    print("\nQ: Cookie过期了怎么办?")
    print("A: 重新运行此工具获取新的Cookie")


if __name__ == "__main__":
    main()
