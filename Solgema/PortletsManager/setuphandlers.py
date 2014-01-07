from StringIO import StringIO

from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.CMFEditions import StandardModifiers
from Products.CMFEditions.VersionPolicies import ATVersionOnEditPolicy

from AccessControl import ClassSecurityInfo
from zope.interface import implements
from Products.CMFCore import permissions   

from zope.component import getUtility, getAdapters
from zope.component import getMultiAdapter
from zope.component import getSiteManager

from plone.portlets.interfaces import IPortletManager
security = ClassSecurityInfo()

def setPortletInterface(portal, out):
    leftColumn = getUtility(IPortletManager, name=u'plone.leftcolumn', context=portal)
    rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=portal)

def setupSolgemaPortletsManager(context):
    """various things to do while installing..."""
    if context.readDataFile('spm_various.txt') is None:
        return
    site = context.getSite()
    jstool = getToolByName(site, 'portal_javascripts')
    jstool.cookResources()
    csstool = getToolByName(site, 'portal_css')
    csstool.cookResources()
    out = StringIO()
