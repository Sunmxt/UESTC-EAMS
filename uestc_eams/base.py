'''

    Basic elements

'''


import requests
import re

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
    Wrapped HTTP request method for dealing with cookies in redirect responses.
'''

def WrappedGet(_url, _my_session = None, **kwargs):
    '''
        Wrapper for requests.get()
    '''

    if(_my_session):
        ss = _my_session
    else:
        ss = requests.Session()

    target_url = _url

    allow_redirects = kwargs.get('allow_redirects')
    if(allow_redirects != None):
        kwargs.pop('allow_redirects')

    cookies = kwargs.get('cookies')
    if(cookies):
        ss.cookies.update(cookies)

    while True:
        rep = ss.get(target_url, allow_redirects = False, **kwargs)
        if(rep.is_redirect):
            if(allow_redirects == False):
                return rep
            target_url = rep.headers['Location']
            continue
        break

    rep.cookies.update(ss.cookies)

    return rep

def WrappedPost(_url, _my_session = None, **kwargs):
    '''
        Wrapper for requests.post()
    '''

    if(_my_session):
        ss = _my_session
    else:
        ss = requests.Session()

    target_url = _url
    allow_redirects = kwargs.get('allow_redirects')
    if(allow_redirects != None):
        kwargs.pop('allow_redirects')

    cookies = kwargs.get('cookies')
    if(cookies):
        ss.cookies.update(cookies)

    rep = ss.post(target_url, allow_redirects = False, **kwargs)
    if(allow_redirects == False):
        return rep

    if('data' in kwargs.keys()):
        kwargs.pop('data')

    while rep.is_redirect:
        target_url = rep.headers['Location']
        rep = ss.get(target_url, allow_redirects = False, **kwargs)

    return rep


    
re_host = re.compile(r'(?:.*?\://)(.+?(?=/)|.+)')



