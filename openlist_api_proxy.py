#!/usr/bin/env python3
"""
OpenList API代理
绕过JWT认证问题，直接操作数据库
"""

import sqlite3
import json
import os
from typing import Dict, List, Any

class OpenListAPIProxy:
    def __init__(self, data_dir: str = "/Users/primihub/github/OpenList/data"):
        self.data_dir = data_dir
        self.db_path = os.path.join(data_dir, "data.db")
        
    def get_storages(self) -> List[Dict[str, Any]]:
        """获取存储列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, mount_path, driver, addition, status, disabled, remark 
            FROM x_storages
            ORDER BY "order"
        """)
        
        storages = []
        for row in cursor.fetchall():
            storage = {
                "id": row[0],
                "mount_path": row[1],
                "driver": row[2],
                "addition": json.loads(row[3]) if row[3] else {},
                "status": row[4],
                "disabled": bool(row[5]),
                "remark": row[6]
            }
            storages.append(storage)
        
        conn.close()
        return storages
    
    def add_storage(self, mount_path: str, driver: str, addition: Dict, remark: str = "") -> bool:
        """添加存储"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO x_storages 
                (mount_path, driver, addition, status, disabled, remark) 
                VALUES (?, ?, ?, 'work', 0, ?)
            """, (mount_path, driver, json.dumps(addition), remark))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"添加存储失败: {e}")
            conn.rollback()
            conn.close()
            return False
    
    def delete_storage(self, storage_id: int) -> bool:
        """删除存储"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM x_storages WHERE id = ?", (storage_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"删除存储失败: {e}")
            conn.rollback()
            conn.close()
            return False
    
    def update_storage(self, storage_id: int, **kwargs) -> bool:
        """更新存储"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            update_fields = []
            update_values = []
            
            for key, value in kwargs.items():
                if key == "addition" and isinstance(value, dict):
                    update_fields.append(f"{key} = ?")
                    update_values.append(json.dumps(value))
                else:
                    update_fields.append(f"{key} = ?")
                    update_values.append(value)
            
            if update_fields:
                update_values.append(storage_id)
                cursor.execute(f"""
                    UPDATE x_storages 
                    SET {', '.join(update_fields)}
                    WHERE id = ?
                """, update_values)
                
                conn.commit()
            
            conn.close()
            return True
        except Exception as e:
            print(f"更新存储失败: {e}")
            conn.rollback()
            conn.close()
            return False

def main():
    proxy = OpenListAPIProxy()
    
    print("=== OpenList API代理 ===")
    print("1. 查看存储列表")
    print("2. 添加存储")
    print("3. 删除存储")
    print("4. 退出")
    
    while True:
        choice = input("\n请选择操作 (1-4): ").strip()
        
        if choice == "1":
            storages = proxy.get_storages()
            print("\n=== 存储列表 ===")
            for storage in storages:
                print(f"ID: {storage['id']}")
                print(f"挂载路径: {storage['mount_path']}")
                print(f"驱动: {storage['driver']}")
                print(f"状态: {storage['status']}")
                print(f"备注: {storage['remark']}")
                print("-" * 40)
        
        elif choice == "2":
            print("\n=== 添加存储 ===")
            mount_path = input("挂载路径 (例如: /baidu): ").strip()
            driver = input("驱动类型 (例如: BaiduNetdisk): ").strip()
            remark = input("备注: ").strip()
            
            # 根据驱动类型请求不同的配置
            addition = {}
            if driver == "BaiduNetdisk":
                addition["refresh_token"] = input("百度网盘refresh_token: ").strip()
            elif driver == "Aliyundrive":
                addition["refresh_token"] = input("阿里云盘refresh_token: ").strip()
            elif driver == "Local":
                addition["root_folder_path"] = input("本地路径: ").strip()
            # 可以添加更多驱动的配置
            
            if proxy.add_storage(mount_path, driver, addition, remark):
                print("✅ 存储添加成功，请重启OpenList容器")
            else:
                print("❌ 存储添加失败")
        
        elif choice == "3":
            print("\n=== 删除存储 ===")
            storage_id = input("要删除的存储ID: ").strip()
            
            if storage_id.isdigit():
                if proxy.delete_storage(int(storage_id)):
                    print("✅ 存储删除成功，请重启OpenList容器")
                else:
                    print("❌ 存储删除失败")
            else:
                print("❌ 请输入有效的存储ID")
        
        elif choice == "4":
            print("退出")
            break
        
        else:
            print("❌ 无效选择")

if __name__ == "__main__":
    main()