'''

    Utils for testing

'''

class HookedMethod:
    def __init__(self, _proc, _proc_arg):
        def redirect_to(_hooked_self, *args, **kwargs):
            _proc(_proc_arg, _hooked_self, *args, **kwargs)
        self.__call__ = redirect_to     

