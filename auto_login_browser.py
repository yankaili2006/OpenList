#!/usr/bin/env python3
"""
浏览器自动化登录获取云盘token
使用Selenium模拟浏览器登录
"""

import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class CloudAutoLogin:
    def __init__(self):
        self.driver = None
        self.config_file = "auto_login_config.json"
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置失败: {e}")
        return {
            "baidu": {"username": "", "password": ""},
            "aliyun": {"username": "", "password": ""},
            "quark": {"username": "", "password": ""}
        }
    
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            print(f"配置已保存到 {self.config_file}")
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def init_driver(self):
        """初始化浏览器驱动"""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 设置用户数据目录，避免重复登录
        user_data_dir = os.path.join(os.path.expanduser('~'), '.cloud_auto_login')
        chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return True
        except Exception as e:
            print(f"初始化浏览器失败: {e}")
            print("请确保已安装Chrome浏览器和ChromeDriver")
            return False
    
    def close_driver(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
    
    def wait_for_element(self, by, value, timeout=10):
        """等待元素出现"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    
    def auto_login_baidu(self):
        """自动登录百度网盘并获取token"""
        print("\n=== 百度网盘自动登录 ===")
        
        # 访问百度网盘开放平台授权页面
        self.driver.get("https://openapi.baidu.com/oauth/2.0/authorize?response_type=code&client_id=iYCeC9g08h5vuP9UqvPHKKSVrKFXGa1v&redirect_uri=oob&scope=basic,netdisk")
        
        try:
            # 等待页面加载
            time.sleep(3)
            
            # 检查是否需要登录
            if "登录" in self.driver.title or "login" in self.driver.page_source.lower():
                print("需要登录百度账号...")
                
                # 输入用户名
                username_input = self.wait_for_element(By.ID, "TANGRAM__PSP_4__userName")
                username_input.clear()
                username_input.send_keys(self.config["baidu"]["username"])
                
                # 输入密码
                password_input = self.wait_for_element(By.ID, "TANGRAM__PSP_4__password")
                password_input.clear()
                password_input.send_keys(self.config["baidu"]["password"])
                
                # 点击登录
                login_btn = self.wait_for_element(By.ID, "TANGRAM__PSP_4__submit")
                login_btn.click()
                
                time.sleep(5)
            
            # 授权页面
            if "授权" in self.driver.title or "authorize" in self.driver.page_source.lower():
                print("正在授权...")
                
                # 点击授权按钮
                try:
                    auth_btn = self.wait_for_element(By.ID, "TANGRAM__PSP_4__confirm")
                    auth_btn.click()
                    time.sleep(3)
                except:
                    # 尝试其他选择器
                    auth_btn = self.driver.find_element(By.XPATH, "//button[contains(text(),'授权')]")
                    auth_btn.click()
                    time.sleep(3)
            
            # 获取授权码
            if "授权成功" in self.driver.page_source or "authorization code" in self.driver.page_source:
                # 这里需要手动复制授权码，因为百度会显示在页面上
                print("请手动复制页面上的授权码，然后按回车继续...")
                input()
                
                auth_code = input("请输入授权码: ").strip()
                
                if auth_code:
                    # 使用授权码获取refresh_token（这里需要调用API）
                    print(f"获取到授权码: {auth_code}")
                    print("请使用此授权码通过API获取refresh_token")
                    return {"auth_code": auth_code}
            
        except Exception as e:
            print(f"百度网盘登录失败: {e}")
            print("当前页面URL:", self.driver.current_url)
            print("当前页面标题:", self.driver.title)
        
        return None
    
    def auto_login_aliyun(self):
        """自动登录阿里云盘并获取token"""
        print("\n=== 阿里云盘自动登录 ===")
        
        # 访问阿里云盘授权页面
        self.driver.get("https://auth.aliyundrive.com/v2/oauth/authorize?client_id=4d7bcac4e5b14c68a4a1c7b8f82f6b1f&redirect_uri=https://www.aliyundrive.com/sign/callback&response_type=code&scope=user:base,file:all:read,file:all:write")
        
        try:
            # 等待页面加载
            time.sleep(5)
            
            print("阿里云盘需要扫码登录，请在浏览器中完成扫码...")
            print("扫码完成后，页面会跳转，请等待...")
            
            # 等待用户扫码
            input("扫码完成后按回车继续...")
            
            # 检查是否跳转到回调页面
            if "callback" in self.driver.current_url:
                # 从URL中提取code
                current_url = self.driver.current_url
                if "code=" in current_url:
                    code = current_url.split("code=")[1].split("&")[0]
                    print(f"获取到授权码: {code}")
                    
                    # 这里可以自动调用API获取refresh_token
                    print("正在通过API获取refresh_token...")
                    
                    import requests
                    token_url = "https://auth.aliyundrive.com/v2/oauth/token"
                    data = {
                        "client_id": "4d7bcac4e5b14c68a4a1c7b8f82f6b1f",
                        "code": code,
                        "grant_type": "authorization_code"
                    }
                    
                    response = requests.post(token_url, json=data)
                    if response.status_code == 200:
                        token_data = response.json()
                        refresh_token = token_data.get("refresh_token")
                        print(f"成功获取refresh_token: {refresh_token}")
                        return {"refresh_token": refresh_token}
                    else:
                        print(f"获取token失败: {response.text}")
            
        except Exception as e:
            print(f"阿里云盘登录失败: {e}")
        
        return None
    
    def auto_login_quark(self):
        """自动登录夸克网盘并获取cookie"""
        print("\n=== 夸克网盘自动登录 ===")
        
        # 访问夸克网盘登录页面
        self.driver.get("https://pan.quark.cn")
        
        try:
            # 等待页面加载
            time.sleep(5)
            
            # 检查是否需要登录
            if "登录" in self.driver.page_source or "login" in self.driver.page_source.lower():
                print("需要登录夸克账号...")
                
                # 点击登录按钮
                try:
                    login_btn = self.wait_for_element(By.XPATH, "//button[contains(text(),'登录')]")
                    login_btn.click()
                    time.sleep(3)
                except:
                    # 尝试其他选择器
                    login_btn = self.driver.find_element(By.CLASS_NAME, "login-btn")
                    login_btn.click()
                    time.sleep(3)
                
                # 输入用户名
                username_input = self.wait_for_element(By.NAME, "username")
                username_input.clear()
                username_input.send_keys(self.config["quark"]["username"])
                
                # 输入密码
                password_input = self.wait_for_element(By.NAME, "password")
                password_input.clear()
                password_input.send_keys(self.config["quark"]["password"])
                
                # 点击登录
                submit_btn = self.wait_for_element(By.XPATH, "//button[@type='submit']")
                submit_btn.click()
                
                # 等待登录完成
                time.sleep(10)
            
            # 登录成功后获取cookie
            if "我的文件" in self.driver.page_source or "网盘" in self.driver.title:
                print("登录成功，获取cookie中...")
                
                # 获取所有cookies
                cookies = self.driver.get_cookies()
                
                # 提取关键cookie
                important_cookies = {}
                for cookie in cookies:
                    if any(key in cookie['name'].upper() for key in ['QUTHK', 'QUTOKEN']):
                        important_cookies[cookie['name']] = cookie['value']
                
                if important_cookies:
                    print("获取到关键cookie:")
                    for name, value in important_cookies.items():
                        print(f"  {name}: {value[:20]}...")
                    
                    # 构建cookie字符串
                    cookie_str = "; ".join([f"{name}={value}" for name, value in important_cookies.items()])
                    return {"cookie": cookie_str}
                else:
                    print("未找到关键cookie，尝试获取全部cookie")
                    all_cookies = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
                    return {"cookie": all_cookies}
            
        except Exception as e:
            print(f"夸克网盘登录失败: {e}")
            print("当前页面URL:", self.driver.current_url)
        
        return None
    
    def setup_credentials(self):
        """设置登录凭证"""
        print("\n=== 设置登录凭证 ===")
        
        for platform in ["baidu", "aliyun", "quark"]:
            print(f"\n{platform.upper()}:")
            username = input(f"  用户名/手机号 (留空跳过): ").strip()
            if username:
                self.config[platform]["username"] = username
                password = input(f"  密码: ").strip()
                self.config[platform]["password"] = password
        
        self.save_config()
    
    def run_auto_login(self):
        """运行自动登录"""
        print("云盘平台自动登录工具")
        print("=" * 50)
        
        # 检查配置
        if not any(self.config[platform]["username"] for platform in ["baidu", "aliyun", "quark"]):
            print("检测到未设置登录凭证，请先设置")
            self.setup_credentials()
        
        # 初始化浏览器
        if not self.init_driver():
            return
        
        try:
            results = {}
            
            # 选择要登录的平台
            print("\n选择要自动登录的平台:")
            print("1. 百度网盘")
            print("2. 阿里云盘") 
            print("3. 夸克网盘")
            print("4. 全部平台")
            
            choice = input("请选择 (1-4): ").strip()
            
            platforms_to_login = []
            if choice == '1':
                platforms_to_login = ['baidu']
            elif choice == '2':
                platforms_to_login = ['aliyun']
            elif choice == '3':
                platforms_to_login = ['quark']
            elif choice == '4':
                platforms_to_login = ['baidu', 'aliyun', 'quark']
            else:
                print("无效选择")
                return
            
            for platform in platforms_to_login:
                if platform == 'baidu':
                    result = self.auto_login_baidu()
                elif platform == 'aliyun':
                    result = self.auto_login_aliyun()
                elif platform == 'quark':
                    result = self.auto_login_quark()
                
                if result:
                    results[platform] = result
                    print(f"✓ {platform} 登录成功")
                else:
                    print(f"✗ {platform} 登录失败")
            
            # 保存结果
            if results:
                output_file = "auto_login_results.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                print(f"\n✓ 登录结果已保存到 {output_file}")
                print("您可以将这些token用于云盘配置脚本")
        
        finally:
            self.close_driver()

def main():
    auto_login = CloudAutoLogin()
    auto_login.run_auto_login()

if __name__ == "__main__":
    main()