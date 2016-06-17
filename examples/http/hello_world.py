from microservices.http.service import Microservice
from microservices.http.resources import ResourceMarker
import datetime

app = Microservice(__name__)

@app.route(
    '/',
    resource=ResourceMarker(
        update={
            'resource_created': datetime.datetime.now().isoformat()
        },
    ),
)
def hello_world():
    return 'Hello world'

if __name__ == '__main__':
    app.run(debug=True)