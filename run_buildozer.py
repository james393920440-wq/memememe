#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动运行buildozer构建的脚本
"""
import subprocess
import sys
import os

def run_buildozer_with_auto_confirm():
    """自动确认运行buildozer"""
    try:
        # 创建子进程
        process = subprocess.Popen(
            ['buildozer', 'android', 'debug'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # 等待并自动回复确认提示
        stdout, stderr = process.communicate(input='y\n')
        
        print("构建输出:")
        print(stdout)
        
        if stderr:
            print("错误输出:")
            print(stderr)
        
        return process.returncode == 0
        
    except FileNotFoundError:
        print("错误: 未找到buildozer命令")
        return False
    except Exception as e:
        print(f"运行buildozer时出错: {str(e)}")
        return False

if __name__ == '__main__':
    print("开始自动构建APK...")
    success = run_buildozer_with_auto_confirm()
    
    if success:
        print("\n✅ 构建过程启动成功!")
        print("请等待构建完成，这可能需要一些时间...")
    else:
        print("\n❌ 构建启动失败")
        sys.exit(1)