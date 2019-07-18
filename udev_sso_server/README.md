# udev_sso_server

cas 单点登录服务端的实现

## python

使用 python3.6 或者以上版本，理论上支持 python2，不过没有测试。

## 安装

首先安装 pipenv：

```bash
pip install pipenv
```

使用 pipenv 安装依赖：

```bash
pipenv install
```

## 升级数据库

使用 sqlite3 作为本地数据库，在安装完成后，需要创建/升级数据库：

```bash
python manage.py migrate
```

## 启动

简单启动方式：

```bash
python runserver
```

指定绑定ip和端口：

```bash
python runserver 0.0.0.0:4002
```


