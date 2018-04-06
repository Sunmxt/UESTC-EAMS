'''
    Mock server
'''

from inspect import isfunction
from functools import wraps
from .utils import CheckType 

import re

class MockServerMeta(type):
    def __new__(_class, _name, _bases, _attrs):
        route_get = {}
        route_post = {}

        # Find all routes and append to route table.
        for member, val in zip(_attrs.keys(), _attrs.values()):
            if isfunction(val) and hasattr(val, 'mock_svr_route'):
               for item in val.mock_svr_route:
                    if 'GET' in item[1]:
                        route_get[item[0]] = val
                    elif 'POST' in item[1]:
                        route_post[item[0]] = val

        _attrs['server_route_get'] = route_get
        _attrs['server_route_post'] = route_post
        return super().__new__(_class, _name, _bases, _attrs)


class MockServer(metaclass = MockServerMeta):
    """

        Base class of mock servers.

    """

    def __init__(self):
        pass

    def __new__(_class, *arg, **kwargs):
        instance = object.__new__(_class, *arg, **kwargs)
        
        # Map all routed functions to bound methods
        for map_name in ('server_route_get', 'server_route_post'):
            this_map = getattr(instance, map_name)
            for patten, fn in zip(this_map.keys(), this_map.values()):
                routed = getattr(instance, fn.__name__, None)
                # Cannot be a missing or uncallable object
                # if routed == None or not callable(routed):
                if routed == None:
                    del this_map[patten]
                else:
                    this_map[patten] = routed
       
        return instance

    @staticmethod
    @CheckType(_patten = str, _method = (list, tuple))
    def Route(_patten, _methods):
        """
            :decorator:
            :static:

            Route requests to target function.

            :params:
                _patten         Regular expression to match URL
                _methods        Route requests of the specified in _methods only.
                                Now support GET and POST method.
                                

            :example:
                @MockServer.Route('http://www.google.com', methods = ['GET'])
                def __get_google(_url, **kwargs):
                    ... ...
        """
        def routed_function(_function):
            if not isfunction(_function):
                raise TypeError('Requests can be routed to function only.')

            # Record route.
            # All routes will be collected to a route table by MockServerMetaClass
            if not hasattr(_function, 'mock_svr_route'):
                _function.mock_svr_route = []

            # Check whether methods are supported.
            supported_methods = ('GET', 'POST')
            for method in _methods:
                if not method in supported_methods:
                    raise ValueError('Unsupported method : %s' % method)

            # Append to route table
            _function.mock_svr_route.append((_patten, _methods, _function))
            return _function
        return routed_function

    def __get_route_target(self, _map, _url):
        for patten in _map.keys():
            if re.match(patten, _url):
                return _map[patten]

            
    def GetRouteGETTarget(self, _url):
        """
            Get target function routed by _url
        """
        return self.__get_route_target(self.server_route_get, _url)

    def GetRoutePOSTTarget(self, _url):
        """
            Get target function routed by _url
        """
        return self.__get_route_target(self.server_route_post, _url)

    
    def DoPatch(self):
        """
            :abstracted:

            Actually mock something. Define behaviour yourself.

        """
        pass

    def DoUnpatch(self):
        """
            :abstracted:

            Restore the mocked. Define behaviour yourself.
        """
        pass

    def Patch(self, _callable):
        """

            Mock target before actually executing the decorated function.
            And recover after the function returns.
            
        """
        @wraps(_callable)
        def mocked_function(*args, **kwargs):
            self.DoPatch()
            ret = _callable(*args, **kwargs)
            self.DoUnpatch()
            return ret
        return mocked_function

