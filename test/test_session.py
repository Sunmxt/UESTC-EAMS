#! /usr/bin/python

'''

    Test for session module

'''

import unittest
import uestc_eams

from .mock_server import LoginMockServer
from .utils import HookedMethod, MakeResponse

mock_login = LoginMockServer()

class TestSession(unittest.TestCase):
 
    @mock_login.Patch
    def test_Session(self):
        self.__session = uestc_eams.EAMSSession()

        # Try login
        print('--> Login test <--')
        self.assertTrue(self.__session.Login('2015070804011', '104728'))
        self.assertTrue(mock_login.Logined)
        self.assertEqual(mock_login.GetIndexCount, 1)
        print('passed.', end = '\n\n')

        # Test expire session
        print('--> test expired cookies <--')
        test_url = 'http://eams.uestc.edu.cn/eams'
        mock_login.ExpireTestTiggered = False
        rep = self.__session.TryRequestGet(test_url)
        self.assertTrue(mock_login.ExpireTestTiggered)
        self.assertTrue(mock_login.Logined)
        self.assertNotEqual(-1, rep.url.find(test_url))
        print('passed.', end = '\n\n')

        # Test expire session with no redirects following
        print('--> test expired cookies (no redirects following) <--')
        test_url = 'http://eams.uestc.edu.cn/eams/redirect_test'
        mock_login.ExpireTestTiggered = False
        rep = self.__session.TryRequestGet(test_url, allow_redirects = False)
        self.assertTrue(mock_login.ExpireTestTiggered)
        self.assertTrue(mock_login.Logined)
        self.assertNotEqual(-1, rep.url.find(test_url))
        self.assertEqual(rep.status_code, 302)
        print('passed.', end = '\n\n')

        # Test expire session with HTTP 200 redirects.
        print('--> test expired cookies (200 redirect) <--')
        test_url = 'http://eams.uestc.edu.cn/eams/200redirect'
        mock_login.ExpireTestTiggered = False
        mock_login._200RedirectTiggered = False
        rep = self.__session.TryRequestGet(test_url)
        self.assertEqual(mock_login.ExpireTestTiggered, True)
        self.assertEqual(mock_login._200RedirectTiggered, True)
        print('passed.', end = '\n\n')

        # Test expire session with redirect inside page.
        print('--> test logout <--')
        self.assertTrue(self.__session.Logout())
        self.assertFalse(mock_login.Logined)
        print('passed.', end = '\n\n')
    
