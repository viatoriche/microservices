def base_run(app, port=5000, **kwargs):
    """Run app in base run, for debugging and testing

    :param app: wsgi application, ex. Microservice instance
    :param port: int, listen port, default 5000
    :param kwargs: params for app.run
    :return: None
    """
    app.run(port=port, **kwargs)


def gevent_run(app, port=5000, log=None, error_log=None, address='', monkey_patch=True, start=True, **kwargs):
    """Run your app in gevent.wsgi.WSGIServer

    :param app: wsgi application, ex. Microservice instance
    :param port: int, listen port, default 5000
    :param address: str, listen address, default: ""
    :param log: logger instance, default app.logger
    :param error_log: logger instance, default app.logger
    :param monkey_patch: boolean, use gevent.monkey.patch_all() for patching standard modules, default: True
    :param start: boolean, if True, server will be start (server.serve_forever())
    :param kwargs: other params for WSGIServer(**kwargs)
    :return: server
    """
    if log is None:
        log = app.logger
    if error_log is None:
        error_log = app.logger
    if monkey_patch:
        from gevent import monkey

        monkey.patch_all()

    from gevent.wsgi import WSGIServer
    http_server = WSGIServer((address, port), app, log=log, error_log=error_log, **kwargs)
    if start:
        http_server.serve_forever()
    return http_server


def tornado_start():
    """Just start tornado ioloop

    :return: None
    """
    from tornado.ioloop import IOLoop
    IOLoop.instance().start()


def tornado_run(app, port=5000, address="", use_gevent=False, start=True, monkey_patch=None, Container=None,
                Server=None, threadpool=None):
    """Run your app in one tornado event loop process

    :param app: wsgi application, Microservice instance
    :param port: port for listen, int, default: 5000
    :param address: address for listen, str, default: ""
    :param use_gevent: if True, app.wsgi will be run in gevent.spawn
    :param start: if True, will be call utils.tornado_start()
    :param Container: your class, bases on tornado.wsgi.WSGIContainer, default: tornado.wsgi.WSGIContainer
    :param monkey_patch: boolean, use gevent.monkey.patch_all() for patching standard modules, default: use_gevent
    :param Server: your class, bases on tornado.httpserver.HTTPServer, default: tornado.httpserver.HTTPServer
    :return: tornado server
    """
    if Container is None:
        from tornado.wsgi import WSGIContainer
        Container = WSGIContainer

    if Server is None:
        from tornado.httpserver import HTTPServer
        Server = HTTPServer

    if monkey_patch is None:
        monkey_patch = use_gevent

    CustomWSGIContainer = Container

    if use_gevent:
        if monkey_patch:
            from gevent import monkey
            monkey.patch_all()

        import gevent

        class GeventWSGIContainer(Container):
            def __call__(self, *args, **kwargs):
                def async_task():
                    super(GeventWSGIContainer, self).__call__(*args, **kwargs)

                gevent.spawn(async_task)

        CustomWSGIContainer = GeventWSGIContainer

    if threadpool is not None:
        from multiprocessing.pool import ThreadPool

        if not isinstance(threadpool, ThreadPool):
            threadpool = ThreadPool(threadpool)

        class ThreadPoolWSGIContainer(Container):
            def __call__(self, *args, **kwargs):
                def async_task():
                    super(ThreadPoolWSGIContainer, self).__call__(*args, **kwargs)

                threadpool.apply_async(async_task)

        CustomWSGIContainer = ThreadPoolWSGIContainer


    http_server = Server(CustomWSGIContainer(app))
    http_server.listen(port, address)
    if start:
        tornado_start()
    return http_server


def tornado_combiner(configs, use_gevent=False, start=True, monkey_patch=None, Container=None, Server=None, threadpool=None):
    """Combine servers in one tornado event loop process

    :param configs: [
        {
            'app': Microservice Application or another wsgi application, required
            'port': int, default: 5000
            'address': str, default: ""
        },
        { ... }
    ]
    :param use_gevent: if True, app.wsgi will be run in gevent.spawn
    :param start: if True, will be call utils.tornado_start()
    :param Container: your class, bases on tornado.wsgi.WSGIContainer, default: tornado.wsgi.WSGIContainer
    :param Server: your class, bases on tornado.httpserver.HTTPServer, default: tornado.httpserver.HTTPServer
    :param monkey_patch: boolean, use gevent.monkey.patch_all() for patching standard modules, default: use_gevent
    :return: list of tornado servers
    """
    servers = []
    if monkey_patch is None:
        monkey_patch = use_gevent

    if use_gevent:
        if monkey_patch:
            from gevent import monkey
            monkey.patch_all()

    if threadpool is not None:
        from multiprocessing.pool import ThreadPool

        if not isinstance(threadpool, ThreadPool):
            threadpool = ThreadPool(threadpool)

    for config in configs:
        app = config['app']
        port = config.get('port', 5000)
        address = config.get('address', '')
        server = tornado_run(app, use_gevent=use_gevent, port=port, monkey_patch=False, address=address, start=False,
                             Container=Container,
                             Server=Server, threadpool=threadpool)
        servers.append(server)
    if start:
        tornado_start()
    return servers
