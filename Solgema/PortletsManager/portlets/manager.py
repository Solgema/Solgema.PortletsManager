import sys
from Acquisition import Explicit, aq_parent, aq_inner
from zope.component import adapts, getMultiAdapter, queryMultiAdapter, getUtility
from zope.interface import implements, Interface
from zope.annotation.interfaces import IAnnotations

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from zope.publisher.interfaces.browser import IBrowserView
from plone.app.portlets.interfaces import IColumn
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import ILocalPortletAssignable
from plone.portlets.interfaces import IPortletManagerRenderer
from plone.portlets.interfaces import IPortletContext
from plone.portlets.constants import CONTEXT_ASSIGNMENT_KEY
from plone.portlets.constants import CONTEXT_BLACKLIST_STATUS_KEY
from plone.portlets.constants import CONTEXT_CATEGORY, USER_CATEGORY, GROUP_CATEGORY, CONTENT_TYPE_CATEGORY
from plone.portlets.utils import hashPortletInfo
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.app.portlets.browser.editmanager import ContextualEditPortletManagerRenderer as baseContextualEditPortletManagerRenderer
from plone.app.portlets.browser.interfaces import IManageColumnPortletsView, IManageContextualPortletsView
from plone.app.portlets.utils import assignment_mapping_from_key
# import actual plone portlet views
from plone.app.portlets.manager import ColumnPortletManagerRenderer
from plone.app.portlets.manager import DashboardPortletManagerRenderer
from plone.app.portlets.browser.editmanager import EditPortletManagerRenderer
from plone.app.portlets.browser.editmanager import ContextualEditPortletManagerRenderer
from plone.app.portlets.browser.editmanager import DashboardEditPortletManagerRenderer

from plone.app.portlets.interfaces import IDashboard

from Solgema.PortletsManager.interfaces import ISolgemaPortletsManagerLayer, ISolgemaPortletAssignment
from Solgema.PortletsManager.interfaces import ISolgemaPortletManagerRetriever

class SolgemaColumnPortletManagerRenderer(ColumnPortletManagerRenderer):
#    implements(IPortletManagerRenderer)
#    adapts(Interface, ISolgemaPortletsManagerLayer, IBrowserView, IColumn)
    template = ViewPageTemplateFile('column.pt')

    def base_url(self):
        """If context is a default-page, return URL of folder, else
        return URL of context.
        """
        return str(getMultiAdapter((self.context, self.request,), name=u'absolute_url'))

class SolgemaPortletManagerRetriever(object):
    """The default portlet retriever.

    This will examine the context and its parents for contextual portlets,
    provided they provide ILocalPortletAssignable.
    """

    implements(ISolgemaPortletManagerRetriever)
    adapts(Interface, IPortletManager)

    def __init__(self, context, storage):
        self.context = context
        self.storage = storage

    def getManagedPortlets(self):
        """Work out which portlets to display, returning a list of dicts
        describing assignments to render.
        Bypass blacklist tests
        """
        portal_state = getMultiAdapter((self.context, self.context.REQUEST), name=u'plone_portal_state')
        portal = portal_state.portal()
        pcontext = IPortletContext(self.context, None)
        if pcontext is None:
            return []

        categories = [] 

        blacklisted = {}

        manager = self.storage.__name__

        current = self.context
        currentpc = pcontext
        blacklistFetched = set()
        parentsBlocked = False

        while current is not None and currentpc is not None:
            assignable = ILocalPortletAssignable(current, None)
            if assignable is not None:
                annotations = IAnnotations(assignable)
                local = annotations.get(CONTEXT_ASSIGNMENT_KEY, None)
                if local is not None:
                    localManager = local.get(manager, None)
                    if localManager is not None:
                        categories.extend([(CONTEXT_CATEGORY, currentpc.uid, a) for a in localManager.values()])
                    
            # Check the parent - if there is no parent, we will stop
            current = currentpc.getParent()
            if current is not None:
                currentpc = IPortletContext(current, None)
        
        # Get all global mappings for non-blacklisted categories
        
        for category, key in pcontext.globalPortletCategories(False):
            mapping = self.storage.get(category, None)
            if mapping is not None:
                for a in mapping.get(key, {}).values():
                    categories.append((category, key, a,))

        managerUtility = getUtility(IPortletManager, manager, portal)
        if not hasattr(managerUtility, 'listAllManagedPortlets'):
            managerUtility.listAllManagedPortlets = []

        hashlist = managerUtility.listAllManagedPortlets
        assignments = []
        for category, key, assignment in categories:
            portletHash = hashPortletInfo(dict(manager=manager, category=category, key=key, name =assignment.__name__,))
            if portletHash not in hashlist:
                hashlist.append(portletHash)
            assignments.append({'category'    : category,
                                'key'         : key,
                                'name'        : assignment.__name__,
                                'assignment'  : assignment,
                                'hash'        : portletHash,
                                'stopUrls'    : ISolgemaPortletAssignment(assignment).stopUrls,
                                'manager'     : manager,
                                })

        managerUtility.listAllManagedPortlets = hashlist

        #order the portlets
        assignments.sort(lambda a,b:cmp(hashlist.index(a['hash']), hashlist.index(b['hash'])))

        li = []
        here_url = '/'.join(aq_inner(self.context).getPhysicalPath())
        for assigndict in assignments:
            stopped = False
            if assigndict.has_key('stopUrls') and hasattr(assigndict['stopUrls'], 'sort') and len(assigndict['stopUrls'])>0:
                for stopUrl in assigndict['stopUrls']:
                    if stopUrl in here_url:
                        stopped = True
            assigndict['stopped'] = stopped
            assigndict['here_url'] = here_url

        return assignments

class ContextualEditPortletManagerRenderer(baseContextualEditPortletManagerRenderer):
    """Render a portlet manager in edit mode for contextual portlets
    """

#    implements(IPortletManagerRenderer)
    adapts(Interface, ISolgemaPortletsManagerLayer, IManageContextualPortletsView, IPortletManager)
    
    template = ViewPageTemplateFile('solgema-edit-manager-contextual.pt')

    def __init__(self, context, request, view, manager):
        super(ContextualEditPortletManagerRenderer, self).__init__(context, request, view, manager)

    def getIconFor(self, portletType):
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()
        portal_url = portal.absolute_url()
        plone_utils = getToolByName(self.context, 'plone_utils')
        if portletType not in [USER_CATEGORY,GROUP_CATEGORY,CONTENT_TYPE_CATEGORY]:
            return None
        icon = None
        if portletType == USER_CATEGORY:
            icon = plone_utils.getIconFor('controlpanel', 'MemberPrefs', None)
        if portletType == GROUP_CATEGORY:
            icon = plone_utils.getIconFor('controlpanel', 'UsersGroups', None)
        if portletType == CONTENT_TYPE_CATEGORY:
            icon = plone_utils.getIconFor('controlpanel', 'TypesSettings', None)
        if icon:
            return portal_url+'/'+icon
        else:
            return None
        
    def this_manager(self):
        return self.manager

    def this_manager_name_css(self):
        return self.manager.__name__.replace('.', '')

    def context_portlets_hash(self):
        return [a['hash'] for a in self.portlets()]

    def getRenderer(self):
        renderer = queryMultiAdapter((self.context, self.request, self, self.manager), IPortletManagerRenderer)
        if renderer is None:
            renderer = getMultiAdapter((self.context, self.request, self, self.manager), IPortletManagerRenderer)
        return renderer

    def getRetriever(self):
        retriever = queryMultiAdapter((self.context, self.manager), ISolgemaPortletManagerRetriever)
        if retriever is None:
            retriever = getMultiAdapter((self.context, self.manager), ISolgemaPortletManagerRetriever)
        return retriever
        
    def all_visible_portlets(self):
        """get herited portlets"""
        return self.getRenderer().portletsToShow()
        
    def visible_portlets_hash(self):
        return [a['hash'] for a in self.all_visible_portlets()]

    def context_baseUrl(self, rportlet_key, rportlet_category):
        return '%s/++%sportlets++%s' % (rportlet_key, rportlet_category, self.manager.__name__)
        
    def all_herited_portlets(self):
        """get herited portlets"""
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()
        manager = self.manager
        retriever = self.getRetriever()
        rportlets = retriever.getManagedPortlets()
        for rportlet in rportlets:
            name = rportlet['assignment'].__name__
            portlet_context = portal.restrictedTraverse(rportlet['key'][1:len(rportlet['key'])], default=None)
            editview = queryMultiAdapter((rportlet['assignment'], self.request), name='edit', default=None)
            if editview is None or rportlet['category'] != CONTEXT_CATEGORY:
                editviewName = ''
            else:
                editviewName = '%s/%s/edit' % (self.context_baseUrl(rportlet['key'], rportlet['category']), name)
            visibility = rportlet['hash'] in self.visible_portlets_hash() and 'portlet_visible' or 'portlet_hidden'
            visibility += rportlet['hash'] in self.context_portlets_hash() and ' portlet_here' or ''
            assignments = assignment_mapping_from_key(self.context, self.manager.__name__, rportlet['category'], rportlet['key'])
            rportlet['title'] = rportlet['assignment'].title
            rportlet['visibility'] = visibility
            rportlet['editview'] = editviewName
            rportlet['up_url'] = '%s/@@spm-move-portlet-up?name=%s' % (self.context_baseUrl(rportlet['key'], rportlet['category']), name)
            rportlet['down_url'] = '%s/@@spm-move-portlet-down?name=%s' % (self.context_baseUrl(rportlet['key'], rportlet['category']), name)
            rportlet['delete_url'] = '%s/@@spm-delete-portlet?name=%s' % (self.context_baseUrl(rportlet['key'], rportlet['category']), name)
            rportlet['stop_url'] = '%s/@@spm-stop-portlet?name=%s' % (self.context_baseUrl(rportlet['key'], rportlet['category']), name)
            rportlet['allow_url'] = '%s/@@spm-allow-portlet?name=%s' % (self.context_baseUrl(rportlet['key'], rportlet['category']), name)
            rportlet['left_url'] = '%s/@@spm-left-portlet?name=%s' % (self.context_baseUrl(rportlet['key'], rportlet['category']), name)
            rportlet['right_url'] = '%s/@@spm-right-portlet?name=%s' % (self.context_baseUrl(rportlet['key'], rportlet['category']), name)
            rportlet['canDelete'] = rportlet['category'] == CONTEXT_CATEGORY and True or False
            rportlet['manager_name'] = self.manager.__name__
        return rportlets
    
