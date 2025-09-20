#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
本地APK构建脚本
模拟GitHub Actions的构建过程
"""
import os
import sys
import subprocess
import shutil
from datetime import datetime

def run_command(cmd, description=""):
    """运行命令并显示输出"""
    print(f"\n{'='*60}")
    print(f"执行: {description or cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("错误输出:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"命令执行失败: {str(e)}")
        return False

def prepare_environment():
    """准备构建环境"""
    print("准备构建环境...")
    
    # 备份原始main.py
    if os.path.exists('main.py'):
        backup_name = f'main_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
        shutil.copy('main.py', backup_name)
        print(f"已备份原始main.py到: {backup_name}")
    
    # 使用增强版作为main.py
    if os.path.exists('main_enhanced.py'):
        shutil.copy('main_enhanced.py', 'main.py')
        print("已将main_enhanced.py复制为main.py")
    
    return True

def check_dependencies():
    """检查必要的依赖"""
    print("检查依赖...")
    
    # 检查buildozer
    if not shutil.which('buildozer'):
        print("错误: 未找到buildozer，请先安装: pip install buildozer")
        return False
    
    # 检查Java
    if not shutil.which('java'):
        print("警告: 未找到Java，可能需要安装JDK")
    
    # 检查Python版本
    print(f"Python版本: {sys.version}")
    
    return True

def build_apk():
    """构建APK"""
    print("开始构建APK...")
    
    # 清理之前的构建
    if os.path.exists('.buildozer'):
        print("清理之前的构建缓存...")
        shutil.rmtree('.buildozer')
    
    # 使用yes自动确认buildozer的提示
    print("运行buildozer构建（这可能需要很长时间）...")
    
    try:
        # Windows下使用echo y来自动确认
        print("正在启动buildozer构建过程...")
        process = subprocess.Popen(
            'buildozer -v android debug',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # 实时显示输出
        for line in iter(process.stdout.readline, ''):
            print(line, end='')
            # 检查是否构建完成
            if 'BUILD SUCCESSFUL' in line:
                print("\n✅ 构建成功!")
            elif 'BUILD FAILED' in line:
                print("\n❌ 构建失败!")
                
        process.wait()
        return process.returncode == 0
        
    except Exception as e:
        print(f"构建过程出错: {str(e)}")
        return False

def find_and_show_apk():
    """查找并显示生成的APK"""
    bin_dir = 'bin'
    if os.path.exists(bin_dir):
        apk_files = [f for f in os.listdir(bin_dir) if f.endswith('.apk')]
        if apk_files:
            print(f"\n✅ 找到生成的APK文件:")
            for apk in apk_files:
                apk_path = os.path.join(bin_dir, apk)
                size = os.path.getsize(apk_path) / 1024 / 1024
                print(f"  - {apk} ({size:.2f} MB)")
            return True
        else:
            print("未找到APK文件")
            return False
    else:
        print("bin目录不存在")
        return False

def main():
    """主函数"""
    print("=== 安卓通讯录获取器 APK 本地构建工具 ===")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 准备环境
    if not prepare_environment():
        print("环境准备失败")
        sys.exit(1)
    
    # 构建APK
    if build_apk():
        print("\n构建过程完成!")
        find_and_show_apk()
        print("\n✅ APK构建流程结束!")
        print("注意: 如果构建过程中出现错误，请检查网络连接和依赖安装")
    else:
        print("\n❌ APK构建失败")
        print("建议:")
        print("1. 检查网络连接")
        print("2. 确保所有依赖已安装")
        print("3. 查看上面的错误信息")
        print("4. 考虑使用GitHub Actions进行云端构建")
        sys.exit(1)

if __name__ == '__main__':
    main()