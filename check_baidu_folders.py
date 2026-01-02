#!/usr/bin/env python3
"""
检查百度网盘文件夹
"""


def show_baidu_info():
    print("=== 百度网盘状态检查 ===")

    # 检查配置
    import os
    import json

    db_path = "/Users/primihub/github/OpenList/data/data.db"
    if os.path.exists(db_path):
        try:
            import sqlite3

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT addition FROM x_storages WHERE driver = 'BaiduNetdisk'"
            )
            result = cursor.fetchone()
            conn.close()

            if result:
                config = json.loads(result[0])
                print("\n✅ 百度网盘配置存在")
                print(
                    f"refresh_token: 已配置 ({len(config.get('refresh_token', ''))}字符)"
                )
                print(f"client_id: {config.get('client_id', '未设置')}")
                print(
                    f"client_secret: {'已设置' if config.get('client_secret') else '未设置'}"
                )

                if not config.get("client_id") or not config.get("client_secret"):
                    print("\n⚠ 缺少完整的OAuth2.0配置")
                    print("需要client_id和client_secret才能访问真实文件")
                else:
                    print("\n✅ 配置完整，可以访问真实文件")
            else:
                print("\n❌ 没有百度网盘配置")
        except Exception as e:
            print(f"\n❌ 读取配置失败: {e}")
    else:
        print("\n❌ 数据库不存在")

    # 显示模拟文件夹结构
    print("\n📁 百度网盘典型文件夹结构（模拟）:")
    print("""
根目录/
├── 我的文档/
│   ├── 工作报告.pdf
│   ├── 学习资料.zip
│   └── 个人简历.docx
├── 图片/
│   ├── 旅行照片/
│   ├── 家庭相册/
│   └── 工作截图.png
├── 视频/
│   ├── 电影/
│   ├── 电视剧/
│   └── 自制视频.mp4
├── 音乐/
│   ├── 流行歌曲.mp3
│   ├── 古典音乐.flac
│   └── 播客.m4a
├── 工作资料/
│   ├── 项目文档/
│   ├── 会议记录/
│   └── 客户资料.xlsx
├── 下载/
│   ├── 软件安装包.exe
│   ├── 文档模板.zip
│   └── 临时文件.tmp
└── 备份/
    ├── 系统备份/
    ├── 数据备份/
    └── 照片备份/
""")

    print("\n📊 统计信息:")
    print("- 总文件夹数: 8个")
    print("- 总文件数: ~25个")
    print("- 估计占用空间: ~10GB")

    # 获取完整配置的指南
    print("\n🔧 获取完整配置:")
    print("1. 访问: https://developer.baidu.com/")
    print("2. 注册百度开发者账号")
    print("3. 创建应用获取client_id和client_secret")
    print("4. 将凭证添加到OpenList配置中")


def main():
    show_baidu_info()


if __name__ == "__main__":
    main()
