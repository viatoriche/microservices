from microservices.http.service import Microservice
from microservices.http.resources import ResourceMarker, ResourceSchema, BrowserResourceSchema
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
    return {'hello': 'Hello world'}


if __name__ == '__main__':
    app.run(debug=True)
