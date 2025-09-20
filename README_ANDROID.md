# 安卓通讯录获取器

这是一个使用Kivy框架开发的安卓应用，可以读取设备通讯录中的联系人信息。

## 功能特点

✅ **真实通讯录读取**: 使用Android API读取设备中的真实联系人数据  
✅ **中文界面**: 完全中文化的用户界面  
✅ **权限管理**: 自动处理Android运行时权限请求  
✅ **现代化UI**: 使用KivyMD提供Material Design风格界面  
✅ **异步加载**: 后台线程获取数据，不阻塞UI  
✅ **错误处理**: 完善的错误提示和处理机制  
✅ **数据刷新**: 支持重新获取最新联系人数据  

## 应用截图

*主界面*                    *联系人列表*
┌─────────────────────┐    ┌─────────────────────┐
│  安卓通讯录获取器    │    │  通讯录联系人      │
│                     │    │                     │
│  安卓通讯录读取工具  │    │  ┌─────────────────┐│
│                     │    │  │ 张三            ││
│  点击按钮获取设备    │    │  │ 13800138000     ││
│  通讯录联系人        │    │  ├─────────────────┤│
│                     │    │  │ 李四            ││
│  ┌─────────────────┐│    │  │ 13900139000     ││
│  │   获取通讯录     ││    │  ├─────────────────┤│
│  └─────────────────┘│    │  │ 王五            ││
│                     │    │  │ 13700137000     ││
│  ┌─────────────────┐│    │  └─────────────────┘│
│  │   检查权限       ││    │                     │
│  └─────────────────┘│    │                     │
│                     │    │                     │
│  准备就绪           │    │                     │
└─────────────────────┘    └─────────────────────┘

## 技术架构

- **框架**: Kivy + KivyMD
- **语言**: Python 3
- **打包工具**: Buildozer
- **权限管理**: python-for-android
- **Android API**: pyjnius

## 文件结构

```
SAMPLE-KIVYMD-APP-main/
├── main.py                    # 主应用代码
├── buildozer.spec            # 打包配置文件
├── build_apk.py               # 自动打包脚本
├── images/                    # 图标和启动画面
│   ├── favicon.png           # 应用图标
│   └── presplash.png         # 启动画面
└── README_ANDROID.md          # 本文档
```

## 开发环境搭建

### 1. 安装Python依赖

```bash
pip install kivy==2.3.1
pip install https://github.com/kivymd/KivyMD/archive/master.zip
pip install python-for-android
pip install buildozer
pip install pyjnius
pip install android
```

### 2. 安装系统依赖

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install -y python3-pip openjdk-8-jdk git zip unzip
sudo apt install -y python3-setuptools python3-venv
```

#### macOS:
```bash
brew install python3 git
brew cask install android-sdk
```

#### Windows:
- 安装Python 3.7+
- 安装Java JDK 8+
- 安装Git
- 安装Android SDK

### 3. 安装Android SDK

```bash
# 下载并安装Android SDK
wget https://dl.google.com/android/repository/commandlinetools-linux-8512546_latest.zip
unzip commandlinetools-linux-8512546_latest.zip
mkdir -p ~/android-sdk/cmdline-tools
mv cmdline-tools ~/android-sdk/cmdline-tools/latest

# 设置环境变量
echo 'export ANDROID_SDK_ROOT=~/android-sdk' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_SDK_ROOT/cmdline-tools/latest/bin' >> ~/.bashrc
source ~/.bashrc

# 安装必要的SDK组件
sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"
```

## 应用功能详解

### 1. 权限管理

应用会自动检查并请求以下权限：
- `android.permission.READ_CONTACTS`: 读取通讯录权限
- `android.permission.INTERNET`: 网络权限（用于调试）

### 2. 联系人获取

应用通过Android的ContentResolver API读取设备通讯录：
```python
# 获取联系人URI
ContactsContract = autoclass('android.provider.ContactsContract')
uri = ContactsContract.Contacts.CONTENT_URI

# 查询联系人
cursor = content_resolver.query(uri, None, None, None, None)
```

### 3. 数据展示

使用KivyMD的TwoLineListItem组件展示联系人信息：
- 第一行：联系人姓名
- 第二行：电话号码

### 4. 错误处理

完善的错误处理机制：
- 权限拒绝提示
- 无联系人数据提示
- 系统错误提示

## 打包成APK

### 方法一：使用自动打包脚本

```bash
python build_apk.py
```

脚本会自动：
1. 检查环境依赖
2. 准备项目文件
3. 创建requirements.txt
4. 执行buildozer打包

### 方法二：手动打包

```bash
# 清理旧的构建
rm -rf .buildozer bin

# 构建debug版本
buildozer android debug

# 构建release版本
buildozer android release
```

### 构建输出

构建完成后，APK文件位于`bin/`目录下：
- `contactsreader-debug.apk`: 调试版本
- `contactsreader-release.aab`: 发布版本（Google Play）

## 安装和测试

### 1. 启用开发者模式

在安卓设备上：
1. 设置 → 关于手机 → 版本号（连续点击7次）
2. 设置 → 开发者选项 → 启用USB调试

### 2. 安装APK

```bash
# 连接设备
adb devices

# 安装APK
adb install bin/contactsreader-debug.apk
```

### 3. 运行应用

1. 在设备上找到"通讯录获取器"应用
2. 授予读取联系人权限
3. 点击"获取通讯录"按钮

## 配置说明

### buildozer.spec重要配置

```ini
[app]
title = 通讯录获取器
package.name = contactsreader
package.domain = org.novfensec

# 权限配置
android.permissions = android.permission.READ_CONTACTS, android.permission.INTERNET

# Android API配置
android.api = 34
android.minapi = 23

# 架构支持
android.archs = arm64-v8a, armeabi-v7a

# 依赖库
requirements = python3, kivy==2.3.1, https://github.com/kivymd/KivyMD/archive/master.zip, pyjnius, android
```

## 常见问题

### 1. 中文显示问题

如果在某些设备上中文显示为方框，可以尝试：
- 在buildozer.spec中添加中文字体文件
- 使用系统默认字体
- 在代码中动态注册字体

### 2. 权限问题

如果无法获取联系人：
- 确保授予了读取联系人权限
- 检查设备是否有联系人数据
- 查看logcat日志获取详细信息

### 3. 构建失败

如果buildozer构建失败：
- 检查网络连接（需要下载依赖）
- 确保所有依赖已正确安装
- 查看构建日志定位问题
- 尝试清理构建缓存

### 4. 应用崩溃

如果应用运行崩溃：
- 使用adb logcat查看崩溃日志
- 检查权限是否正确处理
- 确保Android API版本兼容

## 调试技巧

### 1. 查看日志

```bash
# 查看设备日志
adb logcat | grep python

# 查看应用日志
adb logcat | grep contactsreader
```

### 2. 测试权限

```bash
# 检查应用权限
adb shell dumpsys package org.novfensec.contactsreader | grep permission
```

### 3. 性能分析

```bash
# 监控CPU和内存使用
adb shell top | grep contactsreader
```

## 扩展功能

### 可以添加的功能：

1. **联系人搜索**: 支持按姓名或电话号码搜索
2. **联系人详情**: 显示更多联系人信息
3. **导出功能**: 将联系人导出为CSV或vCard格式
4. **分组显示**: 按字母顺序分组显示联系人
5. **多语言支持**: 支持英文等其他语言
6. **主题切换**: 支持深色模式
7. **联系人编辑**: 允许编辑联系人信息
8. **云同步**: 与云服务同步联系人

## 发布到应用商店

### 1. 准备发布版本

```bash
# 构建发布版本
buildozer android release

# 签名APK（需要keystore）
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my-release-key.keystore bin/contactsreader-release-unsigned.apk alias_name
```

### 2. Google Play发布

1. 注册Google Play开发者账号
2. 准备应用截图和描述
3. 上传签名的APK/AAB文件
4. 填写应用信息
5. 提交审核

### 3. 其他应用商店

- 华为应用市场
- 小米应用商店
- 应用宝
- 360手机助手

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 邮箱: [your-email@example.com]
- GitHub Issues: [项目Issues页面]

---

**注意**: 本应用需要读取设备通讯录权限，请确保在隐私政策中明确说明数据使用方式。