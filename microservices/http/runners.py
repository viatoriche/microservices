def gevent_run(app, port, log, error_log, **kwargs):
    from gevent.wsgi import WSGIServer
    from gevent import monkey

    monkey.patch_all()
    http_server = WSGIServer(('', port), app, log=log, error_log=error_log, **kwargs)
    http_server.serve_forever()


def base_run(app, port=8080, **kwargs):
    import logging
    import os
    logging.basicConfig(
        level=getattr(logging, os.environ.get('LOG_LEVEL', 'DEBUG')),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    app.run(port=port, **kwargs)