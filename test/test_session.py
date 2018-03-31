#! /usr/bin/python

'''

    Test for session module

'''

import unittest
import uestc_eams
import re
import functools
import pdb
from .utils import HookedMethod

class TestSession(unittest.TestCase):
    
    request_case = (
        {
            'method' : 'get'
            , 'URLRegexp' : '^http://idas\.uestc\.edu\.cn/authserver/login(/.*)'
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
            , 'URLRegexp' : '^http://idas\.uestc\.edu\.cn/authserver/login(?.*)?'
            , 'data' : {
                'username' : '2015070804011'
                , 'password' : '104728'
                , 'lt' : 'LT-1974745-HbcPvy2ZPsiAUmwh7a1luf6hjFgD5P1521293830373-Nqwt-cas'
                , 'dllt' : 'userNamePasswordLogin'
                , 'execution' : 'e20s1'
                , '_eventId' : 'submit'
                , 'rmShown' : '1'
            }
            , 'response_code' : 200
            , 'headers' : {
                'Server' : 'openresty'
                , 'Content-Length' : '0'
                , 'Connection' : 'keep-alive'
            }
            , 'text' : ''
        }
    )


    def setUp(self):
        self.__session = uestc_eams.EAMSSession()
        self.__hook_request_op()
        self.__logined = False
        self.__get_login_index_count = 0
        self.__get_login_index_count = 0

    def tearDown(self):
        self.__unhook_request_op()

    @staticmethod
    def MakeResponse(_case):
        text = _case.get('text', '')
        rep = type('Response-faked', (uestc_eams.session.requests.Response,), {'text' : text})()
        headers = _case.get('headers', {})
        for key, val in zip(headers.keys(), headers.values()):
            rep.headers[key] = val
        rep.status_code = _case.get('response_code', 0)
        return rep 
        
    def _my_test_request_get(self, _session, _url, *args, **kwargs):
        '''

            Faked get method to test behaviour.

        '''
        if re.match(r'^http://portal\.uestc\.edu\.cn(/.*)?', _url) or re.match(r'^http://idas\.uestc\.edu\.cn/authserver/login(/.*|\?.*)', _url):
            assert self.__logined != True
            self.__get_login_index_count += 1
            rep = TestSession.MakeResponse(TestSession.request_case[0])
            rep.url = r'http://idas.uestc.edu.cn/authserver/login?'
            print('Index page is requested.')
            return rep


        elif re.match(r'http://eams\.uestc\.edu\.cn/eams/redirect_test', _url):
            if self.__expire_test_tiggered == True:
                rep = TestSession.MakeResponse({
                            'response_code' : 302
                            , 'text' : 'redirect test passed.'
                            , 'headers' : {
                                'Location' : 'http://idas.uestc.edu.cn/index.do'
                            }
                        }
                    )
            else:
                assert self.__logined == True
                rep = TestSession.MakeResponse({
                        'response_code' : 302
                        , 'text' : 'redirect test.'
                        , 'headers' : {
                            'Location' : 'http://idas.uestc.edu.cn/authserver/login?'
                        }
                    }
                )
                print('expired redirect.')
                self.__expire_test_tiggered = True
                self.__get_login_index_count = -1
                self.__logined = False
            
            rep.url = _url
            return rep

        elif re.match(r'http://eams\.uestc\.edu\.cn/eams/200redirect', _url):
            if True == self.__200redir_tiggered:
                rep = TestSession.MakeResponse({'response_code': 200, 'text' : 'ok'})
                self.__expire_test_tiggered = True
                print('in-page redirect finished.')
            else:
                rep = TestSession.MakeResponse({
                        'response_code': 200
                        , 'text' : r'<html xml:lang="zh" xmlns="http://www.w3.org/1999/xhtml"><body><h2>当前用户存在重复登录的情况，已将之前的登录踢出：</h2><pre>用户名：2015070804011 登录时间：1926-08-17 14:20:31.147 操作系统：Android  浏览器：Chrome 60.0.3112.116</pre><br>请<a href="http://eams.uestc.edu.cn/eams/200redirect">点击此处</a>继续</body></html>'
                    })
                self.__200redir_tiggered = True
                print('in-page redirect.') 
            rep.url = _url
            return rep

        elif re.match(r'http://eams\.uestc\.edu\.cn(/.*)?', _url): 
            if True == self.__expire_test_tiggered:
                rep = TestSession.MakeResponse({'response_code' : 200, 'text' : 'ok'})
                rep.url = _url
            else:
                assert self.__logined == True
                rep = TestSession.MakeResponse(TestSession.request_case[0])
                print('make expired.')
                rep.url = r'http://idas.uestc.edu.cn/authserver/login?'
                self.__logined = False
                self.__get_login_index_count = 0
                self.__expire_test_tiggered = True

            return rep



        raise Exception("Unexpected get request : " + _url)

    def _my_test_request_post(self, _session, _url, *args, **kwargs):
        if re.match(r'^http://idas\.uestc\.edu\.cn/authserver/login(\?.*)?', _url):
            assert self.__get_login_index_count == 1
            self.assertEqual(kwargs['data'], {
                        'username' : '2015070804011'
                        , 'password' : '104728'
                        , 'lt' : 'LT-1974745-HbcPvy2ZPsiAUmwh7a1luf6hjFgD5P1521293830373-Nqwt-cas'
                        , 'dllt' : 'userNamePasswordLogin'
                        , 'execution' : 'e20s1'
                        , '_eventId' : 'submit'
                        , 'rmShown' : '1'
                    }
                )
            self.__logined = True
            print('vaild login post.')
            rep = TestSession.MakeResponse(TestSession.request_case[1])
            rep.url = 'http://idas.uestc.edu.cn/authserver/index.do'
            return rep

        elif re.match(r'http://idas\.uestc\.edu\.cn/authserver/logout(\?.*|/.*)?', _url):
            self.assertEqual(self.__logined, True)
            print('Logout page is requested.')
            self.__logined = False
            rep = TestSession.MakeResponse({
                        'response_code' : 200
                        , 'text' : 'test passed.'
                })
            rep.url = 'http://idas.uestc.edu.cn/index.do'
            return rep

        raise Exception("Unexpected post request : " + _url)

    def __hook_request_op(self):
        self.__ori_get = uestc_eams.session.requests.Session.get 
        uestc_eams.session.requests.Session.get = HookedMethod(self._my_test_request_get, self)
        self.__ori_post = uestc_eams.session.requests.Session.post
        uestc_eams.session.requests.Session.post = HookedMethod(self._my_test_request_post, self)

    def __unhook_request_op(self):
        uestc_eams.session.requests.Session.get = self.__ori_get
        uestc_eams.session.requests.Session.post = self.__ori_post 
        
    def test_Session(self):
        # Try login
        print('--> Login test <--')
        assert True == self.__session.Login('2015070804011', '104728')
        assert self.__logined == True
        assert self.__get_login_index_count == 1
        print('passed.', end = '\n\n')

        # Test expire session
        print('--> test expired cookies <--')
        test_url = 'http://eams.uestc.edu.cn/eams'
        self.__expire_test_tiggered = False
        rep = self.__session.TryRequestGet(test_url)
        assert True == self.__expire_test_tiggered
        assert True == self.__logined == True
        assert -1 != rep.url.find(test_url)
        print('passed.', end = '\n\n')

        # Test expire session with no redirects following
        print('--> test expired cookies (no redirects following) <--')
        test_url = 'http://eams.uestc.edu.cn/eams/redirect_test'
        self.__expire_test_tiggered = False
        rep = self.__session.TryRequestGet(test_url, allow_redirects = False)
        assert True == self.__expire_test_tiggered
        assert True == self.__logined
        assert -1 != rep.url.find(test_url)
        assert rep.status_code == 302
        print('passed.', end = '\n\n')

        # Test expire session with HTTP 200 redirects.
        print('--> test expired cookies (200 redirect) <--')
        test_url = 'http://eams.uestc.edu.cn/eams/200redirect'
        self.__expire_test_tiggered = False
        self.__200redir_tiggered = False
        rep = self.__session.TryRequestGet(test_url)
        self.assertEqual(self.__expire_test_tiggered, True)
        self.assertEqual(self.__200redir_tiggered, True)
        print('passed.', end = '\n\n')

        # Test expire session with redirect inside page.
        print('--> test logout <--')
        assert True == self.__session.Logout()
        assert self.__logined == False
        print('passed.', end = '\n\n')
    
