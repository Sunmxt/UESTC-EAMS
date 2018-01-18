'''

    __init__.py for package uestc_eams

'''

'''
    URLs
'''
from .session import LoginIndex, AuthHost, PortalIndex, SubmenuIndex\
                    , ChildmenuIndex

'''
    Exceptions
'''
from .session import EAMSSessionException, EAMSLoginException\
                    , EAMSException

'''
    Session
'''
from .session import EAMSSession
from .session import Login



