'''

    Basic elements

'''


import requests
import re
import functools

'''
    Constants
'''

UNKNOWN = 0
CASH = 1
CATCH = 2

ELECT = True
CANCEL = False

'''
    URLs
'''

UserAgent = r'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36'
LoginIndex = r'http://idas.uestc.edu.cn/authserver/login?service=http://portal.uestc.edu.cn/'
AuthHost = "idas.uestc.edu.cn"
PortalIndex = r'http://portal.uestc.edu.cn'
LogoutUrl = r'/authserver/logout?service=/authserver/login'

SubmenuIndex = r'http://eams.uestc.edu.cn/eams/home!submenus.action'
ChildmenuIndex = r'http://eams.uestc.edu.cn/eams/home!childmenus.action?menu.id='
EAMSBaseUrl = r'http://eams.uestc.edu.cn/eams'
EAMSHost = 'eams.uestc.edu.cn'
ElectCourseUrl = r'/stdElectCourse.action'
ElectCourseData = r'/stdElectCourse!data.action'
ElectDefault = r'/stdElectCourse!defaultPage.action'
ElectStudentCount = r'/stdElectCourse!queryStdCount.action'
ElectOperate = r'/stdElectCourse!batchOperator.action'
ElectCashChange = r'/stdVirtualCashElect!changeVirtualCash.action'

'''
    Exceptions
'''
class EAMSSessionException(Exception):
    def __init__(self, *kargs):
        super().__init__(*kargs)

class EAMSLoginException(Exception):
    def __init__(self, *karg):
        super().__init__(*kargs)

class UESTCIncorrentAccount(EAMSLoginException):
    def __init__(self, *kargs):
        super().__init__(*kargs)

class EAMSException(Exception):
    def __init__(self, *kargs):
        super().__init__(*kargs)


'''
    Decorators
'''

def RecordMethodException(_record_function, fallback_value = None, *exceptions):
    def RecordCatch(_target_func):
        @functools.wraps(_target_func)
        def WrappedFun(self, *args, **kwargs):
            try:
                return _target_func(self, *args, **kwargs)
            except Exception as s:
                for exception in exceptions:
                    if isinstance(s, exception):
                        _record_function(self, s)
                        return fallback_value
                return fallback_value
        return WrappedFun
    return RecordCatch
                    
                       
re_host = re.compile(r'(?:.*?\://)(.+?(?=/)|.+)')



