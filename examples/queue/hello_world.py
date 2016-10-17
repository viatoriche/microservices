from microservices.queues.service import Microservice
import signal

app = Microservice()

@app.queue('basic_queue')
def hello_world(payload, context):
    print(payload)

def stop(*args, **kwargs):
    app.stop()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, stop)
    app.run(debug=True)