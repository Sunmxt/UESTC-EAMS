import uestc_eams
import unittest

from .mock_server import MockElectServer

mock_elect = MockElectServer()


class TestElectCourseSession(unittest.TestCase):

    @mock_elect.Patch
    def test_ElectCourseSession(self):
        ss = uestc_eams.EAMSSession()

        # Test querying elect course enterence.
        print('--> test load platform <--')
        mock_elect.GetEnterenceOK = False
        mock_elect.EnterenceOpened = True
        ecss = uestc_eams.elect_course.EAMSElectCourseSession(ss)
        self.assertTrue(ecss.Opened)
        self.assertTrue(mock_elect.GetEnterenceOK)
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
        mock_elect.GetEnterenceOK = False
        mock_elect.EnterenceOpened = False
        ecss = uestc_eams.elect_course.EAMSElectCourseSession(ss)
        self.assertEqual(len(ecss.Platform), 0)
        self.assertFalse(ecss.Opened)
        self.assertTrue(mock_elect.GetEnterenceOK)
        print('passed.', end = '\n\n')

    @mock_elect.Patch
    def test_ElectCoursePlatform(self):
        ss = uestc_eams.EAMSSession()
        platform = uestc_eams.elect_course.EAMSElectCourseSession.elect_course_platform('A', 'stdElectCourse!defaultPage.action?electionProfile.id=1328', ss)

        # Test load basic infomation
        print('--> test load basic platform information <--')
        mock_elect.GetDefaultPageOK = False
        self.assertEqual(platform.ElectType, uestc_eams.CATCH)
        self.assertEqual(platform.Elected, [332737, 331038])
        self.assertTrue(mock_elect.GetDefaultPageOK)
        print('passed.', end = '\n\n')

        # Test load course list
        print('--> test load course list <--')
        mock_elect.GetCourseDataOK = False
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
        self.assertTrue(mock_elect.GetCourseDataOK)
        print('passed.',  end = '\n\n')

        # Test querying student counts.
        print("--> test querying stuent counts <--")
        mock_elect.GetStudentCountOK = False
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
        self.assertTrue(mock_elect.GetStudentCountOK)
        print('passed.', end = '\n\n')


        # Test elect
        print('--> test electing <--')
        mock_elect.ElectOp = None
        self.assertTrue(platform.Elect(330983, uestc_eams.ELECT))
        self.assertEqual(mock_elect.ElectOp, True)
        self.assertIn(330983, platform.Elected)
        print('passed.', end = '\n\n')

        # Test cancel
        print('--> test canceling <--')
        mock_elect.ElectOp = None
        self.assertTrue(platform.Elect(331038, uestc_eams.CANCEL))
        self.assertEqual(mock_elect.ElectOp, False)
        self.assertNotIn(331038, platform.Elected)
        print('passed.', end = '\n\n')

        
