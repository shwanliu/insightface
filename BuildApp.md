# 1.构建DockerNginx 图片服务器镜像

## 首先本地创建一个要挂载到容器的图片根目录，
        mkdir /opt/images

## 使用docker 拉取一个Nginx镜像
        docker pull nginx

## 创建一个nginx.conf
        1. 配置监听端口，注意不要冲突
        2. 设置图片根目录

## 使用docker run 命令
        sudo docker run --name image-server -itd -p 8082:8080  \
        -v /Users/liuxiaoying/workplace/CV_Code/insightface/src/api/conf/nginx.conf:/etc/nginx/nginx.conf  \
        -v /opt/images/test:/opt/images/test nginx

## 使用docker run 命令，在实验室进行部署
        sudo docker run --name image-server -itd -p 8082:8080  \
        -v /home/shawnliu/workPlace/insightface/src/api/conf/nginx.conf:/etc/nginx/nginx.conf  \
        -v /home/shawnliu/workPlace/Face_server/images/test:/opt/images/test nginx

# 2.使用python:3.5 构建 人脸识别 insightface镜像

    docker pull python:3.5

# 3.数据库的搭建，用于人脸特征的保存 使用的是MySQL，
    ## 通过数据库的读取操作，去掉原先的单次执行的demo实现
    ### 目前只使用一个表，表的内容包含了
    ---------入库人员的ID
    ---------入库人员的姓名
    ---------入库人脸的特征
    ---------图片保存名称
    ## 通过annoy在高维空间找到近似的特征，进行计算，annoy的查找时间复杂度是O(logN), \ 
        对于大规模的人脸数据特征近似计算比较快
    ## 数据库的操作包括增删改查，这些命令都需要在熟悉一下

# 4.接口的不断添加以及完善工作
    ## 即存的接口包括人脸入库，人脸验证，人脸验证
        接口的参数定义，由于没有经过仔细的探索，比较粗糙，response的定义也比较粗糙，所以前期的需求还是十分的重要的