import signal
import gevent
from microservices.utils import set_logging

set_logging()

from microservices.queues.service import Microservice

app = Microservice()


@app.queue('basic_queue', prefetch_count=1)
def hello_world(payload, context):
    print(payload)


def stop(*args, **kwargs):
    app.stop()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, stop)
    app.run(debug=True)
