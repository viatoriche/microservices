from microservices.http.client import Client
from microservices.utils import set_logging, get_logger

set_logging(level='INFO')
logger = get_logger('microservices client')

client = Client(
    'http://localhost:5000/',
)

logger.info(client.get(key='response'))
logger.info(client.post(data={'test': 'tested'}))

second_resource = client.resource('second')

logger.info(second_resource.get(key='response'))
logger.info(second_resource.post(data={'test': 'tested'}))

logger.info(second_resource.get('test', key='response'))
logger.info(second_resource.post('test'))

one_two_resource = second_resource.resource('one', '2')
logger.info(one_two_resource.get(key='response'))
logger.info(one_two_resource.post(data={'test': 'tested'}))
