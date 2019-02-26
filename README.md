# FM2RSS
把国内私有的FM APP节目转为Podcast RSS源，可以使用泛用性播客客户端订阅，避免下载多个APP的麻烦

## 目前已经完成的
- [x] 企鹅FM
- [ ] 喜马拉雅

## 使用方式
### Python环境

python3 + 以下包

- requests
- beautifulsoup
- feedgen

### 其他环境
- nginx
- 网页目录（这里用的是默认的/var/www/html）对python执行者可读写
- 可以使用crontab定期调度

### 使用方式
把py文件放在任意位置执行即可，需注意权限问题