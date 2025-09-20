# CSDN-demo
这是一个Django学习项目，构建了一个仿CSDN的简易博客系统，使用了Bootstrap框架进行前端页面的设计和布局。

## 技术栈
- 后端：Django
- 前端：Bootstrap / Jquery
- 数据库：MySQL
- 缓存：Redis
- 其他：wangEditor / highlight.js

> 注册时的验证码服务由QQ邮箱提供，需要在QQ邮箱中开启SMTP服务并获取授权码。
> 使用的随机头像API: https://api.dicebear.com/9.x/avataaars/svg?seed=xxx


## 启动Celery Worker
在Windows环境下,
```
celery -A csdn worker -l info -P solo
# 或者
celery -A csdn worker -l info -P threads --concurrency=4
```