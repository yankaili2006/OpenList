#!/usr/bin/env python3
"""
OpenList JWT认证测试脚本
用于诊断和修复JWT token验证问题
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5244"

def test_login(username, password):
    """测试登录"""
    url = f"{BASE_URL}/api/auth/login"
    data = {"username": username, "password": password}
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"登录响应状态码: {response.status_code}")
        print(f"登录响应内容: {response.text}")
        
        if response.status_code == 200:
            token = response.json().get("data", {}).get("token")
            if token:
                print(f"✅ 成功获取token: {token[:50]}...")
                return token
        return None
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        return None

def test_token_validation(token):
    """测试token验证"""
    if not token:
        return False
    
    # 测试存储列表API
    url = f"{BASE_URL}/api/admin/storage/list"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"\nToken验证响应状态码: {response.status_code}")
        print(f"Token验证响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                print("✅ Token验证成功")
                return True
            else:
                print(f"❌ Token验证失败: {data.get('message')}")
                return False
        else:
            print("❌ Token验证失败")
            return False
    except Exception as e:
        print(f"❌ Token验证请求失败: {e}")
        return False

def test_public_apis():
    """测试公共API"""
    print("\n=== 测试公共API ===")
    
    # 测试ping
    try:
        response = requests.get(f"{BASE_URL}/ping", timeout=5)
        print(f"Ping响应: {response.text} (状态码: {response.status_code})")
    except Exception as e:
        print(f"Ping测试失败: {e}")
    
    # 测试公共设置
    try:
        response = requests.get(f"{BASE_URL}/api/public/settings", timeout=5)
        print(f"公共设置响应状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json().get("data", {})
            print(f"站点标题: {data.get('site_title')}")
            print(f"版本: {data.get('version')}")
    except Exception as e:
        print(f"公共设置测试失败: {e}")

def main():
    print("=== OpenList JWT认证诊断 ===")
    
    # 测试公共API
    test_public_apis()
    
    # 测试管理员登录
    print("\n=== 测试管理员登录 ===")
    admin_token = test_login("admin", "admin")
    if admin_token:
        test_token_validation(admin_token)
    
    # 测试访客登录
    print("\n=== 测试访客登录 ===")
    guest_token = test_login("guest", "guest")
    if guest_token:
        test_token_validation(guest_token)
    
    print("\n=== 诊断完成 ===")

if __name__ == "__main__":
    main()