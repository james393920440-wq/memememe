[app]
# 应用标题
title = 极简通讯录

# 包名
package.name = minimalcontacts

# 包域名
package.domain = com.example

# 源码目录
source.dir = .

# 主程序文件
source.main = main_minimal.py

# 源码包含扩展名
source.include_exts = py,png,jpg,kv,atlas

# 版本号
version = 1.0.0

# 依赖要求 - 只使用最基本的依赖
requirements = python3,kivy

# 安卓权限 - 不需要特殊权限
android.permissions = INTERNET

# API级别 - 使用稳定版本
android.api = 29
android.minapi = 21
android.ndk = 23b

# 构建工具版本
android.buildtools_version = 29.0.3

# 架构支持 - 只支持主要架构
android.archs = arm64-v8a

# 支持方向
orientation = portrait

# 日志级别
log_level = 2

# 调试模式
android.debuggable = True

[buildozer]
# Buildozer版本
version = 1.5.0