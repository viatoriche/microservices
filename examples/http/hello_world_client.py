from microservices.http.client import Client
from microservices.http.client import ResponseError
from six import print_

hello_world = Client('http://localhost:5000')

try:
    response = hello_world.get(key='bad_key')
except ResponseError as error:
    print_('Data:', error.response.json())
    print_('Status code:', error.status_code)
    print_('Description:', error.description)
    print_('Content:', error.content)

response = hello_world.get(key='result')
print_(response)

one_two_three = hello_world.resource('one', 'two', 'three')
response = one_two_three.post(data={'post': 'test'})
print_(response)
result = one_two_three.post(data={'post': 'test'}, key='result')
print_(result)