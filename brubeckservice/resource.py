"""This is an abstraction for a directory of resources scoped at the application class level.
Since a Brubeck class is generally run in it's own instance, in effect behaving like a singleton, 
it essentially manages resource for a single Brubeck instance. 
An example of a resource could be a Brubeck service (brubeckservice.base.BrubeckServiceInfo)"""
import logging
import time
from dictshield.document import Document
from dictshield.fields import (StringField,
                               DictField,
)

# Used to hold our resources for the life of the application
# This will be a reference to a dict stored in a property of the application 
# class that will be added dynamically
_resources = None

def assure_resource(application):
    """assure that our application has a _resources property"""
    logging.debug("Checking for %s _resources" % application)
    global _resources
    if not hasattr(application, '_resources'):
        setattr(application, '_resources', {})
        logging.debug("Created _resource attr")
        _resources = application._resources
    else:
        logging.debug("application._resources (%s) already initialized" % application._resources)
        _resources = application._resources

def is_resource_registered(key):
    """ Check if a resource is registered.""" 
    logging.debug("Is %s resource registered?" % key)
    if key in _resources:
        logging.debug("Yup")
        return True
    else:
        logging.debug("Nope")
        return False

def register_resource(resource):
    """ Store (register) a resource and call our on_register hook.
    """
    key = resource.key()
    if key not in _resources:
        # add us to the list
        _resources[key] = resource
        resource._on_register()
        logging.debug("register_resource success: %s" % resource.name)
    else:
        logging.debug("register_resource ignored: %s already registered" % 
            resource.name)
    return True

def unregister_resource(key):
    """ Call our on_unregister hook and delete from list.
    """ 
    if key not in _resources:
        logging.debug("unregister_resource ignored: %s not registered" % key)
        return False
    else:
        resource = _resources[key]
        resource._on_unregistered()
        logging.debug("unregister_resource success: %s" % service_addr)

        resource._on_unregister()
        del _resources[key]

        return True

def get_resource(key):
    """ Check if key is a resource that is registered
    and return resource if found, None if not found.
    """ 
    if key in _resources:
        logging.debug("get_resource found resource %s" % key)
        return _resources[key]
    else:
        logging.debug("get_resource didn't find resource %s" % key)
        return None


class Resource(Document):
    """A resource is an application level object to store arbitrary data in.
        A resource may implement the following methods few methods:
        on_registered(application)
        `on_registered` is called once when a `resource` is registered.
        on_unregistered(application)
        `on_unregistered` is called once when a `resource` is unregistered.
        
        set(resource)
        sets a resource for the instance
        get()
        retrun the last `resource` that was `set(resource)`
        
        
        init expects `resource` as a keyword parameter
        """
    # The name of the resource. This is what it is looked up by.
    name = StringField(required=True)
    # a resource_type such as data_connection, queryset, service, anything really
    resource_type = StringField(required=True)
    # a list of categories
    category = DictField(required=True)
    
    def __init__(self, *args, **kwargs):
        self.resource = None # this is where we store the user defined resource
        self.start_timestamp = int(time.time() * 1000)
        self.end_timestamp = self.start_timestamp
        super(Resource, self).__init__(*args, **kwargs)
    
    
    def _on_register(self):
        self.on_unregister()
    
    def _on_unregister(self):
        self.on_unregister()
    
    def set(self, resource):
        self.resource = resource;
    
    def get(self):
        return self.resource;
    
    def key(self):
        """used as the key when a resource is stored"""
        return Resource.create_key(self.name, self.resource_type)
    
    @staticmethod
    def create_key(name, resource_type=None):
        """used as the key when a resource is stored"""
        return ((resource_type if resource_type is not None else '') +
                (name if name is not None else ''))
    
    ###########
    ## over-ride these in your app if you need
    ## to do something durinsg registration/unregistration
    ###########
    def on_register(self):
        pass
    
    def on_unregister(self,):
        pass
