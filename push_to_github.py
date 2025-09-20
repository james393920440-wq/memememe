#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
推送到GitHub并触发自动构建的脚本
"""
import os
import subprocess
import sys
from datetime import datetime

def run_command(cmd, description=""):
    """运行命令"""
    print(f"\n{'='*50}")
    print(f"执行: {description or cmd}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("错误:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"命令失败: {str(e)}")
        return False

def check_git():
    """检查git状态"""
    print("检查Git状态...")
    
    # 检查git是否安装
    if not run_command('git --version', '检查Git版本'):
        print("错误: 未找到Git，请先安装Git")
        return False
    
    # 检查当前目录状态
    print("\n当前Git状态:")
    run_command('git status', '检查Git状态')
    
    return True

def setup_github_repo():
    """设置GitHub仓库"""
    print("\n设置GitHub仓库...")
    
    repo_url = input("请输入GitHub仓库URL (例如: https://github.com/用户名/仓库名.git): ").strip()
    
    if not repo_url:
        print("错误: 未提供仓库URL")
        return False
    
    # 检查是否已有远程仓库
    result = subprocess.run('git remote get-url origin', shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"当前远程仓库: {result.stdout.strip()}")
        change = input("是否更改为新的仓库? (y/n): ").lower()
        if change != 'y':
            return True
    
    # 添加或更新远程仓库
    if result.returncode == 0:
        run_command(f'git remote set-url origin {repo_url}', '更新远程仓库')
    else:
        run_command(f'git remote add origin {repo_url}', '添加远程仓库')
    
    return True

def commit_and_push():
    """提交并推送代码"""
    print("\n准备提交代码...")
    
    # 添加所有文件
    if not run_command('git add .', '添加所有文件'):
        print("警告: 添加文件失败")
    
    # 检查是否有更改
    result = subprocess.run('git status --porcelain', shell=True, capture_output=True, text=True)
    if not result.stdout.strip():
        print("没有需要提交的更改")
        return True
    
    # 提交代码
    commit_message = f"更新项目 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    if not run_command(f'git commit -m "{commit_message}"', '提交代码'):
        print("错误: 提交失败")
        return False
    
    # 推送到GitHub
    print("\n推送到GitHub...")
    if run_command('git push -u origin main', '推送到main分支'):
        print("✅ 推送成功!")
        return True
    else:
        # 尝试强制推送
        print("尝试强制推送...")
        if run_command('git push -f -u origin main', '强制推送到main分支'):
            print("✅ 强制推送成功!")
            return True
    
    return False

def check_github_actions():
    """检查GitHub Actions配置"""
    print("\n检查GitHub Actions配置...")
    
    actions_file = '.github/workflows/buildozer_action.yml'
    if os.path.exists(actions_file):
        print("✅ GitHub Actions配置文件存在")
        print("构建将在推送后自动开始")
        print("\n构建进度查看方式:")
        print("1. 打开GitHub仓库页面")
        print("2. 点击 'Actions' 选项卡")
        print("3. 查看最新的工作流运行")
        return True
    else:
        print("❌ GitHub Actions配置文件不存在")
        return False

def main():
    """主函数"""
    print("=== 推送到GitHub并触发自动构建 ===")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查git
    if not check_git():
        sys.exit(1)
    
    # 设置GitHub仓库
    if not setup_github_repo():
        sys.exit(1)
    
    # 检查GitHub Actions
    check_github_actions()
    
    # 提交并推送
    if commit_and_push():
        print("\n🎉 操作完成!")
        print("\n下一步:")
        print("1. 访问GitHub仓库查看Actions进度")
        print("2. 等待构建完成 (约10-30分钟)")
        print("3. 在Actions页面下载生成的APK文件")
        print("\n注意: 首次构建可能需要更长时间")
    else:
        print("\n❌ 推送失败，请检查错误信息")
        sys.exit(1)

if __name__ == '__main__':
    main()