'''

    __init__.py for package uestc_eams

'''

'''
    URLs
'''
from .base import LoginIndex, AuthHost, PortalIndex, SubmenuIndex\
                    , ChildmenuIndex, EAMSBaseUrl, ElectCourseUrl\
                    , ElectDefault, ElectStudentCount, ElectOperate\
                    , ELECT, CANCEL, CASH, CATCH, UNKNOWN

'''
    Exceptions
'''
from .base import EAMSSessionException, EAMSLoginException\
                    , EAMSException

'''
    Session
'''
from .session import EAMSSession
from .session import Login



