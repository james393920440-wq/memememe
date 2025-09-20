#!/usr/bin/env python3
"""
极简版本推送脚本 - 确保构建成功
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
    print("开始推送极简版本到GitHub...")
    
    # 检查Git状态
    print("\n1. 检查Git状态")
    if not run_command("git status"):
        return False
    
    # 备份当前版本
    print("\n2. 备份当前版本")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if os.path.exists("main.py"):
        shutil.copy("main.py", f"main_before_minimal_{timestamp}.py")
        print("已备份 main.py")
    
    if os.path.exists("buildozer.spec"):
        shutil.copy("buildozer.spec", f"buildozer_before_minimal_{timestamp}.spec")
        print("已备份 buildozer.spec")
    
    # 使用极简版本
    print("\n3. 使用极简版本")
    if os.path.exists("main_minimal.py"):
        shutil.copy("main_minimal.py", "main.py")
        print("已替换 main.py 为极简版本")
    
    if os.path.exists("buildozer_minimal.spec"):
        shutil.copy("buildozer_minimal.spec", "buildozer.spec")
        print("已替换 buildozer.spec 为极简版本")
    
    # 添加到Git
    print("\n4. 添加到Git")
    run_command("git add main.py")
    run_command("git add buildozer.spec")
    run_command("git add main_minimal.py")
    run_command("git add buildozer_minimal.spec")
    run_command("git add push_minimal.py")
    
    # 提交更改
    print("\n5. 提交更改")
    commit_msg = f"使用极简版本确保构建成功 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    if not run_command(f'git commit -m "{commit_msg}"'):
        print("提交失败，可能是没有更改")
        return False
    
    # 推送到GitHub
    print("\n6. 推送到GitHub")
    if run_command("git push origin master"):
        print("\n✅ 极简版本推送成功！")
        print("GitHub Actions 将开始构建极简版本...")
        print("\n极简版本特点：")
        print("- 只使用纯Kivy，无安卓依赖")
        print("- 无特殊权限要求")
        print("- 模拟联系人数据")
        print("- 最稳定的构建配置")
        print("\n构建状态查看：")
        print("- 访问: https://github.com/james393920440-wq/memememe/actions")
        print("- 构建完成后APK将在Artifacts中提供下载")
        print("\n这个版本应该100%能构建成功！")
        return True
    else:
        print("\n❌ 推送失败")
        return False

if __name__ == "__main__":
    main()