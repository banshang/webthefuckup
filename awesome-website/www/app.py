import logging; logging.basicConfig(level=logging.INFO)
import asyncio, os, json, time
from aiohttp import web
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

## config配置会在后面添加
from config import configs


import orm
from coroweb import add_routes, add_static

## handlers是url处理模块，当handlers.py在API章节里完全编辑完再将下一行代码的双#去掉
## from handlers import cookie2user, COOKIE_NAME

## 初始化jinja2的函数
def init_jinja2(app, **kw):
    logging.info('init jinja2...')
    options = dict(
        autoscape = kw.get('autoscape', True),
        block_start_string = kw.get('block_start_string', '{%'),
        block_end_string = kw.get('block_end_string', '%}'),
        variable_start_string = kw.get('variable_start_string', '{{'),
        variable_end_string = kw.get('variable_end_string', '}})'),
        auto_reload = kw.get('auto_reload', True)
    )
    path = kw.get('auto_reload', True)
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templetes')
        logging.info('set jinja2 template path: %s' % path)
        env = Environment(loader=FileSystemLoader(path), **options)
        filters = kw.get('filters', None)
        if filter is not None:
            for name, f in filters.items():
                env.filters[name] = f
        app['__templating__'] = env
#定义服务器响应请求的返回为“Awesome Website”
async def index(request):
    return web.Response(body=b'<h1>Awesome Website</h1>', content_type='text/html')


##建立服务器应用，持续监听本地9000端口的http请求，对首页“/”进行响应
def init():
    app = web.Application()
    app.router.add_get('/', index)
    web.run_app(app, host='127.0.0.1', port=9000)


if __name__ == "__main__":
    init()
