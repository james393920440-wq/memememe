
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

构建时间: 2025-09-20 11:53:34
