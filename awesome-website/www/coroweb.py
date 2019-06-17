import asyncio, os, inspect, logging, functools

from urllib import parse

from aiohttp import web

## apis是处理分页的模块，代码在后面，要把apis.py放在www下
## APIError 是指API调用时发生路基错误
from apis import APIError


## 装饰函数
def get(path):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'GET'
        wrapper.__route__ = path
        return wrapper
    return decorator

def post(path):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, *kw):
            return func(*args, **kw)
        wrapper.__method__ = 'POST'
        wrapper.__route__ = path
        return wrapper
    return decorator

def get_required_kw_args(fn):
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY\
        and param.default == inspect.Parameter.empty:
            args.append(name)
    return tuple(args)

def get_named_kw_args(fn):
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
    return tuple(args)

def has_named_kw_args(fn):
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            return True

def has_var_kw_arg(fn):
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True

def has_request_arg(fn):
    sig = inspect.signature(fn)
    param = sig.parameters
    found = False
    for name, param in params.items():
        if name == 'request':
            found = True
            continue
        if found and (param.kind != inspect.Parameter.VAR_POSITIONAL
                      and param.kind != inspect.Parameter.KEYWORD_ONLY
                      and param.kind != inspect.Parameter.VAR_KEYWORD):
            raise ValueError('request parameter must be the last named parameter in function: %s%s' % (fn.__name__, str(sig)))
            return found

## 定义RequestHandler从URL函数中分析出其需要接受的参数
class RequestHandler(object):

    def __init__(self, app, fn):
        self._app = app
        self._func = fn
        self._has_request_arg = has_request_arg(fn)
        self._has_var_kw_arg = has_var_kw_arg(fn)
        self._has_named_kw_args = has_named_kw_args(fn)
        self._named_kw_args = get_named_kw_args(fn)
        self._required_kw_args = get_required_kw_args(fn)

    async def __call_(self, request):
        kw = None
        if self._has_var_kw_arg or self._has_named_kw_args
            or self._required_kw_args:
            if request.method == 'POST':
                if not request.content_type:
                    return web.HTTPBadRequest(text='Missing Content_Type.')
                ct = request.content_type.lower()
                if ct.startswith('application/json'):
                    params = await request.json()
                    if not isinstance(params, dict):
                        return web.HTTPBadRequest(text='JSON body must\
                                                  be object.')
                    kw = params
                elif ct.startswith('application/x-www-form-urlencoded')\
                     or ct.startswith('multipart/form-data'):
                        params = await request.post()
                        kw = dict(**params)
                else:
                    return web.HTTPBadRequest(text='Unsupported Content-Type:\
                                            %s' % request.content_type)
            if request.method = 'GET':
                qs = request.query_string
                if qs:
                    kw = dict()
                    for k, v in parse.parse_qs(qs, True).items():
                        kw[k] = v[0]
            if kw is None:
                kw = dict(**request.match_info)
            else:
                if not self._has_var_kw_arg and self._named_kw_args:
                    # remove all unnamed kw:
                    copy = dict()
                    for name in self._named_kw_args:
                        if name in kw:
                            copy[name] = kw[name]
                    kw = copy
                # check named arg:
                for k, v in request.match_info.items():
                    if k in kwL
                    logging.warning('Duplicate arg name in named arg and\
                                    kw args: %s' % k)
                    kw[k] = v
            if self._has_request_arg:



