#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化稳定版本推送脚本
使用稳定配置构建APK
"""
import os
import sys
import subprocess
import shutil
import time
from datetime import datetime

def run_command(cmd, description):
    """执行命令并显示进度"""
    print(f"\n📋 {description}")
    print(f"📝 命令: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print(f"✅ {description} - 成功")
            if result.stdout:
                print("输出:", result.stdout[:200])
        else:
            print(f"❌ {description} - 失败")
            if result.stderr:
                print("错误:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ {description} - 异常: {str(e)}")
        return False
    
    return True

def main():
    """主函数"""
    print("🚀 稳定版本APK构建工具")
    print("=" * 50)
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查Git状态
    print("\n🔍 检查Git状态...")
    result = subprocess.run("git status", shell=True, capture_output=True, text=True)
    if "nothing to commit" not in result.stdout:
        print("⚠️  检测到未提交的更改")
        response = input("是否先提交更改? (y/n): ").strip().lower()
        if response == 'y':
            if not run_command("git add .", "添加文件到Git"):
                return False
            
            commit_msg = input("请输入提交信息 (默认: 使用稳定版本配置): ").strip()
            if not commit_msg:
                commit_msg = "使用稳定版本配置"
            
            if not run_command(f'git commit -m "{commit_msg}"', "提交更改"):
                return False
    
    # 检查分支
    print("\n🌿 检查当前分支...")
    result = subprocess.run("git branch --show-current", shell=True, capture_output=True, text=True)
    current_branch = result.stdout.strip()
    print(f"当前分支: {current_branch}")
    
    if current_branch != "master":
        print("⚠️  当前不是master分支")
        response = input("是否切换到master分支? (y/n): ").strip().lower()
        if response == 'y':
            if not run_command("git checkout master", "切换到master分支"):
                return False
    
    # 备份原始文件
    print("\n💾 备份原始文件...")
    backup_files = ["main.py", "buildozer.spec"]
    backup_dir = "backup_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(backup_dir, exist_ok=True)
    
    for file in backup_files:
        if os.path.exists(file):
            shutil.copy2(file, backup_dir)
            print(f"✅ 备份 {file} 到 {backup_dir}")
    
    # 使用稳定版本
    print("\n🔄 使用稳定版本配置...")
    
    # 检查稳定文件是否存在
    if os.path.exists("main_stable.py"):
        shutil.copy2("main_stable.py", "main.py")
        print("✅ 使用 main_stable.py 作为主程序")
    
    if os.path.exists("buildozer_stable.spec"):
        shutil.copy2("buildozer_stable.spec", "buildozer.spec")
        print("✅ 使用 buildozer_stable.spec 作为配置文件")
    
    # 添加并提交更改
    print("\n📤 准备推送到GitHub...")
    if not run_command("git add main.py buildozer.spec", "添加稳定版本文件"):
        return False
    
    if not run_command('git commit -m "使用稳定版本配置构建"', "提交稳定版本"):
        # 如果没有更改，继续执行
        print("⚠️  可能没有更改需要提交，继续执行...")
    
    # 推送到GitHub
    print("\n🚀 推送到GitHub触发云端构建...")
    if not run_command("git push origin master", "推送到GitHub"):
        return False
    
    print("\n🎉 推送成功！")
    print("📱 GitHub Actions 将自动开始构建APK")
    print("⏱️  构建预计需要10-30分钟")
    print("\n🔗 查看构建进度:")
    print("1. 访问您的GitHub仓库")
    print("2. 点击 Actions 选项卡")
    print("3. 查看最新的工作流运行")
    print("\n📋 稳定版本特性:")
    print("- 简化的权限处理")
    print("- 更保守的API级别 (21-31)")
    print("- 改进的错误处理")
    print("- 更好的兼容性")
    
    print(f"\n✅ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔄 构建完成后，APK将可在Actions页面下载")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎯 操作成功完成！")
            sys.exit(0)
        else:
            print("\n❌ 操作失败！")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        sys.exit(1)