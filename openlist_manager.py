#!/usr/bin/env python3
"""
OpenList存储管理器
绕过JWT认证问题，直接通过数据库管理存储配置
"""

import sqlite3
import json
import os
from typing import Dict, List, Any

class OpenListStorageManager:
    def __init__(self, data_dir: str = "/Users/primihub/github/OpenList/data"):
        self.data_dir = data_dir
        self.db_path = os.path.join(data_dir, "data.db")
    
    def get_storages(self) -> List[Dict[str, Any]]:
        """获取所有存储配置"""
        if not os.path.exists(self.db_path):
            return []
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, mount_path, driver, addition, status, disabled, remark 
                FROM x_storages 
                ORDER BY "order"
            """)
            
            storages = []
            for row in cursor.fetchall():
                storage = dict(row)
                # 解析addition字段
                if storage['addition']:
                    try:
                        storage['addition'] = json.loads(storage['addition'])
                    except:
                        storage['addition'] = {}
                storages.append(storage)
            
            return storages
        except Exception as e:
            print(f"获取存储列表失败: {e}")
            return []
        finally:
            conn.close()
    
    def add_storage(self, mount_path: str, driver: str, addition: Dict, remark: str = "") -> bool:
        """添加存储配置"""
        if not os.path.exists(self.db_path):
            print("数据库文件不存在")
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 获取当前最大order值
            cursor.execute("SELECT MAX(\"order\") FROM x_storages")
            max_order = cursor.fetchone()[0] or 0
            
            cursor.execute("""
                INSERT INTO x_storages 
                (mount_path, driver, addition, status, disabled, remark, "order") 
                VALUES (?, ?, ?, 'work', 0, ?, ?)
            """, (mount_path, driver, json.dumps(addition), remark, max_order + 1))
            
            conn.commit()
            print(f"✅ 存储添加成功: {mount_path} ({driver})")
            return True
        except Exception as e:
            print(f"❌ 添加存储失败: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def delete_storage(self, storage_id: int) -> bool:
        """删除存储配置"""
        if not os.path.exists(self.db_path):
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM x_storages WHERE id = ?", (storage_id,))
            conn.commit()
            print(f"✅ 存储删除成功: ID {storage_id}")
            return True
        except Exception as e:
            print(f"❌ 删除存储失败: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_supported_drivers(self) -> List[str]:
        """获取支持的驱动列表"""
        drivers = [
            # 本地和网络存储
            "Local", "Ftp", "Sftp", "Webdav", "S3",
            # 国内云盘
            "BaiduNetdisk", "Aliyundrive", "AliyundriveOpen", "AliyundriveShare",
            "115", "115Open", "115Share", "Weiyun", "189", "189TV", "189PC",
            "QuarkOpen", "QuarkUC", "QuarkUCTV", "PikPak", "PikPakShare",
            "Terabox", "Mopan", "Wopan",
            # 国际云盘
            "Onedrive", "OnedriveApp", "OnedriveSharelink", "GoogleDrive",
            "Dropbox", "Mega", "YandexDisk", "Mediafire", "ProtonDrive",
            # 开发者和特殊
            "Github", "GithubReleases", "Teambition", "Teldrive",
            "Lanzou", "Ilanzou", "Chaoxing", "NeteaseMusic",
            "Cloudreve", "CloudreveV4", "Kodbox", "Smb",
            # 虚拟和工具
            "Alias", "Virtual", "Crypt", "Chunk", "Strm", "UrlTree"
        ]
        return sorted(drivers)

def main():
    manager = OpenListStorageManager()
    
    print("=== OpenList 存储管理器 ===")
    print("直接通过数据库管理存储配置，绕过JWT认证问题\n")
    
    if not os.path.exists(manager.db_path):
        print("❌ 数据库文件不存在")
        print("请确保OpenList服务正在运行")
        return
    
    while True:
        print("\n" + "="*50)
        print("1. 查看存储列表")
        print("2. 添加存储")
        print("3. 删除存储")
        print("4. 查看支持的驱动")
        print("5. 重启服务（使配置生效）")
        print("6. 退出")
        
        choice = input("\n请选择操作 (1-6): ").strip()
        
        if choice == "1":
            print("\n=== 存储列表 ===")
            storages = manager.get_storages()
            if not storages:
                print("暂无存储配置")
            for storage in storages:
                print(f"ID: {storage['id']}")
                print(f"  挂载路径: {storage['mount_path']}")
                print(f"  驱动类型: {storage['driver']}")
                print(f"  状态: {storage['status']}")
                print(f"  备注: {storage['remark']}")
                if storage['addition']:
                    # 隐藏敏感信息
                    addition = storage['addition'].copy()
                    for key in ['refresh_token', 'password', 'access_token', 'cookie', 'secret_access_key']:
                        if key in addition:
                            addition[key] = '***隐藏***'
                    print(f"  配置: {json.dumps(addition, ensure_ascii=False)}")
                print("-" * 40)
        
        elif choice == "2":
            print("\n=== 添加存储 ===")
            mount_path = input("挂载路径 (例如: /baidu): ").strip()
            if not mount_path.startswith('/'):
                mount_path = '/' + mount_path
            
            print("\n支持的驱动类型:")
            drivers = manager.get_supported_drivers()
            for i, driver in enumerate(drivers[:25]):  # 显示前25个
                print(f"  {driver}")
            if len(drivers) > 25:
                print(f"  ... 还有 {len(drivers)-25} 个驱动")
            
            driver = input("\n驱动类型: ").strip()
            remark = input("备注: ").strip()
            
            # 根据驱动类型收集配置
            addition = {}
            if driver == "BaiduNetdisk":
                addition["refresh_token"] = input("百度网盘refresh_token: ").strip()
                addition["root_path"] = "/"
            elif driver == "Aliyundrive":
                addition["refresh_token"] = input("阿里云盘refresh_token: ").strip()
                addition["root_id"] = "root"
            elif driver == "Local":
                addition["root_folder_path"] = input("本地路径: ").strip() or "/"
            elif driver == "Webdav":
                addition["url"] = input("WebDAV地址: ").strip()
                addition["username"] = input("用户名: ").strip()
                addition["password"] = input("密码: ").strip()
            elif driver == "S3":
                addition["access_key_id"] = input("Access Key ID: ").strip()
                addition["secret_access_key"] = input("Secret Access Key: ").strip()
                addition["endpoint"] = input("Endpoint: ").strip()
                addition["bucket"] = input("Bucket名称: ").strip()
            else:
                print(f"驱动 {driver} 需要特定配置")
                config_json = input("配置JSON (或留空使用默认配置): ").strip()
                if config_json:
                    try:
                        addition = json.loads(config_json)
                    except:
                        print("❌ JSON格式错误，使用空配置")
            
            if manager.add_storage(mount_path, driver, addition, remark):
                print("\n💡 存储添加成功！请重启OpenList容器使配置生效:")
                print("   docker restart openlist")
            else:
                print("❌ 存储添加失败")
        
        elif choice == "3":
            print("\n=== 删除存储 ===")
            storage_id = input("要删除的存储ID: ").strip()
            
            if storage_id.isdigit():
                if manager.delete_storage(int(storage_id)):
                    print("\n💡 存储删除成功！请重启OpenList容器:")
                    print("   docker restart openlist")
                else:
                    print("❌ 存储删除失败")
            else:
                print("❌ 请输入有效的存储ID")
        
        elif choice == "4":
            print("\n=== 支持的驱动 ===")
            drivers = manager.get_supported_drivers()
            for driver in drivers:
                print(f"  {driver}")
            print(f"\n总共支持 {len(drivers)} 种存储驱动")
        
        elif choice == "5":
            print("\n重启OpenList容器...")
            os.system("docker restart openlist")
            print("✅ 容器已重启")
            print("等待服务恢复...")
            import time
            time.sleep(5)
        
        elif choice == "6":
            print("退出")
            break
        
        else:
            print("❌ 无效选择")

if __name__ == "__main__":
    main()