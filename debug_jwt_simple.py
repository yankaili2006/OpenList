#!/usr/bin/env python3
"""
简单的JWT调试工具
"""

import requests
import json
import base64
from datetime import datetime

BASE_URL = "http://localhost:5244"

def decode_jwt(token):
    """解码JWT token"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        # 解码payload
        payload_encoded = parts[1]
        # 添加padding
        padding = 4 - len(payload_encoded) % 4
        if padding != 4:
            payload_encoded += '=' * padding
        
        payload_bytes = base64.urlsafe_b64decode(payload_encoded)
        payload = json.loads(payload_bytes)
        
        return payload
    except Exception as e:
        print(f"解码失败: {e}")
        return None

def main():
    print("=== JWT调试工具 ===\n")
    
    # 获取token
    print("1. 获取管理员token...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "admin", "password": "admin"}
    )
    
    if response.status_code != 200:
        print(f"登录失败: {response.text}")
        return
    
    data = response.json()
    token = data.get("data", {}).get("token")
    
    if not token:
        print("未获取到token")
        return
    
    print(f"✅ 获取到token: {token[:50]}...\n")
    
    # 解码token
    print("2. 解码token内容...")
    payload = decode_jwt(token)
    if payload:
        print("Payload内容:")
        for key, value in payload.items():
            if key == 'exp':
                exp_time = datetime.fromtimestamp(value)
                now = datetime.now()
                status = "已过期" if exp_time < now else "有效"
                print(f"  {key}: {value} ({exp_time}) - {status}")
            else:
                print(f"  {key}: {value}")
    
    # 测试token
    print("\n3. 测试token验证...")
    headers = {"Authorization": f"Bearer {token}"}
    
    test_endpoints = [
        ("/api/admin/storage/list", "GET"),
        ("/api/admin/driver/list", "GET"),
        ("/api/fs/list", "POST")
    ]
    
    for endpoint, method in test_endpoints:
        print(f"\n测试 {method} {endpoint}:")
        try:
            if method == "POST":
                resp = requests.post(
                    f"{BASE_URL}{endpoint}",
                    headers=headers,
                    json={"path": "/", "page": 1, "per_page": 10}
                )
            else:
                resp = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            
            print(f"  状态码: {resp.status_code}")
            result = resp.json()
            if "code" in result:
                print(f"  错误: {result.get('message')}")
            else:
                print(f"  成功: 获取到数据")
                
        except Exception as e:
            print(f"  请求异常: {e}")

if __name__ == "__main__":
    main()