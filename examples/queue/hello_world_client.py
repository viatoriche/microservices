from microservices.queues.client import Client

client = Client()

q = client.queue('basic_queue')

q.publish({"message": "Hello, world!"})
