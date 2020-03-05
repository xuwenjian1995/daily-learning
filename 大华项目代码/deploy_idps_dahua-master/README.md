# deploy_idps_dahua

大华idps版本管理
```
1.提交代码  
2.去idps1机器/AI/deploy_idps_stable-3.0-stable-52ecea0ffc7c705d28b167fc8d9ab06bd66bf549目录
3.git pull拉取代码  
4.如果更改了yml文件则需要重启集群  
  docker stack rm dahua  删除集群  
  docker ps 确认dahua集群相关容器是否全部结束
  sh run_dahua.sh  启动集群
5.如果没有更改yml
  docker service update --force  xxxxxxxx
  xxxxx为docker service ls | grep mysql 这样搜到的服务名称
```