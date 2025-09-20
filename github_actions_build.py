#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GitHub Actions风格的本地构建脚本
模拟GitHub Actions环境进行APK构建
"""
import os
import sys
import subprocess
import shutil
import tempfile
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

def setup_environment():
    """设置构建环境"""
    print("设置构建环境...")
    
    # 安装依赖
    dependencies = [
        'buildozer',
        'cython==3.0.11',
        'python-for-android'
    ]
    
    for dep in dependencies:
        print(f"安装 {dep}...")
        if not run_command(f'pip install {dep}', f'安装 {dep}'):
            print(f"警告: 安装 {dep} 失败")
    
    return True

def prepare_project():
    """准备项目文件"""
    print("准备项目文件...")
    
    # 备份原始main.py
    if os.path.exists('main.py'):
        backup_name = f'main_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
        shutil.copy('main.py', backup_name)
        print(f"已备份原始main.py到: {backup_name}")
    
    # 使用增强版作为main.py
    if os.path.exists('main_enhanced.py'):
        shutil.copy('main_enhanced.py', 'main.py')
        print("已将main_enhanced.py复制为main.py")
    
    # 清理构建缓存
    for cache_dir in ['.buildozer', 'bin']:
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print(f"已清理 {cache_dir}")
    
    return True

def try_alternative_build():
    """尝试替代构建方法"""
    print("尝试替代构建方法...")
    
    # 方法1: 使用python-for-android直接构建
    print("方法1: 使用python-for-android...")
    
    # 创建构建目录
    build_dir = 'p4a_build'
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)
    
    # 准备构建脚本
    build_script = f"""
import os
os.system('python-for-android apk --private . --package=com.example.contacts --name="通讯录获取器" --version=1.0 --bootstrap=sdl2 --requirements=python3,kivy,kivymd,android --permission=READ_CONTACTS --permission=INTERNET --arch=arm64-v8a')
"""
    
    with open(os.path.join(build_dir, 'build.py'), 'w', encoding='utf-8') as f:
        f.write(build_script)
    
    # 尝试运行
    success = run_command(f'cd {build_dir} && python build.py', '运行python-for-android构建')
    
    if success:
        # 查找生成的APK
        for root, dirs, files in os.walk(build_dir):
            for file in files:
                if file.endswith('.apk'):
                    apk_path = os.path.join(root, file)
                    target_path = os.path.join('bin', file)
                    os.makedirs('bin', exist_ok=True)
                    shutil.copy(apk_path, target_path)
                    print(f"✅ 找到APK: {target_path}")
                    return True
    
    return False

def create_manual_build_guide():
    """创建手动构建指南"""
    guide_content = f"""
# 安卓通讯录获取器 APK 构建指南

## 方法1: GitHub Actions (推荐)
1. 将代码推送到GitHub仓库
2. GitHub Actions会自动触发构建
3. 在Actions页面下载生成的APK文件

## 方法2: 使用WSL (Windows子系统Linux)
1. 安装WSL和Ubuntu
2. 在WSL中运行以下命令：
   ```bash
   sudo apt update
   sudo apt install -y python3-pip openjdk-17-jdk git
   pip3 install buildozer cython
   buildozer android debug
   ```

## 方法3: 使用Docker
1. 安装Docker
2. 运行：
   ```bash
   docker run -it --rm -v $(pwd):/workspace kivy/buildozer
   cd /workspace
   buildozer android debug
   ```

## 方法4: 云端构建服务
- 使用GitHub Codespaces
- 使用GitPod
- 使用其他云端Linux环境

当前项目状态:
- 主文件: main_enhanced.py (已准备)
- 构建配置: buildozer.spec (已配置)
- GitHub Actions: .github/workflows/buildozer_action.yml (已配置)

构建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    with open('BUILD_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("已创建构建指南: BUILD_GUIDE.md")

def main():
    """主函数"""
    print("=== GitHub Actions风格APK构建工具 ===")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 设置环境
    setup_environment()
    
    # 准备项目
    prepare_project()
    
    # 尝试替代构建
    success = try_alternative_build()
    
    if success:
        print("\n✅ APK构建成功!")
    else:
        print("\n❌ 本地构建失败")
        print("创建替代构建指南...")
        create_manual_build_guide()
        print("\n📖 请查看 BUILD_GUIDE.md 了解其他构建方法")
        print("推荐使用方法1 (GitHub Actions) 进行云端构建")

if __name__ == '__main__':
    main()