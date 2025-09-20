#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
一键推送到GitHub并触发自动构建的简单脚本
"""
import os
import subprocess
import sys
from datetime import datetime

def simple_push():
    """简单的推送流程"""
    print("=== 一键推送到GitHub ===")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查git
    try:
        subprocess.run(['git', '--version'], check=True, capture_output=True)
        print("✅ Git已安装")
    except:
        print("❌ 请先安装Git")
        return False
    
    # 初始化git仓库（如果不存在）
    if not os.path.exists('.git'):
        print("初始化Git仓库...")
        subprocess.run(['git', 'init'], check=True)
        subprocess.run(['git', 'config', 'user.name', 'Your Name'], check=True)
        subprocess.run(['git', 'config', 'user.email', 'your.email@example.com'], check=True)
    
    # 添加所有文件
    print("添加文件到Git...")
    subprocess.run(['git', 'add', '.'], check=True)
    
    # 检查是否有更改
    result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    if not result.stdout.strip():
        print("没有需要提交的更改")
        return True
    
    # 提交更改
    commit_msg = f"更新通讯录获取器 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    print(f"提交更改: {commit_msg}")
    subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
    
    # 获取远程仓库URL
    print("\n请按以下步骤操作:")
    print("1. 打开浏览器访问: https://github.com/new")
    print("2. 创建新仓库 (例如: ContactFetcher)")
    print("3. 不要添加README文件")
    print("4. 创建完成后复制仓库URL")
    
    repo_url = input("\n请输入GitHub仓库URL: ").strip()
    if not repo_url:
        print("未提供仓库URL，操作取消")
        return False
    
    # 添加远程仓库
    try:
        subprocess.run(['git', 'remote', 'add', 'origin', repo_url], check=True)
    except:
        # 如果已存在，更新URL
        subprocess.run(['git', 'remote', 'set-url', 'origin', repo_url], check=True)
    
    # 推送到GitHub
    print("推送到GitHub...")
    try:
        subprocess.run(['git', 'push', '-u', 'origin', 'main'], check=True)
        print("✅ 推送成功!")
        return True
    except:
        try:
            subprocess.run(['git', 'push', '-u', 'origin', 'master'], check=True)
            print("✅ 推送到master分支成功!")
            return True
        except Exception as e:
            print(f"推送失败: {e}")
            return False

def show_next_steps():
    """显示后续步骤"""
    print("\n" + "="*50)
    print("🎉 推送完成! 下一步:")
    print("="*50)
    print("1. 访问您的GitHub仓库页面")
    print("2. 点击顶部的 'Actions' 选项卡")
    print("3. 查看正在运行的构建工作流")
    print("4. 等待构建完成 (通常10-30分钟)")
    print("5. 构建完成后下载APK文件")
    print("\n📱 应用功能:")
    print("- 获取安卓通讯录权限")
    print("- 读取并显示联系人")
    print("- 搜索联系人功能")
    print("- Material Design界面")
    print("\n⚙️ 构建配置:")
    print("- 目标API: 34 (Android 14)")
    print("- 最低API: 23 (Android 6.0)")
    print("- 架构: arm64-v8a, armeabi-v7a")

def main():
    """主函数"""
    if simple_push():
        show_next_steps()
        print("\n✨ GitHub Actions会自动开始构建您的APK!")
    else:
        print("\n❌ 操作失败，请检查错误信息")
        sys.exit(1)

if __name__ == '__main__':
    main()