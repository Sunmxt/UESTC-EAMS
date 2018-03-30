'''

    Server Demo by Flask providing HTTP API to access to UESTC EAMS.

    No tokens. No more functions. No plan to be actually used.

'''

from flask import Flask, request, abort, jsonify, g
from uestc_eams.cli import AccountDatabase
from uestc_eams import EAMSSession
from functools import wraps

'''
    Config
'''

DB_PATH = 'account.db'


class EAMSAPIServer:
    def __init__(self, _db_path):
        self.__db = AccountDatabase(_db_path)

    def __def__(self):
        self.__db = None

    def load_session(_process):
        '''
            Load session according to username or session id.
        '''
        @wraps(_process)
        def load_session_wrapper(self, *args, **kwargs):
            sid = kwargs.get('sid', None)
            username = kwargs.get('username', None)
            if sid != None and username != None:
                abort(400) # Bad request
            elif sid == None and username == None:
                abort(400) 

            if sid != None:
                username ,ss = self.__db.GetSessionFromID(sid)
                if not ss: # Not logined.
                    abort(403)
                kwargs.pop('sid')
            else:
                sid, ss = self.__db.GetSessionFromUsername(username)
                if not ss:
                    abort(403)
                kwargs.pop('username')

            self.session = ss
            response = _process(self, *args, **kwargs)
            if self.session != None:
                self.__db.UpdateSessionByUsername(username, self.session)
            else:
                self.__db.DropSession(_username = username)
                
            self.session = None

            return response

        return load_session_wrapper

    def account_login(self):
        if request.method != 'POST':
            abort(405)
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            abort(400)

        response = {'result' : True, 'reason' : 'Succeed'}

        # Check whether logined.
        sid, ss = self.__db.GetSessionFromUsername(username)
        if sid:
            response['reason'] = 'Already logined.'
            return jsonify(**response)

        # Try login.
        ss = EAMSSession()
        result = ss.Login(_username = username, _password = password)
        if result:
            if not self.__db.SaveSession(username, ss):
                response['result'] = False
                response['reason'] = self.__db.Exception.args[0] if self.__db.Exception.args else 'Cannot save session.'
            return jsonify(**response)

        # Unable to login
        response['request'] = False
        response['reason'] = 'Unable to login.'
        return jsonify(**response)

    @load_session
    def query_elect_open(self):
        return jsonify(result = self.session.ElectCourse.Opened)

    @load_session
    def query_electable(self, platform):
        return jsonify(self.session.ElectCourse.Courses)

    @load_session
    def query_elect_platforms(self):
        return jsonify(list(self.session.ElectCourse.Platform.keys()))

    @load_session
    def account_logout(self):
        self.session = None
        return jsonify({'result': True})
        

app = Flask(__name__)

def get_api_server():
    if not hasattr(g, 'server'):
        g.server = EAMSAPIServer(DB_PATH)
    return g.server

@app.route('/user/login', methods = ['POST'])
def api_login():
    return get_api_server().account_login()

@app.route('/user/id/<int:sid>/Elect/Opened', methods = ['Get'])
@app.route('/user/name/<string:username>/Elect/Opened', methods = ['Get'])
def api_query_elect_open(**kwargs):
    return get_api_server().query_elect_open(**kwargs)


@app.route('/user/id/<int:sid>/Elect/<string:platform>/Courses', methods = ['Get'])
@app.route('/user/name/<string:username>/Elect/<string:platform>/Courses', methods = ['Get'])
def api_query_electable(**kwarg):
    return get_api_server().query_electable(**kwarg)

@app.route('/user/id/<int:sid>/Elect/')
@app.route('/user/name/<string:username>/Elect/')
def api_query_elect_platform(**kwarg):
    return get_api_server().query_elect_platforms(**kwarg)

@app.route('/user/id/<int:sid>/logout')
@app.route('/user/name/<string:username>/logout')
def api_logout(**kwarg):
    return get_api_server().account_logout(**kwarg)

