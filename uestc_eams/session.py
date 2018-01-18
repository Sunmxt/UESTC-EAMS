'''
    Session module for accessing UESTC EMAS System
'''


import requests
import re
import pdb


'''
    Setting
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
    Global
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
    UNKNOWN = 0 # 未知
    CASH = 1    # 权重
    CATCH = 2   # 抢课

    ELECT = True    #
    CANCEL = False  #

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


class EAMSElectCourseSession:
    '''
        UESTC's course-elect interface.

        Created by EAMSSession.CreateElectCourseSession().
    '''

    class elect_course_platform:

        ELECT_TYPE_STRING = {
            EAMSSession.UNKNOWN : 'Unknown'
            , EAMSSession.CASH : 'Cash'
            , EAMSSession.CATCH : 'Catch'
        }

        @property
        def URL(self):
            return self.__origin_url

        @property
        def Name(self):
            return self.__name

        @property
        def ElectType(self):
            if(not self.__basic_loaded):
                self.__load_basic_infomation()

            return self.__elect_type

        @property
        def ElectTypeString(self):
            if(not self.__basic_loaded):
                self.__load_basic_infomation()

            return EAMSElectCourseSession.elect_course_platform.ELECT_TYPE_STRING[self.__elect_type]

        @property
        def Courses(self):
            if(not self.__courses_loaded):
                self.__load_available_courses()
            return self.__courses

        @property
        def Counts(self):
            if(not self.__counts_loaded):
                self.__load_student_counts()
            return self.__counts

        def __init__(self, _name, _url, _session):
            self.__elect_type = EAMSSession.UNKNOWN

            self.__courses = {}
            self.__counts = {}
            self.__elected = []
            
            self.__elected_loaded = False
            self.__counts_loaded = False
            self.__courses_loaded = False
            self.__basic_loaded = False

            self.__name = _name

            self.__origin_url = _url
            self.__url = _url
            if(EAMSBaseUrl[-1] != '/' and self.__url[0] != '/'):
                self.__url = '/' + self.__url
            else:
                if(EAMSBaseUrl[-1] == '/' and self.__url[0] == '/'):
                    self.__url = self.__url[1:]

            profile_id = re.search(r'electionProfile\.id\s*=\s*(\d+)', _url)
            if(not profile_id):
                raise EAMSException('Unknown profile id.')

            self.__profile_id = int(profile_id.groups()[0])

            self.__session = _session

        def __load_basic_infomation(self):
            '''

                Reload basic course-elect information of current plarform

                @Return:
                    True        Succeed
                    False       Failed

            '''
            
            full_url = EAMSBaseUrl + self.__url
            header = {
                    'User-Agent' : UserAgent
                    ,'Referer' : EAMSBaseUrl + ElectCourseUrl
                }

            #pdb.set_trace()
            #rep = self.__session.TryRequestGet(full_url, headers = header)
            #if(not rep):
            #    return False

            m = re.findall(r'var\s+virtualCashEnabled\s*=\s*(false|true)', open('eams/cappkg/elect_default_page.html').read())
            
            if(not m):
                return False

            if(m[0].lower() == 'false'):
                self.__elect_type = EAMSSession.CATCH
            else:
                self.__elect_type = EAMSSession.CASH

            self.__basic_loaded = True

            return True

        def __load_student_counts(self):
            '''
                Update student counts of the available courses.

                @Return:
                    the number of available courses.
            '''
            header = {
                'User-Agent' : UserAgent
                , 'Referer' : EAMSBaseUrl + self.__url
            }
            '''
            rep = self.__session.TryRequestGet(\
                            EAMSBaseUrl + ElectStudentCount + '?profileId=%d' % self.__profile_id\
                            ,headers = header)
            if(not rep):
                return 0
            '''

            #lic = re.search(r'{.*}', rep.text)
            lic = re.search(r'{(.*)}', open('eams/cappkg/queryStdCount.action.js').read())
            if(not lic):
                return 0
            cjd = eval('{' + lic.groups()[0] + '}', type('PARSE', (dict,), {'__getitem__': lambda s,n:n})())

            self.__counts = {
                int(_id) : {
                    'current' : info['sc']
                    , 'limit': info['lc']
                    , 'cross_limit': info['coc']
                    , 'current_a' : info['ac']
                    , 'current_b' : info['bc']
                    , 'current_c' : info['cc']
                } for _id, info in zip(cjd.keys(), cjd.values())
            }

            self.__counts_loaded = True

            return len(self.__counts)


        def __load_available_courses(self):
            '''
                Update available course list.

                @Return:
                    the number of available courses.
            '''
            header = {
                'User-Agent' : UserAgent
                , 'Referer' : EAMSBaseUrl + self.__url
            }
            
            rep = self.__session.TryRequestGet( \
                EAMSBaseUrl + ElectCourseData + '?profileId=%d' % self.__profile_id \
                , )
            if(not rep):
                return 0
            
            cj = re.search(r'{.*}', rep.text)
            if(not cj):
                return 0
            cjd = eval('{'+ cj.groups[0] +'}', type('PARSE', (dict,), {'__getitem__': lambda s,n:n}))

            self.__courses = {
                _id : {
                    'number' : info['no']
                    , 'credits': info['credits']
                    , 'teachers' : info['teachers']
                    , 'campus' : info['campusName']
                    , 'remark' : info['electCourseRemark']
                    , 'exam' : info['examArrange']
                    , 'arrange' : info['arrangeInfo']
                } for _id, info in zip(cjd.keys(), cjd.values())
            }
            
            self.__courses_loaded = True

            return len(self.CourseById)

        def Elect(self, _id, _op, _cash = 0):
            '''
                Elect the specified course.

                @Params:
                    _id     [int]   Course ID
                    _op     [bool]  True(Elect) or False(Cancel)
                    _cash   [int]   Cash. Ignored for cancel operation. Default to 0.

                @Return:
                    A tuple :
                    (Result, Descrpition)

                    Result          [bool]  True if succeed.
                    Descrpition     [str]   Description of result.
            '''

            if(not isinstance(_op, bool)):
                raise TypeError('_op should be a boolean')
                return (False, 'Invailed parameters')
            if(not isinstance(_op, int)):
                raise TypeError('_id should be a integar')
                return (False, 'Invailed parameters')

            if(not self.__basic_loaded):
                self.__load_basic_infomation()
                if(not self.__basic_loaded):
                    return (False, 'Unable to load basic information')
            
            header = {
                'User-Agent' : UserAgent
                , 'Referer' : EAMSBaseUrl + ElectDefault + '?profileId=%d' % self.__profile_id
                , 'X-Requested-With' : 'XMLHttpRequest'
            }

            op_data = {}
            if(_op == EAMSSession.CANCEL):
                op_data['operator0'] = '%d:false' % _id
            else:
                op_data['operator0'] = '%d:true:0' % _id

            if(self.__elect_type == EAMSSession.CASH):
                op_data['virtualCashCost' + _id] = _cash

            rep = self.__session.TryRequestPost(EAMSBaseUrl + ElectOperate \
                                , headers = header, data = op_data)
            if(not rep):
                return (False, 'Error occurs in POST request')
            #text = open('eams/cappkg/batchop_reply.html').read()
            #text = text.replace('\r', '').replace('\t', '').replace('\n', '')
            text = rep.text.replace('\r', '').replace('\t', '').replace('\n', '')
            m = re.search(r'<div(?:\s*.*?=\".*\")*\s*>(.*?)(?:\s*</.*>)*</div>', text)
            if(not m):
                result_message = ''
            else:
                result_message = m.groups()[0]

            m = re.search(r'window\.electCourseTable\.lessons\({id:333103}\)\.update\({(.*?)}\)', text)
            if(not m):
                return (False, result_message)
            m = m.groups()[0].replace('true', 'True').replace('false', 'False')
            update_dict = eval('{' + m + '}', type('PARSE', (dict,), {'__getitem__':lambda s,n:n})())
            if(update_dict.get('elected') != True):
                return (False, result_message)

            self.__elected.append(_id)
            return (True, result_message)

        def Refresh(self):
            '''
                Refresh information about platform
            '''

            self.__counts_loaded = False
            self.__courses_loaded = False
            self.__basic_loaded = False

        def ChangeCash(self, _id, _cash):
            pass


    @property
    def Opened(self):
        return self.__opened

    @property
    def Platform(self):
        if(not self.__platform_loaded):
            self.__load_platforms()
        return self.__platform


    def __init__(self, _cookiejar_ref_list, _session):
        if(not isinstance(_cookiejar_ref_list, list)):
            raise TypeError('_cookiejar_ref_list should be a list')

        if(not isinstance(_session, EAMSSession)):
            raise TypeError('_session should be a EAMSSession')


        self.__opened = False
        self.__platform = {}
        self.__platform_loaded = False
        self.__cookiejar_ref_list = _cookiejar_ref_list
        self.__session = _session

        self.__platform_by_url = {}

    def __generate_platform_index(self):
        self.__platform_by_url = {
            interface.URL : interface
            for interface in self.__platform.values()
        }

    def GetPlatformByName(self, _name):
        return self.__platform_by_name.get(_name)['interface']

    def __load_platforms(self):
        '''
            Update available course resourse including:
                1) Platform information
                2) Available course resource in each platform.
            and build operating interface.

            @Return:
                return False when no platform is available.
                return True when platforms is available
        '''

        header = {
            'User-Agent' : UserAgent
        }


        rep = self.__session.TryRequestGet(EAMSBaseUrl + ElectCourseUrl \
                                            , headers = header)

        if(not rep):
            return False

        plat_info = re.findall(r'(\w)平台.*?\<a.+?href=\"(.*?)\".*?\>\S*?进入选课'\
                    , open('eams/cappkg/stdElectCourse.html').read(), flags=re.DOTALL)
        #plat_info = re.findall(r'(\w)平台.*?\<a.+?href=\"(.*?)\".*?\>\S*?进入选课'\
        #                        , rep.text)

        if(len(plat_info) == 0):
            self.__opened = False
            self.__platform = []
            self.__platform_by_url = {}
            return False

        self.__opened = True
        # check whether refreshing is needed.
        need_refresh = False
        count = 0
        for name, url in plat_info:
            count += 1
            target_dict = self.__platform_by_url.get(url)
            if(not target_dict):
                need_refresh = True
                break
            else:
                target_dict['name'] = name

        if(count != len(self.__platform)):
            need_refresh = True

        if(not need_refresh):
            return len(self.__platform) != 0

        # Refresh
        new_plat = {}
        for name, url in plat_info:
            interface = self.__platform_by_url.get(url)
            if(not target_dict):
                interface = EAMSElectCourseSession.elect_course_platform(name, url, self.__session)
                new_plat[name] = interface

        self.__platform = new_plat
        self.__generate_platform_index()

        self.__platform_loaded = True
        return True

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

