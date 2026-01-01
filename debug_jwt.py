#!/usr/bin/env python3
"""
JWT调试工具 - 分析OpenList的JWT token问题
"""

import requests
import json
import base64
from datetime import datetime

BASE_URL = "http://localhost:5244"

def decode_jwt_without_verification(token):
    """不解密验证，直接解码JWT token内容"""
    try:
        # JWT token格式: header.payload.signature
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        # 解码header和payload
        header = json.loads(base64.urlsafe_b64decode(parts[0] + '=='))
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + '=='))
        
        return {
            'header': header,
            'payload': payload,
            'signature': parts[2][:20] + '...'  # 只显示签名前20个字符
        }
    except Exception as e:
        return {'error': str(e)}

def test_jwt_flow():
    """测试完整的JWT流程"""
    print("=== JWT Token调试分析 ===\n")
    
    # 1. 获取token
    print("1. 获取管理员token...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "admin", "password": "admin"}
    )
    
    if login_response.status_code != 200:
        print(f"登录失败: {login_response.text}")
        return
    
    token_data = login_response.json()
    token = token_data.get("data", {}).get("token") if isinstance(token_data, dict) else None
    
    if not token:
        print("未获取到token")
        return
    
    print(f"✅ 获取到token: {token[:50]}...")
    
    # 2. 解码token
    print("\n2. 解码JWT token...")
    decoded = decode_jwt_without_verification(token)
    if decoded:
        print("Header:", json.dumps(decoded['header'], indent=2))
        print("Payload:", json.dumps(decoded['payload'], indent=2))
        print("Signature:", decoded['signature'])
        
        # 检查过期时间
        exp_timestamp = decoded['payload'].get('exp')
        if exp_timestamp:
            exp_time = datetime.fromtimestamp(exp_timestamp)
            now = datetime.now()
            print(f"Token过期时间: {exp_time} ({exp_timestamp})")
            print(f"当前时间: {now}")
            print(f"是否已过期: {exp_time < now}")
    
    # 3. 测试token验证
    print("\n3. 测试token验证...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试多个API端点
    endpoints = [
        "/api/admin/storage/list",
        "/api/admin/driver/list", 
        "/api/fs/list",
        "/api/me"
    ]
    
    for endpoint in endpoints:
        print(f"\n测试 {endpoint}:")
        try:
            if endpoint == "/api/fs/list":
                # POST请求
                response = requests.post(
                    f"{BASE_URL}{endpoint}",
                    headers=headers,
                    json={"path": "/", "page": 1, "per_page": 10}
                )
            else:
                # GET请求
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            
            print(f"  状态码: {response.status_code}")
            print(f"  响应: {response.text[:200]}...")
            
        except Exception as e:
            print(f"  请求失败: {e}")
    
    # 4. 测试公共端点（应该不需要认证）
    print("\n4. 测试公共端点...")
    public_endpoints = [
        "/ping",
        "/api/public/settings",
        "/api/public/offline_download_tools"
    ]
    
    for endpoint in public_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"  {endpoint}: 状态码 {response.status_code}")
        except Exception as e:
            print(f"  {endpoint}: 失败 - {e}")

def analyze_problem():
    """分析问题原因"""
    print("\n=== 问题分析 ===")
    print("""
可能的问题原因:
1. JWT密钥不匹配 - 容器重启后密钥变化
2. Token缓存机制 - 内存缓存失效导致所有token无效
3. 时间同步问题 - 服务器时间不正确
4. 二进制文件内部bug - 认证逻辑有缺陷

基于测试结果，最可能的原因是:
- Token缓存机制: 生成的token被添加到内存缓存，但重启后缓存丢失
- 这导致所有"有效"的JWT token都被标记为"invalidated"
""")

if __name__ == "__main__":
    test_jwt_flow()
    analyze_problem()