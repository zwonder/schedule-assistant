# 数据库权限配置说明

## 问题原因
CloudBase 数据库默认安全规则为只读或完全拒绝访问，导致无法读写数据。

## 解决方案

需要在 CloudBase 控制台配置数据库安全规则。

### 方法1：通过 CloudBase 控制台配置（推荐）

1. 访问 [CloudBase 控制台](https://console.cloud.tencent.com/tcb)
2. 选择环境：`zwonder-8gq5j7i479378123`
3. 进入「数据库」→「安全规则」
4. 添加以下规则：

```json
{
  "read": "auth != null",
  "write": "auth != null"
}
```

5. 保存并生效

### 方法2：针对每个集合单独配置

如果只想开放部分集合权限，可以分别配置：

#### pa_schedules（日程表）
```json
{
  "read": "auth != null",
  "create": "auth != null",
  "update": "auth != null && auth.uid == doc.author_id",
  "delete": "auth != null && auth.uid == doc.author_id"
}
```

#### pa_user_config（用户配置）
```json
{
  "read": "auth != null",
  "write": "auth != null"
}
```

#### pa_world_posts（广场帖子）
```json
{
  "read": "auth != null",
  "create": "auth != null",
  "update": "auth != null && (auth.uid == doc.author_id)",
  "delete": "auth != null && auth.uid == doc.author_id"
}
```

#### pa_blocklist（拉黑列表）
```json
{
  "read": "auth != null",
  "write": "auth != null"
}
```

## 快速配置（开发环境）

如果是测试/开发环境，可以临时设置为：
```json
{
  "read": true,
  "write": true
}
```

⚠️ **注意**：生产环境请勿使用此配置，任何人都可以删除数据。

## 配置后

1. 刷新浏览器页面
2. 重新登录（匿名或微信登录）
3. 测试功能：
   - 今日待办加载
   - 添加日程
   - 修改昵称
   - 所有日程列表

## 前端修改说明

已修改前端代码，确保所有数据库操作都包含 `author_id` 字段：
- 查询时添加 `where({ author_id: currentOpenid })`
- 创建时添加 `author_id: currentOpenid`

这样可以：
1. 用户只能看到自己的数据
2. 数据隔离更安全
3. 避免权限冲突
