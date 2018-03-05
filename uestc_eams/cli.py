'''

    Commandline interface to accessing UESTC EAMS system.


'''

import re
import os.path
import getopt
import sqlite3
from .session import Login


HELP_TEXT = ' \
Access to UESTC EAMS system. \
\
Usage: %s <command> [options]\

Command:\
    login       <account> [options]             Login with account.\
    logout                                      Logout.\
    list                                        List information\
    elect                                       Elect course.\
\
login options:\
        --no-persist                            Do not keep logined state.\
    -p  --password                              Specified account password.\
\
logout options:\
    -i  --id                                    Specified account ID to logout.\
\
list options:\
        --account                               List logined accounts.\
        --semester                              List semesters.\
        --course            <semester_id>       List courses of specified semester.\
        --elect-platform                        List available course electing platform.\
        --electable         <platform_id>       List available courses in specified electing platform.\
        --elected           <platform_id>       List elected platform.\
\
elect options:\
    -i  --id                <course_id>         Course ID to elect.\
    -c  --cash              <cash>              Cashes to the course. If the specified course is elected, \
                                                cashes will be alter.\
    -d  --cancel            <course_id>         Cancel election of specified course.\


'

def GetAccountDatabaseDirectory():
    return '/var/cache'

def GetAccountDatabaseName():
    return 'uestc_eams'

def GetAccountDatabasePath():
    dir = GetAccountDatabaseDirectory()
    if dir[-1] != '/':
        return dir + '/' + GetAccountDatabaseName()
    return dir + GetAccountDatabaseName()

def SQLBadStringCheck(_string):
    pass

class AccountDatabase:
    def __init__(self, _db_path):
        self.__db_path = _db_path
        self.__conn = sqlite3.connect(_db_path)
        self.__check_integrailty()

    def __connect_to(self, _db_path):
        not_need_init = os.path.exists(_db_path):

        conn = sqlite3.connect(_db_path)
        
        if not_need_init:
            __ensure_integrailty()
            return conn

        self.__init_account_table()
        return conn

    def __init_account_table(self):
        cur = self.__conn.cursor()
        cur.execute('CREATE TABLE Accounts(\
                    ID INTEGAR PRIMARY KEY
                    , Username TEXT NOT NULL COLLATE NOCASE
                    , SessionObject BLOB NOT NULL)
            ')
        self.__conn.commit()
        
            
    def __ensure_integrailty(self):
        cur = self.__conn.cursor()
        cur.execute('SELECT name FROM sqlite_master where type==\'table\' and \'name == \'Accounts\'')
        self.__conn.commit()
        datas = self.fetchall()
        # Found Account table
        if len(data) < 1:
            self.__init_account_table()

    def FromUsername(self, _username):
        if not isinstance(_username, str):
            raise TypeError('_username should be str.')
        if SQLBadStringCheck(_username):
            raise ValueError('Invailed user name.')

        cur = self.__conn.cursor()

        # WARNING : SQL INJECT.
        cur.execute('SELECT name FROM Accounts where (name == %s)' % _user_name)
        self.__conn.commit()
        return self.__conn.fetchall()

    def FromID(self, _id):
        if not isinstance(_id, int):
            raise TypeError('_id should be an integar.')

        cur = self.__conn.cursor()
        
        cur.execute('SELECT ID FROM Accounts where (id == %d)' % _id)
        self.__conn.commit()
        return self.__conn.fetchall()

    def UpdateByUsername(self, _username):
        if not isinstance(_username, str):
            raise TypeError('_username should be str.')
        if SQLBadStringCheck(_username):
            raise ValueError('Invailed user name.')

                
            

class EAMSCommandShell:
    def __init__(self):
        self.__account_db_loaded = False
        pass

    def __load_account_database(self):
        if self.__account_db_loaded:
            return True
        try: 
            self.__account_db = AccountDatabase(GetAccountDatabasePath())
        except Exception as s:
            raise s
            return False

        return True

    def DoLogin(self, _arguments):
        long_opt = ['no-persist',  'password']
        try:
            opts, extra = getopt.gnu_getopt(_arguments, 'p:', long_opt)
        except getopt.GetoptError as e:
            print(e)
            return 1

        # Check account specified
        if len(extra) > 1:
            print('Too many accounts.')
            return 1
        elif len(extra) == 0:
            print('Must specified an account.')
            return 1
        self.__username = extra[0]

        # Other options
        for opt, val in opts:
            if opt == '-p' or opt == '--password':
                if len(val) == 0:
                    print('Password is too short.')
                    return 1
                self.__password = val
            elif opt == '--no-persist':
                self.__no_persist = True
            else:
                print('Unknown option : %s' % opt)

        # Check password specified
        if not self.__password:
            print('Logging in with no password is not supported.')
        
        if not self.__load_account_database():
            print('Cannot access to account database.')
        # Check if account has logined.
        '
        ss, id = account_db.GetSessionByUsername()
        if ss:
            print(\'User %s has logined.\' % self.__username)
            print(\'ID is %d\' % id)
            return 1
        '

        # Login with the specified
        try:
            ss = Login(self.__username, self.__password)
            if not ss:
                print('Login Failed')
        except 
        
        
    def DoLogout(self, _arguments):
        pass

    def DoList(self, _arguments):
        pass

    def DoElect(self, _arguments):
        pass

    def PrintHelp(self, _arguments):
        pass
        
    def Run(self, _argments):
        len_arg = len(_argments)
        if len_arg < 2:
            self.PrintHelp(_argments)
            return 0

        if _arguments[1].lower() == 'login':
            return self.DoLogin(_arguments[1:])
        elif _arguments[1].lower() == 'logout':
            return self.DoLogout(_arguments[1:])
        elif _arguments[1].lower() == 'list':
            return self.DoList(_arguments[1:])
        elif _arguments[1].lower() == 'elect':
            return self.DoElect(_arguments[1:])
        else:
            self.PrintHelp(_arguments)
            print('Unknown command : %s' % _arguments[1])
            return 1
