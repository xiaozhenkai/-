# ishuwoan服务器安装elasticsearch

[TOC]



## java版本要求1.8以上

下载jdk安装包

去[官网](https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html)下载

```
cd /usr/local/src/
wget --no-check-certificate --no-cookies --header "Cookie: oraclelicense=accept-securebackup-cookie" https://download.oracle.com/otn-pub/java/jdk/8u191-b12/2787e4a523244c269598db4e85c51e0c/jdk-8u191-linux-x64.tar.gz
```

解压jdk安装包

```
mkdir /usr/java
tar -zxvf jdk-8u191-linux-x64.tar.gz -C /usr/java
```

设置jdk环境变量

```
# vim /etc/profile
export JAVA_HOME=/usr/java/jdk1.8.0_191
export JRE_HOME=${JAVA_HOME}/jre
export CLASSPATH=.:$JAVA_HOME/jre/lib/rt.jar:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar
export PATH=$PATH:$JAVA_HOME/bin

source /etc/profile
```

查看java版本

```
java -version
java version "1.8.0_191"
Java(TM) SE Runtime Environment (build 1.8.0_191-b12)
Java HotSpot(TM) 64-Bit Server VM (build 25.191-b12, mixed mode)
```

## 安装elasticsearch

去官网下载最新的elasticsearch6.5.4

```
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.5.4.tar.gz
解压到/data目录，并做好软链接
tar zxvf elasticsearch-6.5.4.tar.gz -C /data/
cd /data/ 
ln -s elasticsearch-6.5.4 elasticsearch
```

创建启动用户

```
groupadd es6
useradd -g es6 -m es6
```

修改权限

```
chown -R es6:es6 /data/elasticsearch-*
```

执行方式

前台执行

```
先切换到es6用户
su - es6
cd /data/elasticsearch-6.5.4/bin
前台启动：
./elasticsearch 
后台启动：
./elasticsearch -d
```

现在需要其他服务器访问elasticsearch服务，需要修改配置，默认绑定127.0.0.1,需要改成0.0.0.0

配置在`config`目录下的`elasticsearch.yml`

默认里面的内容都是备注掉的，可以备份文件，然后清空文件，添加如下几行

```
cluster.name: elasticsearch
network.host: 0.0.0.0
http.port: 9200
bootstrap.memory_lock: false 
bootstrap.system_call_filter: false

配置说明

cluster.name表示es集群的名称，可以自定义一个自己需要的集群名称
http.port 表示对外提供http服务时的http端口。
network.host 表示本地监听绑定的ip地址。

最后两行代码是因为一个错误提示：
[4]: system call filters failed to install; check the logs and fix your configuration or disable system call filters at

Centos6不支持SecComp，而ES5.2.0默认bootstrap.system_call_filter为true

禁用：在elasticsearch.yml中配置bootstrap.system_call_filter为false，注意要在Memory下面: 
bootstrap.memory_lock: false 
bootstrap.system_call_filter: false
```

## 几个启动错误

```
[1]: max file descriptors [65535] for elasticsearch process is too low, increase to at least [65536]
[2]: max number of threads [1024] for user [es6] is too low, increase to at least [4096]
[3]: max virtual memory areas vm.max_map_count [65530] is too low, increase to at least [262144]
[4]: system call filters failed to install; check the logs and fix your configuration or disable system call filters at your own risk
```

解决办法：

问题[1]

```
先查看ulimit -SHn
#切换到root用户修改
vim /etc/security/limits.conf
 
# 在最后面追加下面内容
* hard nofile 65536
* soft nofile 65536
```

问题[2]

```
修改vim /etc/security/limits.d/90-nproc.conf
*          soft    nproc     4096
root       soft    nproc     unlimited
```

问题[3]

```
修改/etc/sysctl.conf
最后添加一行
vm.max_map_count=655360
sysctl -p 从配置加载到内核
```

问题[4]

```
Centos6不支持SecComp，而ES5.2.0默认bootstrap.system_call_filter为true

禁用：在elasticsearch.yml中配置bootstrap.system_call_filter为false，注意要在Memory下面: 
bootstrap.memory_lock: false 
bootstrap.system_call_filter: false
```

注意：在root下修改配置后需要重新进入es6才能看到生效的配置。

## 安装Kibana

前言：安装可视化界面的话可以装一下Kibana，Kibana是一个针对Elasticsearch的开源分析及可视化平台，用来搜索、查看交互存储在Elasticsearch索引中的数据。

1、官网下载6.3.0版本的kibana,安装到/opt，上传kibana-6.3.0-linux-x86_64.tar.gz解压并重命名 

```
wget https://artifacts.elastic.co/downloads/kibana/kibana-6.5.4-linux-x86_64.tar.gz

#解压
tar zxvf kibana-6.5.4-linux-x86_64.tar.gz -C /data/
#创建软链接
cd /data/
ln -s kibana-6.5.4-linux-x86_64/ kibana

编辑配置文件
vim /data/kibana/config/kibana.yml
添加一下内容

server.port: 5601
server.host: "0.0.0.0"
elasticsearch.url: "http://127.0.0.1:9200"
```

切换到bin目录下，启动即可。

```
#不能关闭终端
./kibana  

#可关闭终端
nohup ./kibana &
```

放开防火墙，可以在本地浏览器通过IP:5601的方式访问kibana。

## 参考

[CentOS单机安装Elasticsearch6.3.0](https://blog.csdn.net/qq982782662/article/details/80746159 )
