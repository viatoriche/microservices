def base_run(app, port=8080, **kwargs):
    app.run(port=port, **kwargs)


def gevent_run(app, port=5000, log=None, error_log=None, address='', **kwargs):
    if log is None:
        log = app.logger
    if error_log is None:
        error_log = app.logger
    try:
        from gevent.wsgi import WSGIServer
        from gevent import monkey

        monkey.patch_all()
        http_server = WSGIServer((address, port), app, log=log, error_log=error_log, **kwargs)
        http_server.serve_forever()
    except ImportError:
        error_log.warning('gevent not installed, running in base mode')
        base_run(app, port, **kwargs)


def tornado_run(app, port=5000, address="", use_gevent=False, start=True, Container=None, Server=None):
    if Container is None:
        from tornado.wsgi import WSGIContainer
        Container = WSGIContainer

    if Server is None:
        from tornado.httpserver import HTTPServer
        Server = HTTPServer

    CustomWSGIContainer = Container

    if use_gevent:
        import gevent
        from gevent import monkey
        monkey.patch_all()

        class GeventWSGIContainer(Container):
            def __call__(self, *args, **kwargs):
                def async_task():
                    super(GeventWSGIContainer, self).__call__(*args, **kwargs)

                gevent.spawn(async_task)

        CustomWSGIContainer = GeventWSGIContainer

    http_server = Server(CustomWSGIContainer(app))
    http_server.listen(port, address)
    if start:
        from tornado.ioloop import IOLoop
        IOLoop.instance().start()
