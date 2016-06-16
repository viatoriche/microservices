from addict import Dict
import warnings
warnings.simplefilter('default')


class Resource(dict):
    def __init__(self, **kwargs):
        super(Resource, self).__init__(**kwargs)


class ResourceInfo(dict):
    def __init__(self, resource=None, update=None, **kwargs):
        warnings.warn('ResourceInfo will be remove in future release', DeprecationWarning)
        super(ResourceInfo, self).__init__()
        self.data = Dict()
        if resource is not None:
            self['resource'] = resource
        if kwargs:
            self['methods'] = kwargs
        if update is not None:
            self.update(update)