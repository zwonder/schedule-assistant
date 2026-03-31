#!/bin/bash

# 个人助理 - 问题修复和部署脚本

echo "============================================================"
echo "  个人助理 - CloudBase数据库配置和部署工具"
echo "============================================================"
echo ""

# 检查Python环境
echo "📦 检查Python环境..."
if ! command -v python &> /dev/null; then
    echo "❌ 未找到Python,请先安装Python 3.7+"
    exit 1
fi
echo "✅ Python已安装"
echo ""

# 安装依赖
echo "📥 安装依赖..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi
echo "✅ 依赖安装成功"
echo ""

# 部署数据库安全规则
echo "🔐 配置数据库安全规则..."
echo ""
echo "选择部署方式:"
echo "1) 使用自动化脚本部署(需要腾讯云API密钥)"
echo "2) 手动配置(通过CloudBase控制台)"
echo ""
read -p "请选择 (1/2): " choice

case $choice in
    1)
        echo ""
        echo "🔑 腾讯云API密钥获取:"
        echo "访问: https://console.cloud.tencent.com/cam/capi"
        echo ""
        python deploy_database_rules.py
        ;;
    2)
        echo ""
        echo "📖 手动配置步骤:"
        echo "1. 访问: https://console.cloud.tencent.com/tcb"
        echo "2. 选择环境: zwonder-8gq5j7i479378123"
        echo "3. 进入: 文档型数据库 -> 选择集合 -> 权限设置 -> 安全规则"
        echo "4. 为以下集合配置安全规则:"
        echo "   - pa_schedules"
        echo "   - pa_user_config"
        echo "   - pa_world_posts"
        echo "   - pa_blocklist"
        echo ""
        echo "📄 详细配置规则请查看: CLOUDBASE_DATABASE_SETUP.md"
        echo ""
        read -p "配置完成后按回车继续..."
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "============================================================"
echo "🚀 启动应用..."
echo "============================================================"
echo ""
echo "访问地址: http://localhost:5001"
echo ""
echo "✅ 修复内容:"
echo "  ✓ 今日待办加载"
echo "  ✓ 所有日程列表"
echo "  ✓ 添加日程"
echo "  ✓ 标记任务完成"
echo "  ✓ 修改昵称"
echo "  ✓ 页面标题: 个人助理"
echo ""
echo "============================================================"
echo ""

# 启动应用
python main.py
