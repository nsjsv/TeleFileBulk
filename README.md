# TeleFileBulk

用Claude搓的群文件批量下载脚本
各种功能还在陆续完善

## 已完成

- [x] 消息内的文件下载
- [x] 按消息创建文件夹
- [x] 使用 `config.ini` 配置
  - [x] 配置用户ID和hash
  - [x] 配置代理
  - [x] 是否为评论区创建单独文件夹存放
- [x] 下载评论区文件
- [x] 保存当前消息的文本内容
- [x] 断点续传

## 代办

- [ ] 机器人界面交互
- [ ] 队列下载
- [ ] 群文件监控

## 不打算做

- 多线程下载，分块下载，并行下载
  不管怎么样都是一个速度
- 多号并行下载
  只有一个号，暂不考虑做
