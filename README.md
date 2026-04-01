# Personal Schedule Assistant

<div align="center">

![Version](https://img.shields.io/badge/version-v2.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![CloudBase](https://img.shields.io/badge/CloudBase-TCB-orange.svg)

**个人日程助手** - 基于腾讯云开发的多账号日程管理应用

[在线体验](https://zwonder-8gq5j7i479378123-1305999503.tcloudbaseapp.com/index.html) •
[功能介绍](#功能特性) •
[快速开始](#快速开始) •
[技术栈](#技术栈)

</div>

---

## 📖 项目简介

Personal Schedule Assistant 是一款简洁高效的在线日程管理工具，支持多账号登录、数据云端同步、跨设备访问。

### 核心特点

- 🔐 **多账号支持** - 微信登录、邮箱登录、匿名体验
- ☁️ **云端同步** - 基于腾讯云开发，数据永不丢失
- 📱 **响应式设计** - 适配手机、平板、电脑
- 🌤️ **天气提醒** - 智能天气查询，出行无忧
- 📊 **数据可视化** - 直观查看日程分布

---

## ✨ 功能特性

### 日程管理

| 功能 | 说明 |
|------|------|
| 多种周期 | 支持年、月、周、日、单次任务 |
| 提前提醒 | 自定义提前提醒天数（1-30天） |
| 标签分类 | 自由添加标签，便于筛选 |
| 视图切换 | 今日视图 / 所有日程 / 广场 |

### 用户系统

| 功能 | 说明 |
|------|------|
| 微信登录 | 一键授权，便捷登录 |
| 邮箱登录 | 验证码登录，保护隐私 |
| 匿名体验 | 无需注册，快速体验 |
| 数据迁移 | 匿名用户可绑定邮箱合并数据 |

### 附加功能

| 功能 | 说明 |
|------|------|
| 天气预报 | 三日预报 + 出行建议 |
| 纪念日 | 重要日期倒计时提醒 |
| 广场 | 与其他用户分享心得 |

---

## 🚀 快速开始

### 在线体验

直接访问：https://zwonder-8gq5j7i479378123-1305999503.tcloudbaseapp.com/index.html

### 本地运行

```bash
# 克隆项目
git clone https://github.com/zwonder/schedule-assistant.git

# 进入目录
cd schedule-assistant

# 使用任意 HTTP 服务器运行
# Python
python -m http.server 8080

# Node.js
npx serve .

# 然后访问 http://localhost:8080/web/
```

---

## 🛠 技术栈

| 分类 | 技术 |
|------|------|
| 前端 | HTML5 + CSS3 + JavaScript (原生) |
| 后端 | Python (Flask) |
| 数据库 | 腾讯云开发 NoSQL |
| 部署 | 腾讯云 CloudBase |
| 认证 | CloudBase Auth (微信/邮箱) |

---

## 📁 项目结构

```
schedule-assistant/
├── web/
│   └── index.html          # 主页面（单文件应用）
├── core/                   # 核心业务逻辑
├── services/               # 服务层
├── config/                 # 配置文件
├── data/                   # 数据文件
├── app.py                  # Flask 应用入口
├── main.py                 # 主程序
├── requirements.txt        # Python 依赖
├── Dockerfile              # Docker 配置
└── cloudbaserc.json        # 云开发配置
```

---

## 🔧 部署指南

### 腾讯云 CloudBase 部署

1. 登录 [腾讯云开发控制台](https://console.cloud.tencent.com/tcb)
2. 创建环境
3. 安装 CloudBase CLI：`npm install -g @cloudbase/cli`
4. 初始化项目：`tcb init`
5. 部署：`tcb deploy`

### Docker 部署

```bash
docker build -t schedule-assistant .
docker run -p 8080:8080 schedule-assistant
```

---

## 📝 更新日志

### v2.0.0 (2026-04-01)
- ✨ 新增多账号用户系统
- ✨ 支持微信一键登录
- ✨ 新增邮箱验证码登录
- 🎨 优化 UI 界面
- 🐛 修复日程提醒逻辑

### v1.0.0 (2026-03-31)
- 🎉 初始版本发布
- ✨ 日程管理基础功能
- ✨ 天气查询
- ✨ 匿名用户支持

---

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源。

---

<div align="center">

**Made with ❤️ by [zwonder](https://github.com/zwonder)**

</div>
