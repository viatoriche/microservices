def gevent_run(app):
    import gevent

    gevent.spawn(app.run)