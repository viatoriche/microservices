def base_run(app, port=8080, **kwargs):
    app.run(port=port, **kwargs)


def gevent_run(app, port, log, error_log, **kwargs):
    try:
        from gevent.wsgi import WSGIServer
        from gevent import monkey

        monkey.patch_all()
        http_server = WSGIServer(('', port), app, log=log, error_log=error_log, **kwargs)
        http_server.serve_forever()
    except ImportError:
        error_log.warning('gevent not installed, running in base mode')
        base_run(app, port, **kwargs)
