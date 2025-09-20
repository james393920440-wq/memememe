#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安卓APK打包脚本
使用buildozer将Kivy应用打包成安卓APK文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_environment():
    """检查打包环境"""
    print("检查打包环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major != 3 or python_version.minor < 7:
        print("警告: 建议使用Python 3.7或更高版本")
    
    # 检查buildozer
    try:
        result = subprocess.run(['buildozer', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"buildozer版本: {result.stdout.strip()}")
        else:
            print("buildozer未安装或未配置到PATH")
            return False
    except FileNotFoundError:
        print("buildozer未安装，请先安装: pip install buildozer")
        return False
    
    # 检查Java
    try:
        result = subprocess.run(['java', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("Java环境: 已安装")
        else:
            print("Java未安装，请先安装Java JDK")
            return False
    except FileNotFoundError:
        print("Java未安装，请先安装Java JDK")
        return False
    
    return True

def prepare_project():
    """准备项目文件"""
    print("准备项目文件...")
    
    # 检查必要文件
    required_files = ['main.py', 'buildozer.spec']
    for file in required_files:
        if not os.path.exists(file):
            print(f"错误: 缺少必要文件 {file}")
            return False
    
    # 创建必要的目录
    dirs = ['images', 'bin']
    for dir_name in dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"创建目录: {dir_name}")
    
    # 检查图标文件
    icon_files = ['images/favicon.png', 'images/presplash.png']
    for icon in icon_files:
        if not os.path.exists(icon):
            print(f"警告: 缺少图标文件 {icon}")
    
    return True

def build_apk(build_type='debug'):
    """构建APK"""
    print(f"开始构建{build_type}版本的APK...")
    
    # 清理旧的构建
    if os.path.exists('.buildozer'):
        print("清理旧的构建文件...")
        shutil.rmtree('.buildozer')
    
    # 构建命令
    cmd = ['buildozer']
    if build_type == 'debug':
        cmd.extend(['android', 'debug'])
    elif build_type == 'release':
        cmd.extend(['android', 'release'])
    else:
        print(f"不支持的构建类型: {build_type}")
        return False
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        # 执行构建
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("构建成功!")
            
            # 查找生成的APK文件
            bin_dir = Path('bin')
            if bin_dir.exists():
                apk_files = list(bin_dir.glob('*.apk'))
                if apk_files:
                    print(f"生成的APK文件:")
                    for apk in apk_files:
                        print(f"  - {apk}")
                        print(f"  文件大小: {apk.stat().st_size / 1024 / 1024:.2f} MB")
                else:
                    print("未找到生成的APK文件")
            
            return True
        else:
            print(f"构建失败，返回码: {result.returncode}")
            print("错误输出:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"构建过程出错: {str(e)}")
        return False

def create_requirements_txt():
    """创建requirements.txt文件"""
    requirements = [
        "kivy==2.3.1",
        "https://github.com/kivymd/KivyMD/archive/master.zip",
        "python-for-android",
        "pyjnius",
        "android",
        "exceptiongroup",
        "asynckivy",
        "asyncgui",
        "materialyoucolor"
    ]
    
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        for req in requirements:
            f.write(f"{req}\n")
    
    print("已创建requirements.txt文件")

def main():
    """主函数"""
    print("=== 安卓通讯录获取器APK打包工具 ===")
    print()
    
    # 检查环境
    if not check_environment():
        print("环境检查失败，请先安装必要的工具")
        return
    
    # 准备项目
    if not prepare_project():
        print("项目准备失败")
        return
    
    # 创建requirements.txt
    create_requirements_txt()
    
    # 选择构建类型
    print("\n选择构建类型:")
    print("1. debug版本 (调试版本)")
    print("2. release版本 (发布版本)")
    
    choice = input("请输入选择 (1/2): ").strip()
    build_type = 'debug' if choice == '1' else 'release' if choice == '2' else 'debug'
    
    print(f"\n开始构建{build_type}版本...")
    
    # 构建APK
    success = build_apk(build_type)
    
    if success:
        print(f"\n✅ {build_type}版本APK构建成功!")
        print("APK文件位于 bin/ 目录下")
    else:
        print(f"\n❌ {build_type}版本APK构建失败!")
        print("请检查错误信息并重新尝试")
    
    print("\n构建完成!")

if __name__ == '__main__':
    main()