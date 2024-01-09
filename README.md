# icloud_backup
构建dockerr镜像,备份icloud照片

### 使用步骤:  
1.下载镜像  
2.新建容器    
     (1)装载文件 {群晖上的备份路径} 到 "/app/photos"(容器的工作路径)  
3.第一期启动需要进入容器输入:python icloud_back.py {apple_id} {password}  
