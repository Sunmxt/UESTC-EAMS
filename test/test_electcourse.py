from .utils import HookedMethod, MakeResponse
import uestc_eams
import unittest
import re
import pdb


class TestElectCourseSession(unittest.TestCase):
    def setUp(self):
        self.__ori_try_request_op = uestc_eams.EAMSSession.TryRequestOp
        uestc_eams.EAMSSession.TryRequestOp = HookedMethod(self.__hooked_request_op, self)
        #self.maxDiff = None

    def tearDown(self):
        uestc_eams.EAMSSession.TryRequestOp = self.__ori_try_request_op

    def __hooked_request_op(self, _session, _url, _op, **kwargs):
        if _op == uestc_eams.session.requests.Session.get:
            if -1 != _url.find('http://eams.uestc.edu.cn/eams/stdElectCourse.action'):
                self.__get_enterence_page_ok = True
                if self.__enterence_open:
                    print('enterence requested. [Opened]')
                    rep = MakeResponse({
                            'response_code' : 200
                            , 'text' : '''<h2 styl    e="text-align:center">2016-1029 学年2学期 -2学期第二轮抢课（第3时段）—2010级B平台</h2><a style="margin:auto;font-size:16px;" href="stdElectCourse!defaultPage.action?electionProfile.id=1328" target="stdElectDiv">进入选课>>>></a>&nbsp;&nbsp;&nbsp;
<h2 styl    e="text-align:center">2017-2018学年2学期 17-18-2学期第二轮抢课（第3时段）—2016级A平台</h2><a style="margin:auto;font-size:16px;" href="stdElectCourse!defaultPage.action?electionProfile.id=1327" target="stdElectDiv">进入选课>>>></a>&nbsp;&nbsp;&nbsp;'''
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
                
            elif -1 != _url.find('http://eams.uestc.edu.cn/eams/stdElectCourse!defaultPage.action?electionProfile.id=1328'):
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
                self.__get_default_page = True
                print('Electing default page requested.')
                return rep
            elif -1 != _url.find('http://eams.uestc.edu.cn/eams/stdElectCourse!data.action?profileId=1328'):
                rep = MakeResponse({
                        'response_code' : 200
                        , 'text' : r"var lessionJSONs = [{id:330983,no:'A1513220.01',name:'编译从入门到放弃',code:'A1513220',credits:0.1,courseId:39480,startWeek:1,endWeek:12,courseTypeId:17,courseTypeName:'不是课程',courseTypeCode:'X',scheduled:true,hasTextBook:false,period:32,weekHour:4,revertCount:0,withdrawable:false,textbooks:'',teachers:'<a href=\'javascript:showDescription(5120044)\'>666<\/a>',crossCollege:false,campusCode:'1',campusName:'清水河校区',remark:'Just test 1',electCourseRemark:'',arrangeInfo:[{weekDay:2,weekState:'01111111111110000000000000000000000000000000000000000',startUnit:9,endUnit:11,weekStateText:'第1-12周',rooms:'立人楼B108'}],examArrange:''}, {id:332737,no:'A1513220.01',name:'数据库从删库到跑路',code:'A1518220',credits:0.1,courseId:31180,startWeek:1,endWeek:12,courseTypeId:17,courseTypeName:'不是课程1',courseTypeCode:'X',scheduled:true,hasTextBook:false,period:32,weekHour:4,revertCount:0,withdrawable:false,textbooks:'',teachers:'<a href=\'javascript:showDescription(5120044)\'>777<\/a>',crossCollege:false,campusCode:'1',campusName:'清水河校区',remark:'Just test 2',electCourseRemark:'',arrangeInfo:[{weekDay:2,weekState:'00101010101010101010000000000000000000000000000000000',startUnit:9,endUnit:11,weekStateText:'无Text',rooms:'BC108'}],examArrange:''}, {id:331038,no:'A1513220.01',name:'操作系统从入门到入土',code:'A1518220',credits:0.1,courseId:31180,startWeek:1,endWeek:12,courseTypeId:17,courseTypeName:'不是课程2',courseTypeCode:'X',scheduled:true,hasTextBook:false,period:32,weekHour:4,revertCount:0,withdrawable:false,textbooks:'',teachers:'<a href=\'javascript:showDescription(5120044)\'>888<\/a>',crossCollege:false,campusCode:'1',campusName:'清水河校区',remark:'Just test 3',electCourseRemark:'',arrangeInfo:[{weekDay:2,weekState:'00101010101010101010000100010000000000000000000000000',startUnit:9,endUnit:11,weekStateText:'无Text',rooms:'BC108'}],examArrange:''}]"
                    })
                rep.url = _url
                self.__get_course_data = True
                print('Course data required.')
                return rep
            elif -1 != _url.find('http://eams.uestc.edu.cn/eams/stdElectCourse!queryStdCount.action?profileId=1328'):
                rep = MakeResponse({
                        'response_code' : 200
                        , 'text' : r"window.lessonId2Counts={'330983':{sc:1,lc:2,coc:3,ac:4,bc:5,cc:6}, '332737': {sc:6,lc:5,coc:4,ac:3,bc:2,cc:1}, '331038' : {sc:0,lc:0,coc:0,ac:0,bc:0,cc:0}}"
                    })
                rep.url = _url
                self.__get_student_count = True
                print('student count requested.')
                return rep

            raise Exception('Unexcepted GET request: ' + _url)




        elif _op == uestc_eams.session.requests.Session.post:
            if -1 != _url.find(r'http://eams.uestc.edu.cn/eams/stdElectCourse!batchOperator.action?profileId=1328'):
                self.assertIn('headers', kwargs)
                self.assertIn('data', kwargs)
                headers = kwargs['headers']
                data = kwargs['data'] 
                self.assertIn('Referer', headers)
                self.assertIn('X-Requested-With', headers)
                self.assertIn('Origin', headers)
                self.assertEqual(headers['Origin'], 'http://eams.uestc.edu.cn')
                self.assertEqual(headers['Referer'], 'http://eams.uestc.edu.cn/eams/stdElectCourse!defaultPage.action?electionProfile.id=1328')
                self.assertEqual(headers['X-Requested-With'], 'XMLHttpRequest')
                self.assertIn('operator0', data)
                self.assertIsInstance(data['operator0'], str)

                op = data['operator0'].split(':')
                self.assertTrue(op[0].isdigit())
                if op[1] == 'true':
                    self.__elect_op = True
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
                    self.__elect_op = False
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
                
            raise Exception('Unexcepted POST requests: ' + _url)

        raise Exception('Unexcepted HTTP Method.')

        
    def test_ElectCourseSession(self):
        ss = uestc_eams.EAMSSession()

        # Test querying elect course enterence.
        print('--> test load platform <--')
        self.__get_enterence_page_ok = False
        self.__enterence_open = True
        ecss = uestc_eams.elect_course.EAMSElectCourseSession(ss)
        self.assertTrue(ecss.Opened)
        self.assertTrue(self.__get_enterence_page_ok)
        self.assertEqual(len(ecss.Platform), 2)
        self.assertIsInstance(ecss.Platform['B'], uestc_eams.elect_course.EAMSElectCourseSession.elect_course_platform)
        self.assertIsInstance(ecss.Platform['A'], uestc_eams.elect_course.EAMSElectCourseSession.elect_course_platform)
        self.assertEqual(ecss.Platform['B'].URL, r'stdElectCourse!defaultPage.action?electionProfile.id=1328')
        self.assertEqual(ecss.Platform['A'].URL, r'stdElectCourse!defaultPage.action?electionProfile.id=1327')
        self.assertEqual(ecss.Platform['A'].ProfileID, 1327)
        self.assertEqual(ecss.Platform['B'].ProfileID, 1328)
        print('passed.', end = '\n\n')

        # Test querying elect course closed enterence
        print('--> test load platform [no enterence] <--')
        self.__get_enterence_page_ok = False
        self.__enterence_open = False
        ecss = uestc_eams.elect_course.EAMSElectCourseSession(ss)
        self.assertEqual(len(ecss.Platform), 0)
        self.assertFalse(ecss.Opened)
        self.assertTrue(self.__get_enterence_page_ok)
        print('passed.', end = '\n\n')

    def test_ElectCoursePlatform(self):
        ss = uestc_eams.EAMSSession()
        platform = uestc_eams.elect_course.EAMSElectCourseSession.elect_course_platform('A', 'stdElectCourse!defaultPage.action?electionProfile.id=1328', ss)

        # Test load basic infomation
        print('--> test load basic platform information <--')
        self.__get_default_page = False
        self.assertEqual(platform.ElectType, uestc_eams.CATCH)
        self.assertEqual(platform.Elected, [332737, 331038])
        self.assertTrue(self.__get_default_page)
        print('passed.', end = '\n\n')

        # Test load course list
        print('--> test load course list <--')
        self.__get_course_data = False
        c = [
                {
                    'name': '编译从入门到放弃'
                    , 'id' : 330983
                    , 'credits': 0.1
                    , 'teachers' : ('666', )
                    , 'campus' : '清水河校区'
                    , 'remark' : 'Just test 1'
                    , 'exam' : ''
                    , 'week_hour' : 4
                    , 'type' : '不是课程'
                    , 'arrange' : ({'day':2, 'start':9, 'end':11, 'weeks':((2,13),), 'room':'立人楼B108'},)
                }
                , {
                    'name': '数据库从删库到跑路'
                    , 'id' : 332737
                    , 'credits': 0.1
                    , 'teachers' : ('777', )
                    , 'campus' : '清水河校区'
                    , 'remark' : 'Just test 2'
                    , 'exam' : ''
                    , 'week_hour' : 4
                    , 'type' : '不是课程1'
                    , 'arrange' : ({'day':2, 'start':9, 'end':11, 'weeks':((3,3),(5,5),(7,7),(9,9),(11,11),(13,13),(15,15),(17,17),(19,19)), 'room':'BC108'},)
                }
                , {
                    'name': '操作系统从入门到入土'
                    , 'id' : 331038
                    , 'credits': 0.1
                    , 'teachers' : ('888', )
                    , 'campus' : '清水河校区'
                    , 'remark' : 'Just test 3'
                    , 'exam' : ''
                    , 'week_hour' : 4
                    , 'type' : '不是课程2'
                    , 'arrange' : ({'day':2, 'start':9, 'end':11, 'weeks':((3,3),(5,5),(7,7),(9,9),(11,11),(13,13),(15,15),(17,17),(19,19),(24,24),(28,28)), 'room':'BC108'},)
                }
            ]
        self.assertEqual(platform.Courses, c)
        self.assertTrue(self.__get_course_data)
        print('passed.',  end = '\n\n')

        # Test querying student counts.
        print("--> test querying stuent counts <--")
        self.__get_student_count = False
        c = {
                330983 : {
                    'current' : 1
                    , 'limit' : 2
                    , 'cross_limit' : 3
                    , 'current_a' : 4
                    , 'current_b' : 5
                    , 'current_c' : 6
                }
                , 332737 : {
                    'current' : 6
                    , 'limit' : 5
                    , 'cross_limit' : 4
                    , 'current_a' : 3
                    , 'current_b' : 2
                    , 'current_c' : 1
                }
                , 331038 : {
                    'current' : 0
                    , 'limit' : 0
                    , 'cross_limit' : 0
                    , 'current_a' : 0
                    , 'current_b' : 0
                    , 'current_c' : 0
                }
            }
        self.assertEqual(platform.Counts, c)
        self.assertTrue(self.__get_student_count)
        print('passed.', end = '\n\n')


        # Test elect
        print('--> test electing <--')
        self.__elect_op = None
        self.assertTrue(platform.Elect(330983, uestc_eams.ELECT))
        self.assertEqual(self.__elect_op, True)
        self.assertIn(330983, platform.Elected)
        print('passed.', end = '\n\n')

        # Test cancel
        print('--> test canceling <--')
        self.__elect_op = None
        self.assertTrue(platform.Elect(331038, uestc_eams.CANCEL))
        self.assertEqual(self.__elect_op, False)
        self.assertNotIn(331038, platform.Elected)
        print('passed.', end = '\n\n')

        
