#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: xtz
"""
提供jwt 为底层的 token 加密/解密服务
"""

import datetime
import functools
import itertools

import jwt


DEFAULT_EXP = 3600
DEFAULT_NBF = None


class Tokener(object):
    """ 设计用户替代session，无需在后端记录session信息
    token 使用加密算法保证不会被篡改，可以在后端通过token 获得session
    """

    _plugins = []
    _rplugins = []
    _secret = 'CBUGc1r3K&@!W2FivC$NugFZ$Hu9HML9vJd3!WMQ^v35B@X$5Keyaej1rttF2mT6'
    _inner_keys = ('exp', 'nbf', 'aud')

    def register(self, name, plugin):
        """ 注册一个插件
        Args:
            name(str): 插件的名称，暂时没有用上
            plugin(TokenPlugin): 插件类
        """
        self._plugins.append(plugin)
        self._rplugins = list(reversed(self._plugins))

    def _reduce_plugin(self, method, data, reverse=False):
        """ 内部调用, 遍历注册的插件，根据 method 改变数据的结构
        """
        plugins = self._rplugins if reverse else self._plugins
        return functools.reduce(lambda a, b: getattr(b, method)(a), plugins,
                                data)

    def dumps(self, data, *args, **kwargs):
        """
        创建一个token，经过插件修改数据
        """
        data = self._reduce_plugin('dumps', data)
        return self.raw_dumps(data, *args, **kwargs)

    def loads(self, token):
        """
        解密一个token，经过插件修改数据
        """
        raw_result = self.raw_loads(token)
        result = self._reduce_plugin('loads', raw_result, reverse=True)
        return result

    def loads_with_meta(self, token):
        """
        解密一个token，经过插件修改数据，并带上meta信息
        """
        result = self.raw_loads_with_meta(token)
        result['data'] = self._reduce_plugin(
            'loads', result['data'], reverse=True)
        return result

    def raw_dumps(self,
                  data,
                  exp=DEFAULT_EXP,
                  nbf=DEFAULT_NBF):
        """
        创建一个token
        Args:
            data(dict): 需要保存的数据
            exp(int): 多久后过期，按秒计算
            nbf(datetime): 从什么时间生效，在这个时间之前都报错
            aud(str): 限定token的接受者，我们这里定义了只有某个系统才能解密这个token
        """
        if nbf is None:
            nbf = datetime.datetime.utcnow()
        if exp and isinstance(exp, int):
            exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=exp)

        payload = dict(data, exp=exp, nbf=nbf)
        token = jwt.encode(payload, self._secret, algorithm='HS256')
        return token

    def raw_loads(self, token):
        """
        解密一个token

        Args:
            token(str): token

        Return:
            返回保存在 token 中的信息
            会自动识别:

                * exp 超时
                * nbf 错误
                * aud 错误
                * 其他错误
        """
        try:
            msg = jwt.decode(
                token,
                self._secret,
                leeway=1800,  # 允许过期半小时
                algorithms=['HS256'])
            return {k: v for k, v in msg.items() if k not in self._inner_keys}
        except jwt.ExpiredSignatureError:  # exp 超时
            return
        except jwt.ImmatureSignatureError:  # nbf 错误
            return
        except jwt.InvalidAudienceError:  # aud 错误
            return
        except BaseException:  # FIXME 其他错误，可能需要记录日志
            return

    def raw_loads_with_meta(self, token):
        code = 0
        data = {}
        meta = {}

        try:
            msg = jwt.decode(
                token,
                self._secret,
                leeway=1800,  # 允许过期半小时
                algorithms=['HS256'])

            for k, v in msg.items():
                if k in self._inner_keys:
                    meta[k] = v
                else:
                    data[k] = v

        except jwt.ExpiredSignatureError:  # exp 超时
            code = 2
        except jwt.ImmatureSignatureError:  # nbf 错误
            code = 3
        except jwt.InvalidAudienceError:  # aud 错误
            code = 4
        except BaseException:  # FIXME 其他错误，可能需要记录日志
            code = 1

        return {
            'status': True if code == 0 else False,
            'code': code,
            'data': data,
            'meta': meta
        }


class TokenPlugin(object):
    """
        插件可以在 dumps 之前 和 loads 之后改变数据结构

        插件必须实现 dumps, loads 两个方法
    """

    def dumps(self, data):
        raise NotImplementedError

    def loads(self, token):
        raise NotImplementedError


class TokenReduceSize(TokenPlugin):
    """
    通过一定的规则保存信息，减少 token 的大小

        * 保存的信息是字典，字典占用比较大，改成使用默认循序的字符组合，使用'|'符号分割
        * 默认的 rti, id, name, alias, user_node_id, system_id 几个字段，默认在字符组合最前面，无标识
        * 额外的其他信息，在后面添加，使用标识

    一个例子 '12345|67890|admin|管理员|age:18|address:地球某处'

        * 12345: 代表 rti
        * 67890: 代表用户id
        * admin: 代表用户名
        * 管理员: 代表用户别名
        * age: 代表额外字段 age，内容是 '18'
        * address: 代表额外字段 address，内容是 '地球某处'
    """

    _default_fields = sorted(
        ['rti', '_id', 'name', 'alias', 'user_node_id', 'system_id'])

    def dumps(self, data):
        pre = [data.get(k, '') for k in self._default_fields]

        extra_list = [
            '{}:{}'.format(k, v) for k, v in data.items()
            if k not in self._default_fields
        ]

        return {'reduce': '|'.join(itertools.chain(pre, extra_list))}

    def loads(self, token):
        if not token:
            return {}

        fields_len = len(self._default_fields)
        token_list = token['reduce'].split('|')
        value_set = token_list[:fields_len]
        extra_set = token_list[fields_len:]
        return dict(
            itertools.chain((x.split(':', 1) for x in extra_set),
                            itertools.izip(self._default_fields, value_set)))


tokener = Tokener()
tokener.register('reduce_size', TokenReduceSize())

dumps = tokener.dumps
loads = tokener.loads
loads_with_meta = tokener.loads_with_meta
raw_dumps = tokener.raw_dumps
raw_loads = tokener.raw_loads
