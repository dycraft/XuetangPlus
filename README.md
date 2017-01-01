# XuetangPlus

## 开发指南

### 1. page.js
#### 介绍
- 单页路由
- 后退、快进、刷新
#### 使用
- 参考 `welcome/account_bind`
- 参考 官方文档

### 2. swig.js
#### 介绍
- 渲染前端数据，单向绑定（每次更新需要重新render）
- script-template 配合page.js单页路由
#### 使用
- 参考 微信抢票
- 参考 swig.js 官方文档
- 参考 `learn/course_list`

### 3. weui.css
#### 介绍
- css样式表
#### 使用
- 参考 weui.io, 查看源代码

### 4. weui.js
#### 介绍
- 对weui控件(DOM元素)操作的封装
#### 使用
- 参考 weui.io/weuijs/, 查看文档

## API文档

### EventCreate
#### POST

### EventDetail
#### GET
#### POST
todo: 修改事件，参数与`EventCreate`几乎一样

### EventList
#### GET

### EventMonth
#### GET
todo: 与`EventList`几乎一样，只不过参数是月份

### Comment
todo: 急需修改一下代码

### CommentList
#### GET
返回10条最新的消息，可以查看更多
params: openid, curid(最后一条的id，用于下一次请求)
return: [{name("匿名"or"realname"), content}]

### MessageList
#### GET
返回10条最新的消息
params: openid, courseid
return: [{name, content, picUrl}]

### MessageCreate
#### POST
params: openid, courseid, content
return: null
