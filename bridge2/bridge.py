import gevent

def go():
    try:
        for domain in config.domains:
            domain.start()
        for asset in config.assets:
            asset.load_cache()
        gevent.getcurrent().join()
    except KeyboardInterrupt:
        pass
    gevent.shutdown()
    return 0
