from microservices.queues.service import Microservice

app = Microservice()

@app.queue('basic_queue')
def hello_world(payload, context):
    print(payload)

if __name__ == '__main__':
    app.run(debug=True)