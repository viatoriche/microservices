def run(app, port, log, error_log):
    from gevent.wsgi import WSGIServer
    from gevent import monkey

    monkey.patch_all()
    http_server = WSGIServer(('', port), app, log=log, error_log=error_log)
    http_server.serve_forever()