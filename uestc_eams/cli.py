'''

    Commandline interface to accessing UESTC EAMS system.


'''

#import re
import os
import os.path
import getopt
import sqlite3
import pickle
from .session import Login, EAMSSession
from .base import ELECT, CANCEL

'''
    Some constants
'''

ERR_OK = 0
ERR_PARAMS = 1
ERR_NETWORK = 2
ERR_DB = 3

HELP_TEXT = """
Access to UESTC EAMS system. 

Usage: %s <command> [options] < <username> -p <password> | -i account_id>

Command:
    login       <account> [options]             Login with account.
    logout      <account_id>                    Logout.
    query                                       Query information
    elect                                       Elect course.

Common options:
    -p  --password                              Specified account password.
    -i  --id                <account_id>        Specified account ID to logout.

login options:
        --no-persist                            Do not keep login state.

query options:
        --account                               List logined accounts.
        --elect-platform                        List available course electing platform.
        --electable         <platform_id>       List available courses in specified electing platform.
        --elected           <platform_id>       List elected platform.

elect options:
    -I  --course-id         <course_id>         Course ID to elect.
    -d  --cancel            <course_id>         Cancel election of specified course.
    -P  --platform          <platform_id>       Specified platform.
    -f  --force                                 Force to Elect. (experimental)
"""

#    -c  --cash              <cash>              Cash to the course. If the specified course is elected, \n\
#                                                cashes will be alter.\n\
#        --semester                              List semesters.\n\
#        --course            <semester_id>       List courses of specified semester.\n\

WEEK_STR = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat' ,'Sun')

def GetAccountDatabaseDirectory():
    return os.environ['HOME']

def GetAccountDatabaseName():
    return '.uestc_eams'

def GetAccountDatabasePath():
    dir = GetAccountDatabaseDirectory()
    if dir[-1] != '/':
        return dir + '/' + GetAccountDatabaseName()
    return dir + GetAccountDatabaseName()

class AccountDatabase:
    
    def __init__(self, _db_path, _no_throw = False):
        self.__db_path = _db_path
        self.Exception = None
        self.NoThrow = _no_throw
        self.__conn = self.__connect_to(_db_path)

    def Throw(self):
        if(self.Exception):
            raise self.Exception

    def __connect_to(self, _db_path):
        conn = sqlite3.connect(_db_path)
        self.__ensure_integrailty(conn)
        return conn

    def __ensure_integrailty(self, conn):
        try:
            cur = conn.execute("SELECT name FROM sqlite_master where type=='table' and name=='Accounts'")
        except sqlite3.OperationError as s:
            self.Exception = s
            self.Throw()
            return None

        datas = cur.fetchall()
        cur.close()

        # Found Account table
        if len(datas) < 1:
            cur = conn.executescript("""
                    BEGIN EXCLUSIVE TRANSACTION;
                    
                    CREATE TABLE Accounts(
                        ID INTEGER PRIMARY KEY
                        , Username TEXT UNIQUE NOT NULL COLLATE NOCASE
                        , SessionObject BLOB NOT NULL);
                    COMMIT;
                """)
            cur.close()
            
    def GetSessionFromUsername(self, _username):
        if not isinstance(_username, str):
            raise TypeError('_username should be str.')

        cur = self.__conn.cursor()
        self.Exception = None
        try:
            cur.execute('SELECT * FROM Accounts where (Username == ?)', (_username,))
        except sqlite3.OperationError as s:
            self.Exception = s
            self.Throw()
            return (None, None)

        res = cur.fetchall()
        cur.close()
        
        if len(res) < 1:
            return (None, None)
        return (res[0][0], pickle.loads(res[0][2]))

    def GetSessionFromID(self, _id):
        if not isinstance(_id, int):
            raise TypeError('_id should be an integar.')

        cur = self.__conn.cursor()
        self.Exception = None
        try:
            cur.execute('SELECT Username, SessionObject FROM Accounts WHERE (ID == ?)', (_id,))
            res = cur.fetchall()
            cur.close()
        except sqlite3.OperationalError as s:
            self.Exception = s
            self.Throw()
            return (None, None)

        if len(res) < 1:
            return (None, None)
        return (res[0][0], pickle.loads(res[0][1]))
        

    def ListAll(self):
        cur = self.__conn.cursor()
        try:
            cur.execute('SELECT * FROM Accounts')
        except sqlite3.OperationError as s:
            self.Exception = s
            self.Throw()
            return None
        data = cur.fetchall()
        cur.close()
        return data

    def UpdateSessionByUsername(self, _username, _object):
        if not isinstance(_username, str):
            raise TypeError('_username should be str.')
        if not isinstance(_object, EAMSSession):
            raise TypeError('_object shoule be EAMSSession')

        raw = pickle.dumps(_object)
        cur = self.__conn.cursor()
        self.Exception = None
        try:
            cur.execute('UPDATE Accounts SET SessionObject=?  where (Username == ?)', (raw, _username))
            self.__conn.commit()
            cur.close()
        except sqlite3.OperationalError as s:
            self.Exception = s
            self.Throw()
            return False

        return True

    def SaveSession(self, _username, _object):
        if not isinstance(_username, str):
            raise TypeError('_username should be str.')
        if not isinstance(_object, EAMSSession):
            raise TypeError('_object shoule be EAMSSession')

        raw = pickle.dumps(_object)
        cur = self.__conn.cursor()
        self.Exception = None
        try:
            cur.execute('INSERT INTO Accounts(Username, SessionObject) VALUES (?, ?)' , (_username, raw))
            self.__conn.commit()
        except sqlite3.OperationalError as s:
            self.Exception = s
            self.Throw()
            return False
        return True

    def QueryIDByUsername(self, _username):
        if not isinstance(_username, str):
            raise TypeError('_username should be str.') 

        cur = self.__conn.cursor()
        self.Exception = None
        try:
            cur.execute('SELECT ID FROM Accounts where Username == ?' , (_username,))
        except sqlite3.OperationalError as s:
            self.Exception = s
            self.Throw()
            return False
        res = cur.fetchall()
        cur.close()
        if len(res) < 1:
            return None
        return res[0][0]

    def QueryUsernameByID(self, _id):
        if not isinstance(_id, int):
            raise TypeError('_id should be an integer.') 

        cur = self.__conn.cursor()
        self.Exception = None
        try:
            cur.execute('SELECT Username FROM Accounts where ID == ?', (_id,))
        except sqlite3.OperationalError as s:
            self.Exception = s
            self.Throw()
            return False
        res = cur.fetchall()
        cur.close()
        if len(res) < 1:
            return None
        return res[0][0]
        

    def DropSession(self, _username = None, _id = None):
        if _id and not isinstance(_id, int):
            raise('_id should be a integer')
            return False
        if _username and not isinstance(_username, str):
            raise('_username should be str.')
            return False

        if _id:
            if _username:
                username = self.QueryUsernameFromID(_id)
                if _id != username or not username:
                    return False
            cur = self.__conn.cursor()
            self.Exception = None
            try:
                cur.execute('DELETE FROM Accounts WHERE ID == ?', (_id,))
                self.__conn.commit()
            except sqlite3.OperationalError as s:
                self.Exception = s
                self.Throw()
                return False
        elif _username:
            cur = self.__conn.cursor()
            try:
                cur.execute('DELETE FROM Accounts WHERE Username == ?' , (_username,))
                self.__conn.commit()
            except sqlite3.OperationalError as s:
                self.Exception = s
                self.Throw()
                return False
        else:
            raise TypeError('_id or _username should be given.')
            return False
            
        return True
        

def TablePrint(_data, _limits, _margin):
    '''
        Print table line with specfied format.

        _data       line of data elements to print
        _limits     box size of elements
        _margin     margin between two boxes.
    '''
    if not isinstance(_data, list):
        if isinstance(_data, tuple):
            _data = list(_data)
        else:
            raise TypeError('_dict should be list or tuple')
    if not isinstance(_limits, list) and not isinstance(_limits, tuple):
        raise TypeError('_limits should be list or tuple')
    if len(_data) != len(_limits):
        raise ValueError('_limits should have same length with _dict.')

    idx_vec = [0 for i in range(0, len(_data))]
    len_vec = []
    #Convert all elements to string
    for idx in range(0, len(_data)):
        if str == type(_data[idx]):
            _data[idx] = '%s' % _data[idx]
        elif int == type(_data[idx]):
            _data[idx] = '%d' % _data[idx]
        else:
            raise TypeError('Unsupport element type: %s' % type(_data[idx]).__name__)
            return False
        len_vec.append(len(_data[idx]))

    end = False
    while not end:
        # loop for all elements
        end = True
        for idx in range(0, len(_data)):
            # element is fully printed. so just add padding
            if len_vec[idx] <= idx_vec[idx]:
                print(' '*(_limits[idx] + _margin[idx]), end = '')
                continue
            # calculate used spaces
            occup = 0 ; ldx = idx_vec[idx]; nidx = -1
            while occup < _limits[idx] and ldx < len_vec[idx]:
                # drawback : chinese character only
                cord = ord(_data[idx][ldx])
                if 0x4e00 < cord and cord < 0x9fa5:
                    if occup + 2 > _limits[idx]:
                        break
                    occup += 2
                elif _data[idx][ldx] == '\n':
                    nidx = ldx
                    break
                else:
                    occup += 1
                ldx += 1
            # If newline is found (\n), cut the string.
            if nidx != -1:
                print('%s' % _data[idx][idx_vec[idx]:nidx] + ' '*(_limits[idx] - occup), end = '')
                ldx = nidx + 1
            # If box cannot contain the remain part, cut and squeeze it to next line.
            else:
                print('%s' % _data[idx][idx_vec[idx]: ldx] + ' '*(_limits[idx] - occup), end = '')
            # loop until all elements are fully printed
            if ldx < len_vec[idx]:
                end = False
            idx_vec[idx] = ldx
            # pad with margin blanks
            print(' ' * _margin[idx], end = '')
        # next line
        print('')

    return True

class EAMSCommandShell:
    def __init__(self):
        self.__account_db_loaded = False
        self.__password = None
        self.__username = None
        self.__session = None
        self.__session_id = None
        pass

    def __load_account_database(self):
        if self.__account_db_loaded:
            return True
        try: 
            self.__account_db = AccountDatabase(GetAccountDatabasePath())
        except Exception as s:
            raise s
            return False

        # Don't throw exception
        self.__account_db.NoThrow = True

        return True

    
    def __login(self, _user, _password, _id = None, _db_first = True):
        # Firstly, check whether logined.
        if _id:
            username, session = self.__account_db.GetSessionFromID(_id)
            if not session:
                if self.__account_db.Exception:
                    return (ERR_DB, None, None)
                else:
                    return (ERR_PARAMS, None, None)
            return (ERR_OK, username, session)

        if _db_first:
            id, session = self.__account_db.GetSessionFromUsername(_user)
            if session:
                return (ERR_OK, id, session)

        # Try to login
        try:
            session = Login(self.__username, self.__password)
            if not session:
                return (ERR_NETWORK, None, None)
        except Exception as s:
            raise s
            return (ERR_NETWORK, None, None)

        return ERR_OK, None, session

    def __try_login(self):
        retval, id_user, session = self.__login(self.__username, self.__password, self.__id, _db_first = False)
        if retval == ERR_DB:
            print('Cannot account to database: ', end = '')
            print(self.__account_db.Exception)
            return ERR_DB
        elif retval == ERR_PARAMS:
            print('No session %d.' % self.__id)
            return ERR_PARAMS
        elif retval == ERR_NETWORK:
            print('Cannot login.')
            return ERR_NETWORK
        if id:
            print('Username : %s (ID : %d)' % (id_user, self.__id)) 
            self.__username = id_user
        else:
            print('Login successfully.')

        return retval, session

    def DoLogin(self, _arguments):
        long_opt = ['no-persist',  'password']
        self.__no_persist = False
        try:
            opts, extra = getopt.gnu_getopt(_arguments, 'p:', long_opt)
        except getopt.GetoptError as e:
            print(e)
            return ERR_PARAMS

        # Check account specified
        if len(extra) > 1:
            print('Too many accounts.')
            return ERR_PARAMS
        elif len(extra) == 0:
            print('Must specified an account.')
            return ERR_PARAMS
        self.__username = extra[0]

        # Other options
        for opt, val in opts:
            if opt == '-p' or opt == '--password':
                if len(val) == 0:
                    print('Password is too short.')
                    return ERR_PARAMS
                self.__password = val
            elif opt == '--no-persist':
                self.__no_persist = True
            else:
                print('Unknown option : %s' % opt)

        # Check account specified
        if not self.__password:
            print('Logging in with no password is not supported.')
            return ERR_PARAMS
        
        if not self.__load_account_database():
            print('Cannot access to account database.')
            return ERR_DB 

        # Login with the specified
        retval, id, session = self.__login(self.__username, self.__password)
        if id:
            print('User %s has logined. (ID : %d)' % (self.__username, id))
            return ERR_PARAMS
        if retval != ERR_OK:
            print('Cannot login.')
            return ret
        if self.__no_persist:
            print('Login successfully. State not saved.')
            return ERR_OK

        if not self.__account_db.SaveSession(self.__username, session):
            print('Failed to save session : ', end = '')
            print(self.__account_db.Exception)
            return ERR_DB

        # Check whether session is saved
        id = self.__account_db.QueryIDByUsername(self.__username)
        if id == None:
            print('Cannot save session : ', end = '')
            print(self.__account_db.Exception)
            return ERR_DB

        print('Login successfully. (ID : %d)' % id)

        return ERR_OK 
        
    def DoLogout(self, _arguments):
        long_opt = ['id']
        opts, extra = getopt.gnu_getopt(_arguments, 'i:', long_opt)

        self.__id = None
        for opt, val in opts:
            if opt == '--id' or opt == '-i':
                if not val:
                    print('option \'-i\' : Missing ID.')
                    return ERR_PARAMS
                try:
                    self.__id = int(val)
                except ValueError as s:
                    print('Illegal ID : %s.' % val)
                    return ERR_PARAMS

        if not self.__id and len(extra) < 1:
            print('Accounts missing.')
            return ERR_PARAMS

        if not self.__load_account_database():
            print('Cannot access to account database.')
            return ERR_DB

        if self.__id:
            username, session = self.__account_db.GetSessionFromID(self.__id)
            if not username:
                print('No account with ID %d' % self.__id)
            else:
                print('Logout %s' % username)
                if not self.__account_db.DropSession(_id = self.__id):
                    print('Failed : ', end = '')
                    print(self.__account_db.Exception)
                else:
                    session.Logout()
                

        for username in extra:
            id, session = self.__account_db.GetSessionFromUsername(username)
            if not id:
                print('No account %s' % username)
                continue

            if not self.__account_db.DropSession(_username = username):
                print('Failed at %s : ' % username, end = '')
                print(self.__account_db.Exception)
            else:
                print('%s Logouted.' % username)
                session.Logout()

        return ERR_OK

    def ListElectPlatform(self, _session):
        print('Available platform ID:')
        for name, interface in zip(_session.ElectCourse.Platform.keys(), _session.ElectCourse.Platform.values()):
            print(name)
        return ERR_OK

    def __print_elect_course_table(self, _list, _counts):
        limit = (6, 10, 7, 10, 8, 12, 15, 8, 8, 10, 20) 
        margin = (2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2)
        
        print('ID      Name        Credits  Count       Teachers  Type          Arrange          Exam      WeekHour  Campus      Remark')
        for course in _list:
        #for course in _filter(plat.Courses)
            teacher = ''
            arrange = ''
            for t in course['teachers']:
                teacher += t + '\n'
            for t in course['arrange']:
                arrange += '%s week %d-%d %s\n' % (WEEK_STR[t['day'] - 1], t['start'], t['end'], t['room'])
            this_count = _counts.get(int(course['id'])) 
            line = (
                course['id']
                , course['name'].strip()
                , '%.1f' % course['credits']
                , '-/-/-' if not this_count else '%d/%d/%d' % (this_count['current'], this_count['limit'] - this_count['current'], this_count['limit'])
                , teacher
                , course['type'].strip()
                , arrange
                , course['exam'].strip()
                , course['week_hour']
                , course['campus'].strip()
                , course['remark'].strip()
            )
            TablePrint(line, limit, margin)
        return ERR_OK

    def ListElectable(self, _plat):
        return self.__print_elect_course_table(_plat.Courses, _plat.Counts)

    def ListElected(self, _plat):
        elected = [course for course in [_plat.GetCourseByID(id) for id in _plat.Elected] if course]
        return self.__print_elect_course_table(elected, _plat.Counts)
        
    def ListAccounts(self):
        accounts = self.__account_db.ListAll()
        if accounts == None:
            print('Cannot access to database: ', end = '')
            return ERR_DB
        print('Session ID      Username')
        for account in accounts:
            print('%-14d %-15s' % (account[0], account[1]))
        return ERR_OK
            

    def DoList(self, _arguments):
        long_opt = ['account', 'semester', 'course', 'elect-platform', 'electable=', 'elected=', 'id=']
        opts, extra = getopt.gnu_getopt(_arguments, 'i:p:', long_opt)

        self.__list_semester = False
        self.__list_account = False
        self.__list_elect_platform = False
        self.__list_electable = False
        self.__list_course = False
        self.__password = None
        self.__username = None
        self.__id = None
        op_count = 0
        for opt, val in opts:
            if opt == '--account':
                self.__list_account = True
                op_count += 1
            elif opt == '--semester':
                self.__list_semester = True
                op_count += 1
            elif opt == '--elect-platform':
                self.__list_elect_platform = True
                op_count += 1
            elif opt == '--electable':
                self.__list_electable = True
                if not val:
                    print('Platform ID missing...')
                    return ERR_PARAMS
                else:
                    self.__platform_id = val
                op_count += 1
            elif opt == '--elected':
                self.__list_elected = True
                if not val:
                    print('Platform ID missing.')
                    return ERR_PARAMS
                else:
                    self.__platform_id = val
                op_count += 1
            elif opt == '--id' or opt == '-i':
                if not val:
                    print('option \'--id\' : ID value missing.')
                    return ERR_PARAMS
                else:
                    try:
                        self.__id = int(val)
                    except ValueError as s:
                        print('Illegal ID : %s.' % val)
                        return ERR_PARAMS
            elif opt == '-p' or opt == '--password':
                if not val:
                    print('option \'%s\' : password missing.' % opt)
                else:
                    self.__password = val
            else:
                print('Unknown options : %s' % opt)
                return ERR_PARAMS
        if op_count > 1:
            print('Too many query options.')
            return ERR_PARAMS

        if not self.__load_account_database():
            print('Cannot access to account database')
            return ERR_DB

        if self.__list_account:
            return self.ListAccounts()

        if len(extra) > 1:
            print('Too many accounts.')
            return ERR_PARAMS
        elif len(extra) > 0:
            self.__username = extra[0]
        if self.__id and self.__username:
            print('confilct : options for session %d and account %s' % (self.__id, self.__username))
            return ERR_PARAMS
        if not self.__id and not self.__username:
            print('Account missing.')
            return ERR_PARAMS

        if self.__username and not self.__password:
            print('password missing. (see \'--password\' or \'-p\')')
            return ERR_PARAMS

        # load session
        retval, session = self.__try_login()
        if retval != ERR_OK:
            return retvel

        if self.__list_semester:
            print('Support later.')
        else:
            if not session.ElectCourse.Opened:
                print('Course election is not opened.')
                return ERR_OK
            if self.__list_elect_platform:
                retval =  self.ListElectPlatform(session)
            else:
                plat = session.ElectCourse.Platform.get(self.__platform_id)
                if not plat:
                    print('Platform not found: %s' % self.__platform_id)
                print('Current platform: %s' % self.__platform_id)
                
                if self.__list_electable:
                    retval = self.ListElectable(plat)
                elif self.__list_elected:
                    retval = self.ListElected(plat)

        if retval != ERR_OK:
            return retval
        # if session is from account database, update it.
        if not id:
            if not self.__account_db.UpdateSessionByUsername(id_user, session):
                print('Cannot update session: ', end = '')
                print(self.__account_db.Exception)
        return ERR_OK


    def DoElect(self, _arguments):
        long_opt = ['course-id=', 'cancel', 'password=', 'id=', 'platform=', 'force']
        opts, extra = getopt.gnu_getopt(_arguments, 'i:p:I:P:f', long_opt)

        course_id = None
        force = False
        self.__password = None
        self.__username = None
        self.__id = None
        self.__cancel = False
        self.__platform_id = None
        for opt, val in opts:
            if opt == '--course-id' or opt == '-I':
                if not val:
                    print('missing Course ID for option \'%s\'' % opt)
                    return ERR_PARAMS
                try:
                    course_id = int(val)
                except ValueError as s:
                    print('Illegal ID : %s.' % val)
                    return ERR_PARAMS
            elif opt == '--password' or opt == '-p':
                if not val:
                    print('option \'%s\' : password missing.' % opt)
                else:
                    self.__password = val
            elif opt == '--cancel':
                self.__cancel = True
            elif opt == '--id' or opt == '-i':
                if not val:
                    print('option \'--id\' : ID value missing.')
                    return ERR_PARAMS
                else:
                    try:
                        self.__id = int(val)
                    except ValueError as s:
                        print('Illegal ID : %s.' % val)
                        return ERR_PARAMS
            elif opt == '--platform' or opt == '-P':
                if not val:
                    print('option \'--id\' : Platform missing.')
                    return ERR_PARAMS
                else:
                    self.__platform_id = val
            elif opt == '--force' or opt == '-f':
                force = True
            else:
                print('Unknown options : %s' % opt)

            if not self.__load_account_database():
                print('Cannot access to account database')
                return ERR_DB
           
        if len(extra) > 1:
            print('Too many accounts.')
            return ERR_PARAMS
        elif len(extra) > 0:
            self.__username = extra[0]
        if self.__id and self.__username:
            print('confilct : options for session %d and account %s' % (self.__id, self.__username))
            return ERR_PARAMS
        if not self.__id and not self.__username:
            print('Account missing.')
            return ERR_PARAMS

        if self.__username and not self.__password:
            print('password missing. (see \'--password\' or \'-p\')')
            return ERR_PARAMS

        if not self.__platform_id:
            print('Platform missing. (see \'--platform\' or \'-P\')')
            return ERR_PARAMS

        retval, session = self.__try_login()
        if retval != ERR_OK:
            return retvel

        plat = session.ElectCourse.Platform.get(self.__platform_id)
        if not plat:
            print('Platform not found : %s' % self.__platform_id)

        course = plat.GetCourseByID(course_id)
        if not course:
            print('Cannot found the course with ID %d.' % course_id)
            if not force:
                return ERR_PARAMS
        

        if self.__cancel:
            if not course:
                print('Cancel %d by force.' % course_id)
            else:
                print('Cancel %s (%d).' % (course['name'], course_id))
            result, message = plat.Elect(course_id, CANCEL)
        else:
            if not course:
                print('Elect %d by force.' % course_id)
            else:
                print('Elect %s (%d).' % (course['name'], course_id))
            result, message = plat.Elect(course_id, ELECT)

        if result:
            print('Succeed.')
        else:
            print('Failed : %s' % message)

        
        if not self.__account_db.UpdateSessionByUsername(self.__username, session):
            print('Cannot update state : ', end = '')
            print(self.__account_db.Exception)

        return ERR_OK

    def PrintHelp(self, _arguments):
        print(HELP_TEXT % _arguments[0])
        pass
        
    def Run(self, _arguments):
        len_arg = len(_arguments)
        if len_arg < 2:
            self.PrintHelp(_arguments)
            return ERR_OK

        if _arguments[1].lower() == 'login':
            return self.DoLogin(_arguments[2:])
        elif _arguments[1].lower() == 'logout':
            return self.DoLogout(_arguments[2:])
        elif _arguments[1].lower() == 'query':
            return self.DoList(_arguments[2:])
        elif _arguments[1].lower() == 'elect':
            return self.DoElect(_arguments[2:])
        else:
            self.PrintHelp(_arguments)
            print('Unknown command : %s' % _arguments[1])
            return 1
