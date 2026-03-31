"""
通过CloudBase API部署数据库安全规则

前置条件:
1. 腾讯云API密钥(腾讯云控制台 -> 访问管理 -> API密钥管理)
2. 安装依赖: pip install tencentcloud-sdk-python

运行: python deploy_database_rules.py
"""

import json
import os
import sys

# 检查是否安装了tencentcloud-sdk
try:
    from tencentcloud.common import credential
    from tencentcloud.common.profile.client_profile import ClientProfile
    from tencentcloud.common.profile.http_profile import HttpProfile
    from tencentcloud.tcb.v20180608 import tcb_client, models
except ImportError:
    print("错误: 需要安装 tencentcloud-sdk-python")
    print("请运行: pip install tencentcloud-sdk-python")
    sys.exit(1)

# CloudBase环境配置
ENV_ID = "zwonder-8gq5j7i479378123"
REGION = "ap-shanghai"

# 数据库安全规则
DATABASE_RULES = {
    "pa_schedules": {
        "read": "auth != null && doc.author_id == auth.openid",
        "create": "auth != null",
        "update": "auth != null && auth.openid == doc.author_id",
        "delete": "auth != null && auth.openid == doc.author_id"
    },
    "pa_user_config": {
        "read": "auth != null && doc.author_id == auth.openid",
        "create": "auth != null",
        "update": "auth != null && auth.openid == doc.author_id",
        "delete": "auth != null && auth.openid == doc.author_id"
    },
    "pa_world_posts": {
        "read": "auth != null",
        "create": "auth != null",
        "update": "auth != null && auth.openid == doc.author_id",
        "delete": "auth != null && auth.openid == doc.author_id"
    },
    "pa_blocklist": {
        "read": "auth != null && doc.author_id == auth.openid",
        "create": "auth != null",
        "update": "auth != null && auth.openid == doc.author_id",
        "delete": "auth != null && auth.openid == doc.author_id"
    }
}


def get_tencentcloud_credentials():
    """获取腾讯云API密钥"""
    secret_id = os.environ.get("TENCENTCLOUD_SECRET_ID")
    secret_key = os.environ.get("TENCENTCLOUD_SECRET_KEY")

    if not secret_id or not secret_key:
        print("\n请提供腾讯云API密钥:")
        print("1. 访问 https://console.cloud.tencent.com/cam/capi")
        print("2. 创建或获取API密钥(SecretId和SecretKey)")

        secret_id = input("\n请输入SecretId: ").strip()
        secret_key = input("请输入SecretKey: ").strip()

        if not secret_id or not secret_key:
            print("错误: 必须提供API密钥")
            return None

    return secret_id, secret_key


def deploy_safe_rule(client, collection_name, rule_json):
    """为指定集合部署安全规则"""
    try:
        req = models.ModifySafeRuleRequest()
        params = {
            "EnvId": ENV_ID,
            "Rules": [{
                "Name": f"db.{collection_name}",
                "Rule": json.dumps(rule_json, ensure_ascii=False)
            }]
        }
        req.from_json_string(json.dumps(params))

        resp = client.ModifySafeRule(req)

        print(f"✅ {collection_name}: 部署成功")
        return True

    except Exception as e:
        print(f"❌ {collection_name}: 部署失败 - {str(e)}")
        return False


def main():
    print("\n" + "="*60)
    print("CloudBase 数据库安全规则部署工具")
    print("="*60)
    print(f"\n环境ID: {ENV_ID}")
    print(f"区域: {REGION}")

    # 获取API密钥
    creds = get_tencentcloud_credentials()
    if not creds:
        return

    secret_id, secret_key = creds

    # 初始化客户端
    try:
        cred = credential.Credential(secret_id, secret_key)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "tcb.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = tcb_client.TcbClient(cred, REGION, clientProfile)

        print("\n✅ CloudBase客户端初始化成功")

    except Exception as e:
        print(f"\n❌ 初始化失败: {str(e)}")
        return

    # 显示即将部署的规则
    print("\n即将部署以下安全规则:")
    print("-" * 60)
    for collection_name, rules in DATABASE_RULES.items():
        print(f"\n集合: {collection_name}")
        print(json.dumps(rules, indent=2, ensure_ascii=False))

    # 确认部署
    confirm = input("\n\n确认部署以上规则? (yes/no): ").strip().lower()
    if confirm not in ["yes", "y"]:
        print("已取消部署")
        return

    # 逐个部署规则
    print("\n开始部署...")
    print("-" * 60)

    success_count = 0
    fail_count = 0

    for collection_name, rules in DATABASE_RULES.items():
        if deploy_safe_rule(client, collection_name, rules):
            success_count += 1
        else:
            fail_count += 1

    # 输出结果
    print("\n" + "="*60)
    print(f"部署完成! 成功: {success_count}, 失败: {fail_count}")
    print("="*60)

    if fail_count == 0:
        print("\n✅ 所有规则部署成功!")
        print("\n下一步:")
        print("1. 访问应用: http://localhost:5001")
        print("2. 测试功能: 今日待办、添加日程、修改昵称等")
    else:
        print("\n⚠️ 部分规则部署失败,请检查错误信息")
        print("\n建议:")
        print("1. 确认腾讯云API密钥正确")
        print("2. 确认环境ID: " + ENV_ID)
        print("3. 参考 CLOUDBASE_DATABASE_SETUP.md 手动配置")


if __name__ == "__main__":
    main()
