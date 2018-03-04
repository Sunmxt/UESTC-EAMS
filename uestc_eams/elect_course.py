'''

    Course electing module.


    Need test:
        1. elected course loading
        2. cash changing operation
        3. available course loading.

'''

UNKNOWN = 0
CASH = 1
CATCH = 2

ELECT = True
CANCEL = False 

from .base import *

class EAMSElectCourseSession:
    '''
        UESTC's course-elect interface.

        Created by EAMSSession.CreateElectCourseSession().
    '''

    class elect_course_platform:

        ELECT_TYPE_STRING = {
            UNKNOWN : 'Unknown'
            , CASH : 'Cash'
            , CATCH : 'Catch'
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

        @property
        def Elected(self):
            if(not self.__elected_loaded):
                self.__load_basic_infomation()
            return self.__elected

        def __init__(self, _name, _url, _session):
            self.__elect_type = UNKNOWN

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

        def __load_elected_course_from_page(self, _page):
            if self.__elected_loaded:
                return 

            _elected = re.match('electedIds\["(.+)"\]', _page)
            self.__elected = [int(x[1:]) if x[0]=='l' else int(x) for x in _elected]

            self.__elected_loaded = True
            
            

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

            #$$$$$
            m = re.findall(r'var\s+virtualCashEnabled\s*=\s*(false|true)', open('eams/cappkg/elect_default_page.html').read())
            
            if(not m):
                return False

            if(m[0].lower() == 'false'):
                self.__elect_type = CATCH
            else:
                self.__elect_type = CASH

            self.__basic_loaded = True

            self.__load_elected_course_from_page(rep.text);
                

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
            #$$$$$$$
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
            if(_op == CANCEL):
                op_data['operator0'] = '%d:false' % _id
            else:
                op_data['operator0'] = '%d:true:0' % _id

            if(self.__elect_type == CASH):
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

            m = re.search(r'window\.electCourseTable\.lessons\({id:\d+}\)\.update\({(.*?)}\)', text)
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
            '''
                Change electing cash.

                @Params:
                    _id             Course ID
                    _cash           New cash.

                @Return:
                    return True if successfully change the cash.
            '''
            if not isinstance(_id, int):
                raise TypeError('_id should be a integar.')
            if not isinstance(_cash, int):
                raise TypeError('_cash should be a integar.')

            header = {
                'UserAgent' : UserAgent
                , 'Referer' : EAMSBaseUrl + ElectDefault + "?profileId=%d" % self.__profile_id
                , 'X-Referered-With' : 'XMLHttpRequest'
            } 
            
            op_data = {
                'profileId' : self.__profile_id
                , 'lessenId' : _id
                , 'changeCost' : _cash
            }

            rep = self.__session.TryRequestPost(EAMSBaseUrl + ElectCashChange \
                                , headers = header, data = op_data)

            '''
                Here check whether operation is succssful and extract extra information.
                if not, return (False, result_message)
            '''
            return (True, result_message) 
            


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

        #if(not isinstance(_session, EAMSSession)):
        #    raise TypeError('_session should be a EAMSSession')


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

