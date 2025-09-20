#!/usr/bin/env python3
"""
简单版本推送脚本 - 使用超简化配置避免构建错误
"""
import os
import subprocess
import shutil
from datetime import datetime

def run_command(cmd, cwd=None):
    """运行命令"""
    print(f"执行: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"错误: {result.stderr}")
        return False
    print(f"输出: {result.stdout}")
    return True

def main():
    """主函数"""
    print("开始推送超简化版本到GitHub...")
    
    # 检查Git状态
    print("\n1. 检查Git状态")
    if not run_command("git status"):
        return False
    
    # 备份原始文件
    print("\n2. 备份原始文件")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if os.path.exists("main.py"):
        shutil.copy("main.py", f"main_backup_{timestamp}.py")
        print("已备份 main.py")
    
    if os.path.exists("buildozer.spec"):
        shutil.copy("buildozer.spec", f"buildozer_backup_{timestamp}.spec")
        print("已备份 buildozer.spec")
    
    # 替换为简化版本
    print("\n3. 使用简化版本")
    if os.path.exists("main_simple.py"):
        shutil.copy("main_simple.py", "main.py")
        print("已替换 main.py 为简化版本")
    
    if os.path.exists("buildozer_simple.spec"):
        shutil.copy("buildozer_simple.spec", "buildozer.spec")
        print("已替换 buildozer.spec 为简化版本")
    
    # 添加到Git
    print("\n4. 添加到Git")
    run_command("git add main.py")
    run_command("git add buildozer.spec")
    run_command("git add main_simple.py")
    run_command("git add buildozer_simple.spec")
    run_command("git add push_simple.py")
    
    # 提交更改
    print("\n5. 提交更改")
    commit_msg = f"使用超简化版本避免构建错误 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    if not run_command(f'git commit -m "{commit_msg}"'):
        print("提交失败，可能是没有更改")
        return False
    
    # 推送到GitHub
    print("\n6. 推送到GitHub")
    if run_command("git push origin master"):
        print("\n✅ 推送成功！")
        print("GitHub Actions 将开始构建超简化版本...")
        print("\n简化版本特点：")
        print("- 使用基本Kivy组件，避免复杂UI依赖")
        print("- 简化的权限处理")
        print("- 基本的联系人获取功能")
        print("- 更稳定的构建配置")
        print("\n构建状态查看：")
        print("- 访问: https://github.com/james393920440-wq/memememe/actions")
        print("- 构建完成后APK将在Artifacts中提供下载")
        return True
    else:
        print("\n❌ 推送失败")
        return False

if __name__ == "__main__":
    main()