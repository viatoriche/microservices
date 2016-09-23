from microservices.http.service import Microservice

from microservices.http.resources import ResourceMarker, ResourceSchema, BrowserResourceSchema
from flask import request, url_for
import datetime

app = Microservice(__name__)

app.config['SCHEMA'] = ResourceSchema(
    response='result',
    response_update=False,
    status_code='status',
    browser=BrowserResourceSchema(
        status=None,
    )
)


@app.route(
    '/',
    resource=ResourceMarker(
        update={
            'resource_created': datetime.datetime.now().isoformat()
        },
    ),
)
def hello_world():
    return {'hello': 'Hello, world'}

@app.route(
    '/<string:one>/<string:two>/<string:three>/',
    methods=['GET', 'POST'],
    resource=ResourceMarker(
        url_params={'one': 'one', 'two': 'two', 'three': 'three'},
    )
)
def one_two_three(one, two, three):
    response = {'one': one, 'two': two, 'three': three}
    if request.method == 'POST':
        response['data'] = request.data
    return response

if __name__ == '__main__':
    app.run(debug=True)
