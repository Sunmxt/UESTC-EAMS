'''

    Utils for testing

'''

class HookedMethod:
    def __init__(self, _proc, _proc_arg):
        self.__proc = _proc
        self.__proc_arg = _proc_arg

    def __call__(self, *args, **kwarg):
        return self.__proc(self.__proc_arg, *args, **kwarg)
