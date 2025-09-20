#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修正的Git推送脚本 - 自动检测分支名称
"""
import os
import subprocess
import sys
from datetime import datetime

def get_current_branch():
    """获取当前分支名称"""
    try:
        result = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except:
        # 如果上面的命令失败，尝试其他方法
        try:
            result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except:
            return None

def check_git_status():
    """检查git状态"""
    print("检查Git状态...")
    try:
        # 检查是否有未提交的更改
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        if result.stdout.strip():
            print("发现未提交的更改")
            return True
        else:
            print("工作目录干净")
            return False
    except Exception as e:
        print(f"检查git状态失败: {e}")
        return False

def commit_changes():
    """提交更改"""
    print("提交更改...")
    try:
        # 添加所有文件
        subprocess.run(['git', 'add', '.'], check=True)
        
        # 提交
        commit_msg = f"更新通讯录获取器 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        print(f"✅ 提交成功: {commit_msg}")
        return True
    except Exception as e:
        print(f"提交失败: {e}")
        return False

def push_to_github():
    """推送到GitHub"""
    # 获取当前分支
    current_branch = get_current_branch()
    if not current_branch:
        print("❌ 无法确定当前分支")
        return False
    
    print(f"当前分支: {current_branch}")
    
    try:
        # 尝试推送
        print(f"推送到远程 {current_branch} 分支...")
        subprocess.run(['git', 'push', '-u', 'origin', current_branch], check=True)
        print("✅ 推送成功!")
        return True
    except subprocess.CalledProcessError:
        print("推送失败，尝试强制推送...")
        try:
            subprocess.run(['git', 'push', '-f', '-u', 'origin', current_branch], check=True)
            print("✅ 强制推送成功!")
            return True
        except Exception as e:
            print(f"强制推送也失败了: {e}")
            return False

def main():
    """主函数"""
    print("=== 修正版GitHub推送脚本 ===")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查是否有更改需要提交
    has_changes = check_git_status()
    
    if has_changes:
        if not commit_changes():
            print("❌ 提交失败")
            return False
    else:
        print("没有需要提交的更改")
    
    # 推送到GitHub
    if push_to_github():
        print("\n🎉 操作完成!")
        print("\n下一步:")
        print("1. 访问您的GitHub仓库")
        print("2. 点击 'Actions' 选项卡")
        print("3. 查看自动构建进度")
        print("4. 等待构建完成后下载APK")
        return True
    else:
        print("\n❌ 推送失败")
        return False

if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)