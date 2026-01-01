#!/usr/bin/env python3
"""
添加示例存储配置到OpenList
"""

import sqlite3
import json
import os

def add_sample_storages():
    db_path = '/Users/primihub/github/OpenList/data/data.db'
    
    if not os.path.exists(db_path):
        print("数据库文件不存在")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 示例存储配置
    sample_storages = [
        {
            "mount_path": "/local",
            "driver": "Local", 
            "addition": {"root_folder_path": "/"},
            "remark": "本地存储示例"
        },
        {
            "mount_path": "/demo",
            "driver": "Webdav",
            "addition": {
                "url": "https://demo.com/dav",
                "username": "demo",
                "password": "demo123"
            },
            "remark": "WebDAV示例"
        }
    ]
    
    try:
        # 获取当前最大order值
        cursor.execute("SELECT MAX(\"order\") FROM x_storages")
        max_order = cursor.fetchone()[0] or 0
        
        for i, storage in enumerate(sample_storages):
            cursor.execute("""
                INSERT INTO x_storages 
                (mount_path, driver, addition, status, disabled, remark, "order") 
                VALUES (?, ?, ?, 'work', 0, ?, ?)
            """, (
                storage["mount_path"],
                storage["driver"],
                json.dumps(storage["addition"]),
                storage["remark"],
                max_order + i + 1
            ))
        
        conn.commit()
        print("✅ 示例存储配置添加成功！")
        print("💡 请重启OpenList容器使配置生效:")
        print("   docker restart openlist")
        
    except Exception as e:
        print(f"❌ 添加存储失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_sample_storages()