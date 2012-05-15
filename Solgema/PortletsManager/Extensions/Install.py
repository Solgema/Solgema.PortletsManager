from Products.CMFCore.utils import getToolByName
import transaction
from zope.component import getUtility, getAdapters, getMultiAdapter, getSiteManager
from plone.portlets.interfaces import IPortletManager

from zope.interface import Interface
from zope.component import getSiteManager
from plone.portlets.interfaces import IPortletManager, IPortletRetriever
from plone.app.portlets.exportimport.interfaces import IPortletAssignmentExportImportHandler

EXTENSION_PROFILES = ('Solgema.PortletsManager:default',)

def install(portal, reinstall=False):

    portal_quickinstaller = getToolByName(portal, 'portal_quickinstaller')
    portal_setup = getToolByName(portal, 'portal_setup')

    if not reinstall :
        leftColumn = getUtility(IPortletManager, name=u'plone.leftcolumn', context=portal)
        rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=portal)
        leftColumn.listAllManagedPortlets = []
        rightColumn.listAllManagedPortlets = []

    for extension_id in EXTENSION_PROFILES:
        portal_setup.runAllImportStepsFromProfile('profile-%s' % extension_id, purge_old=False)
        product_name = extension_id.split(':')[0]
        portal_quickinstaller.notifyInstalled(product_name)
        transaction.savepoint()

def uninstall(portal):
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-Solgema.PortletsManager:uninstall')
    leftColumn = getUtility(IPortletManager, name=u'plone.leftcolumn', context=portal)
    rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=portal)
    if hasattr(leftColumn, 'listAllManagedPortlets'): del leftColumn.listAllManagedPortlets
    if hasattr(rightColumn, 'listAllManagedPortlets'): del rightColumn.listAllManagedPortlets

    sm = getSiteManager(context=portal)
    sm.unregisterAdapter(required=(Interface, IPortletManager), provided=IPortletRetriever)
    sm.unregisterAdapter(required=(Interface,), provided=IPortletAssignmentExportImportHandler)

    return "Imported uninstall profile."


