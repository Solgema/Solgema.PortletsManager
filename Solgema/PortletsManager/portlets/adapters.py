from zope.interface import implements
from Solgema.PortletsManager.interfaces import ISolgemaPortletAssignment
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase

from zope.annotation.attribute import AttributeAnnotations
from plone.app.portlets.portlets.base import Assignment

from Solgema.PortletsManager import options

try:
    from zope.annotation import IAnnotations
except ImportError:
    # BBB for Zope 2.9
    from zope.app.annotation import IAnnotations
from persistent.dict import PersistentDict
from persistent import Persistent

_marker = object()

SolgemaPortletAssignmentStorage = options.PersistentOptions.wire( "SolgemaPortletAssignmentStorage", "SolgemaPortletAssignment", ISolgemaPortletAssignment )

class SolgemaPortletAssignment(SolgemaPortletAssignmentStorage, AttributeAnnotations):

    implements(ISolgemaPortletAssignment)

    _storage = None

    def __init__(self, obj):
        self.obj = obj
        self.context = obj

    """
    @property
    def stopUrls(self):
        return getattr(self, '__stopUrls__', 'rataplan')

    def setStopUrls(self, value):
        self.__stopUrls__ = value
    """
