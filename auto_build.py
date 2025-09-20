#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动处理buildozer交互的构建脚本
"""
import os
import sys
import subprocess
import shutil
import time
import threading
from datetime import datetime

def prepare_build():
    """准备构建"""
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
    
    # 清理之前的构建
    if os.path.exists('.buildozer'):
        print("清理之前的构建缓存...")
        shutil.rmtree('.buildozer')
    
    return True

def build_with_interaction():
    """带交互处理的构建"""
    print("开始构建APK...")
    
    try:
        # 启动buildozer进程
        process = subprocess.Popen(
            ['buildozer', '-v', 'android', 'debug'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        build_success = False
        
        # 读取输出并处理交互
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                
                # 检测需要输入的地方
                if 'Do you want to continue' in output or '是否继续' in output:
                    print("检测到确认提示，自动输入 'y'")
                    process.stdin.write('y\n')
                    process.stdin.flush()
                    time.sleep(1)
                
                # 检测构建状态
                if 'BUILD SUCCESSFUL' in output:
                    build_success = True
                    print("\n✅ 构建成功!")
                elif 'BUILD FAILED' in output:
                    print("\n❌ 构建失败!")
                
        return_code = process.poll()
        return return_code == 0 and build_success
        
    except Exception as e:
        print(f"构建过程出错: {str(e)}")
        return False

def find_apk():
    """查找生成的APK"""
    bin_dir = 'bin'
    if os.path.exists(bin_dir):
        apk_files = [f for f in os.listdir(bin_dir) if f.endswith('.apk')]
        if apk_files:
            print(f"\n✅ 找到生成的APK文件:")
            for apk in apk_files:
                apk_path = os.path.join(bin_dir, apk)
                size = os.path.getsize(apk_path) / 1024 / 1024
                print(f"  - {apk} ({size:.2f} MB)")
                return apk_path
    return None

def main():
    """主函数"""
    print("=== 安卓通讯录获取器 APK 自动构建工具 ===")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查buildozer
    if not shutil.which('buildozer'):
        print("错误: 未找到buildozer，请先安装: pip install buildozer")
        sys.exit(1)
    
    # 准备构建
    if not prepare_build():
        print("环境准备失败")
        sys.exit(1)
    
    # 构建APK
    if build_with_interaction():
        print("\n构建过程完成!")
        apk_path = find_apk()
        if apk_path:
            print(f"\n🎉 APK构建成功!")
            print(f"APK文件位置: {os.path.abspath(apk_path)}")
        else:
            print("⚠️ 构建完成但未找到APK文件")
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