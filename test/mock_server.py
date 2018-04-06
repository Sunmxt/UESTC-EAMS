'''

    Some faked server.


'''


from .mock import MockServer
from .utils import HookedMethod, MakeResponse
from copy import deepcopy

import requests
import uestc_eams 

class RequestsSessionMockServer(MockServer):
    """
        Fake server template by mocking Requests.Session
    """

    def DoPatch(self):
        self.__ori_get = requests.Session.get
        self.__ori_post = requests.Session.post
        requests.Session.get = HookedMethod(self.test_request_get, self)
        requests.Session.post = HookedMethod(self.test_request_post, self)

    def DoUnpatch(self):
        requests.Session.get = self.__ori_get
        requests.Session.post = self.__ori_post

    def test_request_get(self, _session, _url, *args, **kwargs):
        fn = self.GetRouteGETTarget(_url)
        if not fn:
            raise Exception("Unexpected get request : " + _url)
        return fn(_session, _url, *args, **kwargs)

    def test_request_post(self, _session, _url, *args, **kwargs):
        fn = self.GetRoutePOSTTarget(_url)
        if not fn:
            raise Exception("Unexpected post request : " + _url)
        return fn(_session, _url, *args, **kwargs)

class EAMSOPMockServer(MockServer):
    """
        Fake server template by mocking uestc_eams.EAMSSession
    """

    def DoPatch(self):
        self.__ori_try_request_op = uestc_eams.EAMSSession.TryRequestOp
        uestc_eams.EAMSSession.TryRequestOp = HookedMethod(self.test_request_op, self)

    def DoUnpatch(self):
        uestc_eams.EAMSSession.TryRequestOp = self.__ori_try_request_op

    def test_request_op(self, _session, _url, _op, *args, **kwargs):
        if _op == requests.Session.get:
            fn = self.GetRouteGETTarget(_url)
        elif _op == requests.Session.post:
            fn = self.GetRoutePOSTTarget(_url)
        else:
            raise Exception("Unexpected request method.")

        if not fn:
            raise Exception("Unexpected request : " + _url)
        return fn(_session, _url, _op, *args, **kwargs)


class LoginMockServer(RequestsSessionMockServer):
    """
        Login Mock Server
    """

    INDEX_RESPONSE = MakeResponse({
            'text' : """     <form id="casLoginForm" class="fm-v clearfix amp-login-form" role="form" action="/authserver/login?service=http%3A%2F%2Fportal.uestc.edu.cn%2F" method="post">
    <input type="hidden" name="lt" value="LT-1974745-HbcPvy2ZPsiAUmwh7a1luf6hjFgD5P1521293830373-Nqwt-cas"/>
    <input type="hidden" name="dllt" value="userNamePasswordLogin"/>
    <input type="hidden" name="execution" value="e20s1"/>
    <input type="hidden" name="_eventId" value="submit"/>
    <input type="hidden" name="rmShown" value="1">
    """
            , 'response_code' : 200
            , 'headers' : {
                'Server' : 'openresty'
                , 'Content-Type' : 'text/html'
                , 'Content-Length' : '486'
                , 'Connection' : 'keep-alive'
            }
        })

    

    def __init__(self):
        self.Logined = False
        self.GetIndexCount = 0
        self.ExpireTestTiggered = False
        self._200RedirectTiggered = False
        self.InvaildLoginPost = False
        super().__init__()

    @MockServer.Route(r'http://eams\.uestc\.edu\.cn/eams/redirect_test', ['GET'])
    def redirect_test_requested(self, _session, _url, *args, **kwargs):
        if self.ExpireTestTiggered == True:
            rep = MakeResponse({
                        'response_code' : 302
                        , 'text' : 'redirect test passed.'
                        , 'headers' : {
                            'Location' : 'http://idas.uestc.edu.cn/index.do'
                        }
                    }
                )
        else:
            ###> self.assertEqual(self.Login, True)
            rep = MakeResponse({
                    'response_code' : 302
                    , 'text' : 'redirect test.'
                    , 'headers' : {
                        'Location' : 'http://idas.uestc.edu.cn/authserver/login?'
                    }
                }
            )
            print('expired redirect.')
            self.ExpireTestTiggered = True
            ###> self.__get_login_index_count = -1
            self.Login = False
        
        rep.url = _url
        return rep

    
    @MockServer.Route(r'http://eams\.uestc\.edu\.cn/eams/200redirect', ['GET'])
    def redirect200_requested(self, _session, _url, *args, **kwargs):
        if True == self._200RedirectTiggered:
            rep = MakeResponse({'response_code': 200, 'text' : 'ok'})
            self.ExpireTestTiggered = True
            print('in-page redirect finished.')
        else:
            rep = MakeResponse({
                    'response_code': 200
                    , 'text' : r'<html xml:lang="zh" xmlns="http://www.w3.org/1999/xhtml"><body><h2>当前用户存在重复登录的情况，已将之前的登录踢出：</h2><pre>用户名：2015070804011 登录时间：1926-08-17 14:20:31.147 操作系统：Android  浏览器：Chrome 60.0.3112.116</pre><br>请<a href="http://eams.uestc.edu.cn/eams/200redirect">点击此处</a>继续</body></html>'
                })
            self._200RedirectTiggered = True
            print('in-page redirect.') 
        rep.url = _url
        return rep

    @MockServer.Route(r'http://eams\.uestc\.edu\.cn(/.*)?', ['GET'])
    def eams_requested(self, _session, _url, *args, **kwargs):
        if True == self.ExpireTestTiggered:
            rep = MakeResponse({'response_code' : 200, 'text' : 'ok'})
            rep.url = _url
        else:
            ###> self.assertEqual(self.__logined, True)
            rep = deepcopy(LoginMockServer.INDEX_RESPONSE)

            print('make expired.')
            rep.url = r'http://idas.uestc.edu.cn/authserver/login?'
            self.Logined = False
            self.GetIndexCount = 0
            self.ExpireTestTiggered = True

        return rep


    @MockServer.Route(r'^http://portal\.uestc\.edu\.cn(/.*)?', ['GET'])
    @MockServer.Route(r'^http://idas\.uestc\.edu\.cn/authserver/login(/.*|\?.*)', ['GET'])
    def index_requested(self, _session, _url, *args, **kwargs):
        """
            Response with index page
        """
        rep = deepcopy(LoginMockServer.INDEX_RESPONSE)
        rep.url = r'http://idas.uestc.edu.cn/authserver/login?'
        self.GetIndexCount += 1
        return rep

    @MockServer.Route(r'^http://idas\.uestc\.edu\.cn/authserver/login(\?.*)?', ['POST'])
    def login_post_requested(self, _session, _url, *args, **kwargs):
        if kwargs['data'] != {
                    'username' : '2015070804011'
                    , 'password' : '104728'
                    , 'lt' : 'LT-1974745-HbcPvy2ZPsiAUmwh7a1luf6hjFgD5P1521293830373-Nqwt-cas'
                    , 'dllt' : 'userNamePasswordLogin'
                    , 'execution' : 'e20s1'
                    , '_eventId' : 'submit'
                    , 'rmShown' : '1'
                }:
            print('Invaild login post.')
            self.InvaildLoginPost = True
            return None

        self.Logined = True
        print('vaild login post.')
        rep = MakeResponse({
                'response_code' : 200
                , 'headers' : {
                    'Server' : 'openresty'
                    , 'Content-Length' : '0'
                    , 'Connection' : 'keep-alive'
                }
                , 'text' : ''
            })
        rep.url = 'http://idas.uestc.edu.cn/authserver/index.do'
        return rep

    @MockServer.Route(r'http://idas\.uestc\.edu\.cn/authserver/logout(\?.*|/.*)?', ['POST']) 
    def logout_post_requested(self, _session, _url, *args, **kwargs):
        if not self.Logined:
            print('Not logined.')
            self.InvaildLogoutRequest = True
            return None

        print('Logout.')

        rep = MakeResponse({
                    'response_code' : 200
                    , 'text' : 'test passed.'
            })
        rep.url = 'http://idas.uestc.edu.cn/index.do'
        self.Logined = False
        return rep

    
class MockElectServer(EAMSOPMockServer):

    def __init__(self):
        self.GetEnterenceOK = False
        self.GetDefaultPageOK = False
        self.GetStudentCountOK = False
        self.GetCourseDataOK = False

        super().__init__()

    @MockServer.Route('http://eams\.uestc\.edu\.cn/eams/stdElectCourse!queryStdCount\.action\?profileId=1328', ['GET'])
    def student_count_requested(self, _session, _url, _op, **kwargs):
            rep = MakeResponse({
                    'response_code' : 200
                    , 'text' : r"window.lessonId2Counts={'330983':{sc:1,lc:2,coc:3,ac:4,bc:5,cc:6}, '332737': {sc:6,lc:5,coc:4,ac:3,bc:2,cc:1}, '331038' : {sc:0,lc:0,coc:0,ac:0,bc:0,cc:0}}"
                })
            rep.url = _url
            self.GetStudentCountOK = True
            print('student count requested.')
            return rep

    @MockServer.Route('http://eams\.uestc\.edu\.cn/eams/stdElectCourse!data\.action\?profileId=1328', ['GET'])
    def course_data_requested(self, _session, _url, _op, **kwargs):
            rep = MakeResponse({
                    'response_code' : 200
                    , 'text' : r"var lessionJSONs = [{id:330983,no:'A1513220.01',name:'编译从入门到放弃',code:'A1513220',credits:0.1,courseId:39480,startWeek:1,endWeek:12,courseTypeId:17,courseTypeName:'不是课程',courseTypeCode:'X',scheduled:true,hasTextBook:false,period:32,weekHour:4,revertCount:0,withdrawable:false,textbooks:'',teachers:'<a href=\'javascript:showDescription(5120044)\'>666<\/a>',crossCollege:false,campusCode:'1',campusName:'清水河校区',remark:'Just test 1',electCourseRemark:'',arrangeInfo:[{weekDay:2,weekState:'01111111111110000000000000000000000000000000000000000',startUnit:9,endUnit:11,weekStateText:'第1-12周',rooms:'立人楼B108'}],examArrange:''}, {id:332737,no:'A1513220.01',name:'数据库从删库到跑路',code:'A1518220',credits:0.1,courseId:31180,startWeek:1,endWeek:12,courseTypeId:17,courseTypeName:'不是课程1',courseTypeCode:'X',scheduled:true,hasTextBook:false,period:32,weekHour:4,revertCount:0,withdrawable:false,textbooks:'',teachers:'<a href=\'javascript:showDescription(5120044)\'>777<\/a>',crossCollege:false,campusCode:'1',campusName:'清水河校区',remark:'Just test 2',electCourseRemark:'',arrangeInfo:[{weekDay:2,weekState:'00101010101010101010000000000000000000000000000000000',startUnit:9,endUnit:11,weekStateText:'无Text',rooms:'BC108'}],examArrange:''}, {id:331038,no:'A1513220.01',name:'操作系统从入门到入土',code:'A1518220',credits:0.1,courseId:31180,startWeek:1,endWeek:12,courseTypeId:17,courseTypeName:'不是课程2',courseTypeCode:'X',scheduled:true,hasTextBook:false,period:32,weekHour:4,revertCount:0,withdrawable:false,textbooks:'',teachers:'<a href=\'javascript:showDescription(5120044)\'>888<\/a>',crossCollege:false,campusCode:'1',campusName:'清水河校区',remark:'Just test 3',electCourseRemark:'',arrangeInfo:[{weekDay:2,weekState:'00101010101010101010000100010000000000000000000000000',startUnit:9,endUnit:11,weekStateText:'无Text',rooms:'BC108'}],examArrange:''}]"
                })
            rep.url = _url
            self.GetCourseDataOK = True
            print('Course data required.')
            return rep

    @MockServer.Route('http://eams\.uestc\.edu\.cn/eams/stdElectCourse!defaultPage\.action\?electionProfile\.id=1328', ['GET'])
    def default_page_requested(self, _session, _url, _op, **kwargs):
            rep = MakeResponse({
                    'response_code' : 200
                    , 'text' :'''<script type="text/javascript">	
	jQuery(function(){
		jQuery("#electFloatBar").trigger("initStdElectCourseDefaultPage",new function(){
			var electableIds = {};
			var electedIds = {};
			var virtualCashEnabled = false;
			electableIds["l330983"] = "self";
            electableIds["l332737"] = "self";
		    electableIds["l331038"] = "self";
            electedIds["l332737"] = true;
		    electedIds["l331038"] = true; }</script>
'''
                })
            rep.url = _url
            self.GetDefaultPageOK = True
            print('Electing default page requested.')
            return rep

    @MockServer.Route(r'http://eams\.uestc\.edu\.cn/eams/stdElectCourse\.action', ['GET'])
    def enterence_requested(self, _session, _url, _op, **kwargs):
            self.GetEnterenceOK = True
            if self.EnterenceOpened:
                print('enterence requested. [Opened]')
                rep = MakeResponse({
                        'response_code' : 200
                        , 'text' : '''<h2 styl    e="text-align:center">2016-1029 学年2学期 -2学期第二轮抢课（第3时段）—2010级B平台</h2><a style="margin:auto;font-size:16px;" href="stdElectCourse!defaultPage.action?electionProfile.id=1328" target="stdElectDiv">进入选课>>>></a>&nbsp;&nbsp;&nbsp;
<h2 st  e="text-align:center">2017-2018学年2学期 17-18-2学期第二轮抢课（第3时段）—2016级A平台</h2><a style="margin:auto;font-size:16px;" href="stdElectCourse!defaultPage.action?electionProfile.id=1327" target="stdElectDiv">进入选课>>>></a>&nbsp;&nbsp;&nbsp;'''
                    })
                rep.url = _url
                return rep
            else:
                print('enterence requested. [Closed]')
                rep = MakeResponse({
                        'response_code' : 200
                        , 'text' : '''<body><table width="80%" align="center"><tr><td align="center"><h2>现在未到选课时间，无法选课！</h2></td></tr></table></body>
'''
                    })
                rep.url = _url
                return rep

    @MockServer.Route(r'http://eams\.uestc\.edu\.cn/eams/stdElectCourse!batchOperator\.action\?profileId=1328', ['POST'])
    def batch_operator_post(self, _session, _url, _op, **kwargs):
            for name in ('headers', 'data'):
                if not name in kwargs:
                    self.BatchOpArgOK = False
                    return None

            headers = kwargs['headers']
            data = kwargs['data']

            for name in('Referer', 'X-Requested-With', 'Origin'):
                if not name in headers:
                    self.HeaderMissing = True
                    return None

            if headers['Origin'] != 'http://eams.uestc.edu.cn' \
                or headers['X-Requested-With'] != 'XMLHttpRequest':
                self.BadHeaderValue = True

            if not 'operator0' in data or isinstance(data['operator0'], str):
                self.BadOperator = True

            op = data['operator0'].split(':')
            assert op[0].isdigit()
            if op[1] == 'true':
                self.ElectOp = True
                print('Try to elect %s.' % op[0])
                rep = MakeResponse({
                        'response_code' : 200
                        , 'text' : """
<div style="width:85%;color:green;text-align:left;margin:auto;">
				Test选课成功</br>
			</div>
			<script type="text/javascript">
				if(window.electCourseTable){
						window.electCourseTable.lessons({id:""" + op[0] + """})
							.update({
								defaultElected : true,
								elected : true
							    });"""
                    })
            elif op[1] == 'false':
                self.ElectOp = False
                print('Try to cancel %s.' % op[0])
                rep = MakeResponse({
                       'response_code' : 200
                       , 'text' : """<div style="width:85%;color:green;text-align:left;margin:auto;">
				Test退课成功</br>
			</div>
		</td>
			<script type="text/javascript">
				if(window.electCourseTable){
						window.electCourseTable.lessons({id:""" + op[0] + """})
							.update({
								defaultElected : false,
								elected : false});"""
                        })
            rep.url = _url
            return rep
