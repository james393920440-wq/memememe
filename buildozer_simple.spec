[app]
# 应用标题
title = 简单通讯录

# 包名
package.name = simplecontacts

# 包域名
package.domain = com.example

# 源码目录
source.dir = .

# 主程序文件
source.main = main_simple.py

# 源码包含扩展名
source.include_exts = py,png,jpg,kv,atlas

# 版本号
version = 1.0.0

# 依赖要求
requirements = python3,kivy,android-permissions,pyjnius

# 安卓权限
android.permissions = READ_CONTACTS,INTERNET

# API级别 - 使用较新版本但兼容性好
android.api = 30
android.minapi = 21
android.ndk = 23b

# 构建工具版本
android.buildtools_version = 30.0.3

# 架构支持
android.archs = arm64-v8a, armeabi-v7a

# 应用图标
icon.filename = %(source.dir)s/icon.png

# 启动画面
presplash.filename = %(source.dir)s/presplash.png

# 支持方向
orientation = portrait

# 日志级别
log_level = 2

# 调试模式
android.debuggable = True

# 忽略警告
android.warnings = all

[buildozer]
# Buildozer版本
version = 1.5.0