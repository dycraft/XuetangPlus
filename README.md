# XuetangPlus

## 开发指南

### page.js
#### 介绍
- 单页路由
- 后退、快进、刷新
#### 使用
- 参考 `welcome/account_bind`
- 参考 官方文档

### swig.js
#### 介绍
- 渲染前端数据，单向绑定（每次更新需要重新render）
- script-template 配合page.js单页路由
#### 使用
- 参考 微信抢票
- 参考 swig.js 官方文档
- 参考 `learn/course_list`

### weui.css
#### 介绍
- css样式表
#### 使用
- 参考 weui.io, 查看源代码

### weui.js
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

### communication
现在设想的就是每个课程开一个空间允许同学们互相交流，菜单里的[师生交流]放弃。  
可以参考现在前端页面的样式，具体要做的就是把每个人说的话存入数据库，前端需求的话get就行了，机制和日历的事件差不多。  
还有新消息通知这应该是个技术活。
