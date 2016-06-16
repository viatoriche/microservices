from addict import Dict
import warnings
warnings.simplefilter('default')


class Resource(dict):
    def __init__(self, **kwargs):
        super(Resource, self).__init__(**kwargs)
