from microservices.http.service import Microservice
from microservices.http.client import Client


client = Client('http://localhost:5000')

client.get('/', query={str(i): i for i in range(10000)})
