'''
    Session module for accessing UESTC EMAS System
'''


import requests
import re

from .base import *
from .elect_course import EAMSElectCourseSession
    
'''
    Login form
'''
class uestc_portal_login_form:
    def __init__(self):
        self.lt = None
        self.dllt = None
        self.execution = None
        self.eventId = None
        self.rmShown = None
        self.username = None
        self.password = None

    def CheckInternalIntegrity(self):
        return self.lt != None and self.dllt != None and self.execution != None and self.rmShown != None

    def CheckIntegrity(self):
        return self.CheckInternalIntegrity() and self.username != None and self.password != None

    def GeneratePostDataDict(self):
        return {
            'username': self.username
            ,'password': self.password
            ,'lt': self.lt
            ,'dllt': self.dllt
            ,'_eventId': self.eventId
            ,'execution': self.execution
            ,'rmShown': self.rmShown
        }

'''
    Sessions
'''

class EAMSSession:
    '''

        UESTC's portal system login session.

        it provides basic authenticate methods.

        Example:
            1. Login
                ss = EAMSSession()
                ss.Login(_username = '2016xxxxxxxxx', _password = 'xxxxxx')

    '''

    @property
    def Logined(self):
        return self.__logined

    @property
    def ElectCourse(self):
        if(not self.__elect_course_loaded):
            self.__elect_course = self.__create_elect_course_session()
            self.__elect_course_loaded = True
        return self.__elect_course


    def __get_login_form_internal_value(self, _response, _name):
        patten = r'\<input\s*type="hidden"\s*name="' + _name + '"\s*value=\"(\S*)\"'
        m = re.search(patten, _response.text)
        if(not m):
            return None
        gp = m.groups()
        if(not gp):
            return None

        return gp[0]

    def __get_login_post_url(self, _response):
        patten = r'\<form.*id=\"casLoginForm\".*action=\"(.*?)\"'
        m = re.search(patten, _response.text)
        if( not m ):
            return None

        url = m.groups()[0]
        if(url[0] != '/'):
            return 'http://' + AuthHost + '/' + url
        
        return 'http://' + AuthHost + url
        
    def __update_login_form(self, _response):
        self.__login_form.lt = self.__get_login_form_internal_value(_response, 'lt')
        self.__login_form.dllt = self.__get_login_form_internal_value(_response, 'dllt')
        self.__login_form.execution = self.__get_login_form_internal_value(_response, 'execution')
        self.__login_form.eventId = self.__get_login_form_internal_value(_response, '_eventId');
        self.__login_form.rmShown = self.__get_login_form_internal_value(_response, 'rmShown');
        self.__login_post_url = self.__get_login_post_url(_response)
        
        if(not self.__login_form.CheckInternalIntegrity()):
            raise EAMSSessionException('Information lost while paring login form.')
            return None
        if(not self.__login_post_url):
            raise EAMSSessionException('Login-post url not found')
            return None

        return self.__login_form

    def __update_cookies(self, _cookiejar):
        self.__cookiejar.update(_cookiejar)
        if (not self.__cookiejar.get('JSESSIONID_ids2')) and (not self.__cookiejar.get('JSESSIONID_ids1')):
            raise EAMSSessionException('No JSESSIONID found.')
    def UpdateCookies(self, _cookiejar):
        return self.__update_cookies(_cookiejar)

    def __init__(self):
        self.Reset()

    def __getstate__(self):
        contents = self.__dict__.copy()

        # elect course interface should not be pickled.
        class_name = type(self).__name__
        del contents[ '_' + class_name + '__elect_course_loaded']
        del contents[ '_' + class_name + '__elect_course']
        return contents

    def __setstate__(self, _contents):
        self.__dict__.update(_contents)
        self.__elect_course_loaded = False
        self.__elect_course = None


    def __check_session_expired(self):
        self.__cookiejar.clear_expired_cookies()
        if (not self.__cookiejar.get('JSESSIONID_ids2')) and (not self.__cookiejar.get('JSESSIONID_ids1')):     
            raise EAMSSessionException('The session is expired. Please login again.')
    
    def __trace_login_failure(self, _session, _rep):
        pass

    def __create_elect_course_session(self):
        '''

            Create a elect-course session and load platform information.

            @Return:
                EAMSElectCourseSession object.

        '''
        
        if(not self.__logined and not self.Authenticate()):
            raise EAMSSessionException('Not logined.')
            return None
           
        ecss = EAMSElectCourseSession([self.__cookiejar], self)

        return ecss

    def Reset(self):
        '''
            Reset the session object back to initial state.
        '''

        self.__cookiejar = requests.cookies.RequestsCookieJar()
        self.__logined = False
        self.__login_form = uestc_portal_login_form()
        self.Submenus = []

        self.__elect_course = None
        self.__elect_course_loaded = False


    def IsAuthResponse(self, _response):
        '''

            Check whether the specified is a authcentication response 

        '''
        
        host = re_host.search(_response.url).groups()[0]
        return host == 'idas.uestc.edu.cn'

    def Authenticate(self):
        '''

            Authenticate with current account.

            @Return:
                False       Failed
                True        Succeed

            @Exception:
                EAMSLoginException
        '''

        header = {
            'User-Agent' : UserAgent
        }

        ss = requests.session()
        rep = WrappedGet(PortalIndex, _my_session = ss\
                        , headers = header)
        if(rep.status_code != 200):
            ss.close()
            self.__logined = False
            raise EAMSLoginException('Server error [Status code : %d]' % rep.status_code)
            return False

        if(not self.IsAuthResponse(rep)): # logined?
            ss.close()
            self.__logined = True
            return True

        self.__logined = False

        if(not self.__update_login_form(rep) \
            or not self.__login_form.CheckIntegrity()):
            ss.close()
            return False

        post_data = self.__login_form.GeneratePostDataDict()
        rep = WrappedPost(self.__login_post_url, data = post_data\
                            , _my_session = ss, headers = header)
        self.__update_cookies(ss.cookies)

        if(self.IsAuthResponse(rep)): # failed
            self.__trace_login_failure(ss, rep)
            return False

        ss.close()

        self.__logined = True
        return True


    def Login(self, _username, _password):
        '''
            Log in with specified account

            @Params:
                _username       User Name.
                _password       Password

            @Return:
                True        succeed
                False       failed

            @Exception:
                
        '''
        if not isinstance(_username, str) or not isinstance(_password, str):
            raise ValueError('_username and _password should be str.')

        if(self.__login_form.username == _username \
            or self.__login_form.password == _password):
            return True

        self.Logout()

        self.__login_form.username = _username
        self.__login_form.password = _password

        return self.Authenticate()

    def Logout(self):
        '''
            Log out

            @Return
                True        succeed
                False       failed
        '''
        if(not self.__logined):
            return True

        header = {
            'User-Agent' : UserAgent
            , 'Referer' : 'http://' + AuthHost + '/authserver/index.do'
        }

        self.TryRequestPost('http://' + AuthHost + LogoutUrl\
                                    , headers = header)

        self.__cookiejar.clear()
        self.__logined = False
        return True

        

    def Refresh(self):
        '''
            Refresh all interfaces.
        '''
        pass

    def FetchSubmenu(self):
        '''

            Fetch submenus. Save to member 'Submenus'.

            @Return
                [(url, method_name)]

        '''
        header = {
            'User-Agent' : UserAgent
            , 'Referer' : 'http://eams.uestc.edu.cn/eams/home.action'
            , 'Accept' : 'text/html, */*; q=0.01'
            , 'X-Requested-With' : 'XMLHttpRequest'
        }

        '''
        reauth = False
        while True:
            rep = requests.get(SubmenuIndex, headers = header \
                            , cookies = self.__cookiejar)
            if(self.IsAuthResponse(rep)):
                if(reauth):
                    return False
                self.Authenticate()

            break
        '''

        rep = self.TryRequestGet(SubmenuIndex, headers = header)
        if(not rep):
            return []

        self.Submenus = re.findall(r'\<a\s+href=\"(.*?)\".*myTitle=\"(.*?)\"'\
                                , rep.text)
        #Build map dict
        self.SubmenuByName = {name: url for url, name in self.Submenus}
        self.__update_cookies(rep.cookies)

        return self.Submenus 

    def SubmenuURLByName(self, _name, _default = None):
        return self.SubmenuByName.get(_name, _default)

    def TryRequestOp(self, _url, _wrapped_op, **kwargs):
        '''
            Wrapper for request.post
        '''

        target_url = _url
        cookies = kwargs.get('cookies')
        if(cookies):
            self.__cookiejar.update(cookies)
        kwargs['cookies'] = self.__cookiejar
        allow_redirects = kwargs.get('allow_redirects')

        if(allow_redirects != None):
            kwargs.pop('allow_redirects')

        target_host = re_host.search(target_url).groups()[0]

        reauth = False
        while True:
            rep = _wrapped_op(target_url, allow_redirects = False ,**kwargs)
            if(_wrapped_op == WrappedPost):
                _wrapped_op = WrappedGet

            host = re_host.search(rep.url).groups()[0]
            if(host == 'idas.uestc.edu.cn' and host != target_host):
                if(reauth):
                    raise EAMSLoginException('Authentication failure.')
                    return None
                
                if(rep.is_redirect):
                    if(target_host in self.__cookiejar.list_domains()):
                        self.__cookiejar.clear(domain = target_host)
                    target_url = rep.headers['Location']
                    continue

                reauth = True
            elif(rep.is_redirect and allow_redirects != False):
                    self.__cookiejar.update(rep.cookies)
                    target_url = rep.headers['Location']
                    continue
                
            if(rep.status_code != 200):
               raise EAMSSessionException('Unknown error [Status code: %d]' % rep.status_code)
               return None


            m = re.findall(r'\<a.*?\s+href=\"(.*?)\".*?\>\s*?点击此处\s*?\</a\>继续', rep.text)
            if(m):
                self.__update_cookies(rep.cookies)
                target_url = m[0]
                continue

            break

        self.__update_cookies(rep.cookies)

        return rep


    def TryRequestGet(self, _url, **kwargs):
        '''
            Wrapper for requests.get

            TryRequestGet() trys to recover from all portal authentication exceptions raised when invoking HTTP Get method..

            @Return:
                return None when any error occurs.
        '''

        return self.TryRequestOp(_url, WrappedGet, **kwargs)

    def TryRequestPost(self, _url, **kwargs):
        '''
            Wrapper for requests.post
        '''

        return self.TryRequestOp(_url, WrappedPost, **kwargs)



def Login(_username, _password):
    '''

        Login for accessing UESTC's portal system

        @Params:
            _username:      Login user name.
            _password:      Login password

        @Return:
            If no error occurs, return a EAMSSession object.
            Otherwise, it return False.
    '''

    ss = EAMSSession()

    # Login
    if(not ss.Login(_username, _password)):
        return None

    return ss

