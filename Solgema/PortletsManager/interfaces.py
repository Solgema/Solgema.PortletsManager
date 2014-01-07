from zope.interface import Interface, Attribute
from plone.theme.interfaces import IDefaultPloneLayer
from zope.i18nmessageid import MessageFactory
from plone.portlets.interfaces import IPortletAssignment
from zope import schema
from config import _

class ISolgemaPortletsManagerLayer(IDefaultPloneLayer):
    """Solgema portlets manager layer""" 

class ISolgemaPortletManagerRetriever(Interface):
    """marker"""

class IPersistentOptions(Interface):
    """marker"""

class ISolgemaPortletAssignment(IPortletAssignment):
    """store stopped URLS"""

    stopUrls = schema.List(
        title = _(u'stopUrls', default="Urls to stop"),
        required = False,
        default=[],)
