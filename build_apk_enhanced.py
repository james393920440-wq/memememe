#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APK构建脚本 - 用于打包main_enhanced.py
"""
import os
import sys
import shutil
import subprocess
from datetime import datetime

def backup_original_main():
    """备份原始的main.py文件"""
    if os.path.exists('main.py'):
        backup_name = f'main_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
        shutil.copy('main.py', backup_name)
        print(f"已备份原始main.py到: {backup_name}")
        return backup_name
    return None

def prepare_build():
    """准备构建环境"""
    print("正在准备构建环境...")
    
    # 检查必要的文件
    required_files = ['main_enhanced.py', 'buildozer.spec']
    for file in required_files:
        if not os.path.exists(file):
            print(f"错误: 缺少必要文件 {file}")
            return False
    
    # 备份原始main.py
    backup_name = backup_original_main()
    
    # 将main_enhanced.py复制为main.py
    try:
        shutil.copy('main_enhanced.py', 'main.py')
        print("已将main_enhanced.py复制为main.py")
    except Exception as e:
        print(f"复制文件失败: {str(e)}")
        return False
    
    return True

def build_apk():
    """构建APK"""
    print("开始构建APK...")
    
    try:
        # 清理之前的构建
        if os.path.exists('.buildozer'):
            print("清理之前的构建缓存...")
            shutil.rmtree('.buildozer')
        
        # 运行buildozer构建
        print("运行buildozer构建...")
        result = subprocess.run([
            'buildozer', '-v', 'android', 'debug'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("APK构建成功!")
            return True
        else:
            print(f"构建失败，错误信息:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("错误: 未找到buildozer命令，请确保已安装buildozer")
        return False
    except Exception as e:
        print(f"构建过程出错: {str(e)}")
        return False

def find_apk():
    """查找生成的APK文件"""
    bin_dir = 'bin'
    if os.path.exists(bin_dir):
        for file in os.listdir(bin_dir):
            if file.endswith('.apk'):
                return os.path.join(bin_dir, file)
    return None

def main():
    """主函数"""
    print("=== 安卓通讯录获取器 APK 构建工具 ===")
    print(f"构建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 准备构建
    if not prepare_build():
        print("构建准备失败，退出程序")
        sys.exit(1)
    
    # 构建APK
    if build_apk():
        # 查找APK文件
        apk_path = find_apk()
        if apk_path:
            print(f"\n✅ APK构建完成!")
            print(f"APK文件路径: {apk_path}")
            print(f"文件大小: {os.path.getsize(apk_path) / 1024 / 1024:.2f} MB")
        else:
            print("构建成功但找不到APK文件，请检查bin目录")
    else:
        print("\n❌ APK构建失败")
        sys.exit(1)

if __name__ == '__main__':
    main()