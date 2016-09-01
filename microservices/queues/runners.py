def gevent_run(app, monkey_patch=True, start=True, debug=False, **kwargs):
    """Run your app in gevent.spawn, run simple loop if start == True

    :param app: queues.Microservice instance
    :param monkey_patch: boolean, use gevent.monkey.patch_all() for patching standard modules, default: True
    :param start: boolean, if True, server will be start (simple loop)
    :param kwargs: other params for WSGIServer(**kwargs)
    :return: server
    """
    if monkey_patch:
        from gevent import monkey

        monkey.patch_all()

    import gevent

    gevent.spawn(app.run, debug=debug, **kwargs)

    if start:
        while True:
            gevent.sleep(0.1)
