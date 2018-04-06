'''

    Utils for testing

'''

import uestc_eams
from functools import wraps

class HookedMethod:
    '''
    
        Redirect calls to another functions
    
        HookedMethod(_proc, _proc_arg)
    
        Params:
            _proc       Target
            _proc_arg   Argument passed to target
            
    '''
    def __init__(self, _proc, _proc_arg):
        self.__proc = _proc
        self.__proc_arg = _proc_arg

    def __call__(self, *args, **kwarg):
        return self.__proc(self.__proc_arg, *args, **kwarg)


def MakeResponse(_case):
    text = _case.get('text', '')
    rep = type('Response-faked', (uestc_eams.session.requests.Response,), {'text' : text})()
    headers = _case.get('headers', {})
    for key, val in zip(headers.keys(), headers.values()):
        rep.headers[key] = val
    rep.status_code = _case.get('response_code', 0)
    return rep


'''
    Decorator
'''

def CheckType(**_type_dict):
    """
        Decorator CheckType().

        Check whether keyword arguments are of specified types.

        :Example:
            @CheckType(_arg1 = str, _arg2 = (str, int))
            def function1(_arg1, _arg2):
                ... ...
    """
    def decorate(_function):
        @wraps(_function)
        def checked_function(*args, **kwargs):
            # For all arguments.
            checked_keys = _type_dict.keys()
            for key, value in zip(kwargs.keys(), kwargs.values()):
                if key in checked_keys:
                    accepted_types = _type_dict[key]
                    if isinstance(accepted_types, type):
                        if type(value) is accepted_types:
                            continue
                    elif type(value) in _type_dict[key]:
                            continue
                    raise TypeError('Invailed type of %s' % key)
            return _function(*args, **kwargs)
        return checked_function
    return decorate

