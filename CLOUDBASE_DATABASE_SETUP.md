# CloudBase数据库安全规则配置指南

## 问题原因
前端使用CloudBase JS SDK直接访问数据库时,会根据数据库安全规则进行权限验证。默认情况下,安全规则可能设置为"禁止所有访问",导致前端无法读取/写入数据,报错`Permission denied`。

## 解决方案
在CloudBase控制台为每个数据库集合配置正确的安全规则。

## 详细配置步骤

### 1. 登录CloudBase控制台
访问: https://console.cloud.tencent.com/tcb

### 2. 选择环境
选择环境: `zwonder-8gq5j7i479378123`

### 3. 进入文档型数据库
在左侧菜单找到**文档型数据库**,点击进入

### 4. 配置各个集合的安全规则

对以下每个集合重复相同步骤:
- `pa_schedules` (日程表)
- `pa_user_config` (用户配置)
- `pa_world_posts` (广场帖子)
- `pa_blocklist` (拉黑列表)

#### 具体步骤:
1. 点击集合名称(如`pa_schedules`)
2. 切换到**权限设置**标签页
3. 将"基础权限控制"切换为**安全规则**
4. 点击**编辑规则**按钮
5. 将下面的JSON规则复制粘贴进去
6. 点击**保存**

---

## 各集合安全规则

### 1. pa_schedules (日程表)
```json
{
  "read": "auth != null && doc.author_id == auth.openid",
  "create": "auth != null",
  "update": "auth != null && auth.openid == doc.author_id",
  "delete": "auth != null && auth.openid == doc.author_id"
}
```

**说明**:
- `read`: 只能读取自己的数据(通过`author_id`字段匹配)
- `create`: 登录用户可以创建(创建时需要设置`author_id`)
- `update/delete`: 只能修改/删除自己的数据

---

### 2. pa_user_config (用户配置)
```json
{
  "read": "auth != null && doc.author_id == auth.openid",
  "create": "auth != null",
  "update": "auth != null && auth.openid == doc.author_id",
  "delete": "auth != null && auth.openid == doc.author_id"
}
```

**说明**: 用户配置也是个人数据,需要按用户隔离

---

### 3. pa_world_posts (广场帖子)
```json
{
  "read": "auth != null",
  "create": "auth != null",
  "update": "auth != null && auth.openid == doc.author_id",
  "delete": "auth != null && auth.openid == doc.author_id"
}
```

**说明**:
- `read`: 所有登录用户都可以读取广场帖子
- `create`: 所有登录用户可以发帖
- `update/delete`: 只能修改/删除自己的帖子

---

### 4. pa_blocklist (拉黑列表)
```json
{
  "read": "auth != null && doc.author_id == auth.openid",
  "create": "auth != null",
  "update": "auth != null && auth.openid == doc.author_id",
  "delete": "auth != null && auth.openid == doc.author_id"
}
```

**说明**: 拉黑列表是个人数据,需要按用户隔离

---

## 安全规则语法说明

### 可用的变量
- `auth`: 当前用户信息
  - `auth.openid`: 用户唯一标识
  - `auth.uid`: 用户ID
  - `auth != null`: 检查是否已登录

- `doc`: 当前要操作的数据文档
  - `doc.author_id`: 文档中的`author_id`字段
  - `doc.field_name`: 访问文档的任意字段

### 操作类型
- `read`: 读取数据
- `create`: 创建数据
- `update`: 更新数据
- `delete`: 删除数据

### 常用表达式
```javascript
auth != null              // 必须登录
doc.author_id == auth.openid  // 只能操作自己的数据
true                     // 允许所有操作(开发环境用)
```

---

## 验证配置

配置完成后,访问应用:
1. 打开浏览器访问: http://localhost:5001
2. 登录(匿名登录或微信登录)
3. 测试功能:
   - [ ] 今日待办加载
   - [ ] 添加日程
   - [ ] 标记任务完成
   - [ ] 删除任务
   - [ ] 所有日程列表
   - [ ] 修改昵称
   - [ ] 广场发帖

如果所有功能正常,说明配置成功!

---

## 常见问题

### Q1: 还是提示"Permission denied"
- 检查是否为所有集合都配置了安全规则
- 确认规则JSON语法正确(注意逗号和引号)
- 刷新浏览器后重试

### Q2: 在控制台找不到"安全规则"选项
- 确保点击了具体集合名称(如`pa_schedules`)
- 切换到"权限设置"标签页
- 将"基础权限控制"切换为"安全规则"

### Q3: 匿名用户无法操作
- 确认匿名登录已启用(CloudBase控制台 -> 登录授权 -> 匿名登录)
- 安全规则中`auth != null`包含匿名用户

---

## 开发环境临时方案(不推荐生产环境使用)

如果只是为了快速测试,可以临时设置为允许所有操作:

```json
{
  "read": true,
  "create": true,
  "update": true,
  "delete": true
}
```

⚠️ **警告**: 生产环境绝不能使用此配置,任何人都可以删除您的所有数据!

---

## 产品级建议

1. **生产环境必须配置严格的安全规则**
   - 用户数据必须按用户隔离(使用`author_id`)
   - 删除和更新操作需要额外的权限检查

2. **定期审查安全规则**
   - 根据业务需求调整规则
   - 避免过度开放权限

3. **测试环境可以适当放宽**
   - 使用更宽松的规则方便开发调试
   - 但不要在生产环境使用测试规则
