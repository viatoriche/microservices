import signal
from microservices.utils import set_logging
import time

set_logging()

from microservices.queues.service import Microservice

app = Microservice(workers=10)


@app.queue('basic_queue')
def hello_world(payload, context):
    time.sleep(10)
    print('Handled:', payload)


def stop(*args, **kwargs):
    app.stop()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, stop)
    app.run(debug=True)
