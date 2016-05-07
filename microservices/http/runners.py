from microservices.utils import get_logger, set_logging


def base_run(app, port=8080, **kwargs):
    set_logging()
    app.run(port=port, **kwargs)


def gevent_run(app, port, log, error_log, **kwargs):
    try:
        from gevent.wsgi import WSGIServer
        from gevent import monkey
    except ImportError:
        set_logging()
        get_logger().warning('gevent not installed, running in base mode')
        base_run(app, port, **kwargs)

    monkey.patch_all()
    http_server = WSGIServer(('', port), app, log=log, error_log=error_log, **kwargs)
    http_server.serve_forever()
