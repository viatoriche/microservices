from microservices.queues.client import Client

client = Client()

q = client.queue('basic_queue')

for _ in range(20):
    q.publish({"message": "Hello, world!"})
