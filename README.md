# 自动发现Mongodb-mongod进程并自动创建监控项

## 项目说明

本项目 zabbix 3.4.15 配置的mongodb shard 集群自动发现监控配置。
本项目配置完成后会自动发现mongod进程,以端口号作为区分自动创建监控项。

## 软件环境

centos7 \ mongodb4.2 \ zabbix 3.4.15


## 下载本项目

```

cd zabbix-mongodb
```

## Mongodb 用户名密码配置

`config.properties` 此文件中需配置mongod 各进程的用户名密码，需要有读权限

```
[MONGODB]
user=root
password=EJLY9pFodlUFuOd1
```

用户名密码设置完成之后请把 文件用户修改为zabbix

```
chown zabbix:zabbix config.properties
chmod 600 config.properties
```

>本监控脚本默认认为`config.properties`中配置的用户 是 在所有的mongod中都存在。

## 通过mongos进程获取集群数据库信息

如果监控的mongodb节点存在mongos进程请修改此 `get-mongo-info.py` 脚本中的 端口。 

## 安装依赖
>默认 zabbix-server、zabbix-web 已经安装

### 安装 zabbix-agent zabbix-sender
```
yum install zabbix-agent
yum install zabbix-sender
```

### 安装python脚本依赖

```

pip install -r requirements.txt
```

## 脚本提权

修改 /etc/sudoers 文件

```
zabbix  ALL=(ALL)       NOPASSWD:/usr/local/bin/mongo-ports.sh
zabbix  ALL=(ALL)       NOPASSWD:/usr/local/bin/mongodb-stats.sh
zabbix  ALL=(ALL)       NOPASSWD:/usr/local/bin/mongodb-info.sh
```

## 复制文件到指定目录

```
cp get*.py /usr/local/bin
cp mongodb*.sh /usr/local/bin
cp userparameter_mongodb.conf /etc/zabbix/zabbix_agentd.d
```
## 重启zabbix-agent

```
systemctl restart zabbix-agent
```