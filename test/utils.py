'''

    Utils for testing

'''

import uestc_eams

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

