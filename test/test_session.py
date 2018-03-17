#! /usr/bin/python

'''

    Test for session module

'''

import unittest
import uestc_eams
from .utils import HookedMethod

request_case = (
    {
        'method' : 'get'
        , 'URLRegexp': '^http://portal.uestc.edu.cn(/.*)?'
        , 'response_code' : 302
        , 'headers' : {
            'Server': 'openresty'
            , 'Date': 'Sat, 17 Mar 2018 13:37:10 GMT'
            , 'Content-Type' : 'text/html'
            , 'Content-Length' : '154'
            , 'Connection' : 'keep-alive'
            , 'Location' : 'http://idas.uestc.edu.cn/authserver/login?service=http://portal.uestc.edu.cn/'
            }
        , 'text' : """
<html>
<head><title>302 Found</title></head>
<body bgcolor="white">
<center><h1>302 Found</h1></center>
<hr><center>nginx</center>
</body>
</html>
"""
        }
    }
    , {
        'method' : 'get'
        , 'URLRegexp' : '^http://idas.uestc.edu.cn/authserver/login(/.*)'
        , 'response_code' : 200
        , 'headers' : {
            'Server' : 'openresty'
            , 'Content-Type' : 'text/html'
            , 'Content-Length' : '486'
            , 'Connection' : 'keep-alive'
        }
        , 'text' : """
 <form id="casLoginForm" class="fm-v clearfix amp-login-form" role="form" action="/authserver/login?service=http%3A%2F%2Fportal.uestc.edu.cn%2F" method="post">
<input type="hidden" name="lt" value="LT-1974745-HbcPvy2ZPsiAUmwh7a1luf6hjFgD5P1521293830373-Nqwt-cas"/>
<input type="hidden" name="dllt" value="userNamePasswordLogin"/>
<input type="hidden" name="execution" value="e20s1"/>
<input type="hidden" name="_eventId" value="submit"/>
<input type="hidden" name="rmShown" value="1">
"""
    }
    , {
        'method' : 'post'
        , 'URLRegexp' : '^'
    }
)

class TestSessionLogin(unittest.TestCase):    
    def setUp(self):
        self.__session = uestc_eams.EAMSSession()
        self.__hook_request_op()
        self.__stage = 0
        pass

    def tearDown(self):
        self.__unhook_request_op()
    
    def _my_test_request_get(self, _session, _url, *args, **kwargs):
        stage = self.getattr(self, 'test_stage', None)
        
        if _url.search('http://portal.uestc.edu.cn') == 0 :
            self.assertEqual(self.__stage, 0)
            uestc_eams.session.requests.Resp

    def _my_test_request_post(self, _session, _url, *args, **kwargs):
        self.assertEqual(self.__stage, 1)

            
        
    def __hook_request_op(self):
        self.__ori_get = uestc_eams.session.requests.Session.get 
        uestc_eams.session.requests.Session.get = HookedMethod(self._my_test_request_get, self)
        self.__ori_post = uestc_eams.session.requests.Session.post
        uestc_eams.session.Session.post = HookedMethod(self._my_test_request_post, self)

    def __unhook_request_op(self):
        uestc_eams.session.requests.Session.get = self.__ori_get
        uestc_eams.session.requests.Session.post = self.__ori_post 
        
    def test_Login(self):
        self.__session.Login('2015070804011', '104728')
        
        

