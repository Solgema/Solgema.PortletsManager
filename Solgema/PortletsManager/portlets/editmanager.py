from zope.interface import implements, Interface
from zope.component import adapts, getMultiAdapter, queryMultiAdapter, getUtility, getAdapters
from Acquisition import Explicit, aq_parent, aq_inner

from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.utils import hashPortletInfo

from plone.app.portlets.interfaces import IDashboard, IPortletPermissionChecker
from plone.app.portlets.browser.editmanager import ManagePortletAssignments as newManagePortletAssignments

from Solgema.PortletsManager.interfaces import ISolgemaPortletAssignment

class ManagePortletAssignments(newManagePortletAssignments):
    """Utility views for managing portlets for a particular column
    """

    # view @@move-portlet-up
    def spm_move_portlet_up(self, name):
        assignments = aq_inner(self.context)
        IPortletPermissionChecker(assignments)()
        managerid = assignments.id.split('++')[-1]

        parent = aq_parent(aq_inner(self.context))
        key = '/'.join(parent.getPhysicalPath())
        portlethash = hashPortletInfo(dict(manager=managerid, category=CONTEXT_CATEGORY, key=key, name=name,))

        portal_state = getMultiAdapter((self.context, self.context.REQUEST), name=u'plone_portal_state')
        portal = portal_state.portal()
        manager = getUtility(IPortletManager, name=u'plone.rightcolumn', context=portal)
        listhashes = manager.listAllManagedPortlets
        retriever = getMultiAdapter((self.context, manager), ISolgemaPortletManagerRetriever)
        managedPortletsHashes = [a['hash'] for a in retriever.getManagedPortlets()]

        if portlethash in listhashes:
            hashBefore = managedPortletsHashes[managedPortletsHashes.index(portlethash)-1]
            listhashes.remove(portlethash)
            listhashes.insert(listhashes.index(hashBefore), portlethash)
            manager.listAllManagedPortlets = listhashes
        else:
            manager.listAllManagedPortlets = listhashes.insert(0,portlethash)
        
        self.request.response.redirect(self._nextUrl())
        return ''
    
    # view @@move-portlet-down
    def spm_move_portlet_down(self, name):
        assignments = aq_inner(self.context)
        IPortletPermissionChecker(assignments)()
        managerid = assignments.id.split('++')[-1]

        parent = aq_parent(aq_inner(self.context))
        key = '/'.join(parent.getPhysicalPath())
        portlethash = hashPortletInfo(dict(manager=managerid, category=CONTEXT_CATEGORY, key=key, name=name,))

        portal_state = getMultiAdapter((self.context, self.context.REQUEST), name=u'plone_portal_state')
        portal = portal_state.portal()
        manager = getUtility(IPortletManager, name=u'plone.rightcolumn', context=portal)
        listhashes = manager.listAllManagedPortlets
        retriever = getMultiAdapter((self.context, manager), ISolgemaPortletManagerRetriever)
        managedPortletsHashes = [a['hash'] for a in retriever.getManagedPortlets()]

        if portlethash in listhashes:
            hashAfter = managedPortletsHashes[managedPortletsHashes.index(portlethash)+1]
            listhashes.remove(portlethash)
            listhashes.insert(listhashes.index(hashAfter)+1, portlethash)
            manager.listAllManagedPortlets = listhashes
        else:
            manager.listAllManagedPortlets = listhashes.append(portlethash)
        
        self.request.response.redirect(self._nextUrl())
        return ''
    
    # view @@delete-portlet
    def spm_delete_portlet(self, name):
        assignments = aq_inner(self.context)
        IPortletPermissionChecker(assignments)()
        portal_state = getMultiAdapter((self.context, self.context.REQUEST), name=u'plone_portal_state')
        portal = portal_state.portal()
        manager = getUtility(IPortletManager, name=u'plone.rightcolumn', context=portal)
        listhashes = manager.listAllManagedPortlets
        del assignments[name]
        listhashes.remove(portlethash)
        manager.listAllManagedPortlets = listhashes
        self.request.response.redirect(self._nextUrl())
        return ''

    def spm_right_portlet(self, name):
        portal_state = getMultiAdapter((self.context, self.context.REQUEST), name=u'plone_portal_state')
        portal = portal_state.portal()
        assignments = aq_inner(self.context) 
        context = portal.restrictedTraverse(assignments.absolute_url(relative=1))
        rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=context)
        right = getMultiAdapter((context, rightColumn,), IPortletAssignmentMapping, context=context)
        right[name] = assignments[name]
        del assignments[name]
        self.request.response.redirect(self._nextUrl())
        return ''

    def spm_left_portlet(self, name):
        portal_state = getMultiAdapter((self.context, self.context.REQUEST), name=u'plone_portal_state')
        portal = portal_state.portal()
        assignments = aq_inner(self.context)
        context = portal.restrictedTraverse(assignments.absolute_url(relative=1))
        leftColumn = getUtility(IPortletManager, name=u'plone.leftcolumn', context=context)
        left = getMultiAdapter((context, leftColumn,), IPortletAssignmentMapping, context=context)

        left[name] = assignments[name]
        del assignments[name]
        self.request.response.redirect(self._nextUrl())
        return ''
    """
    def spm_stop_portlet(self, name):
        hereurl = self.request.get('here_url', '')
        assignments = aq_inner(self.context)
        IPortletPermissionChecker(assignments)()
        if hasattr(assignments[name], 'stopUrls') and len(assignments[name].stopUrls) > 0:
            urls = assignments[name].stopUrls
            li = []
            added = False
            for url in urls:
                if hereurl in url and not added:
                    li.append(hereurl)
                    added = True
                else:
                    li.append(url)
            if not added:
                li.append(hereurl)
            assignments[name].stopUrls = li
        else:
            assignments[name].stopUrls = [hereurl]

        self.request.response.redirect(self._nextUrl())
        return ''

    def spm_allow_portlet(self, name):
        hereurl = self.request.get('here_url', '')
        assignments = aq_inner(self.context) 
        IPortletPermissionChecker(assignments)()

        li = []
        if hasattr(assignments[name], 'stopUrls') and len(assignments[name].stopUrls) > 0:
            urls = assignments[name].stopUrls
            for url in urls:
                if url not in hereurl:
                    li.append(url)
        assignments[name].stopUrls = li

        self.request.response.redirect(self._nextUrl())
        return ''
    """

    def spm_stop_portlet(self, name):
        hereurl = self.request.get('here_url', '')
        assignments = aq_inner(self.context)
        portlet = ISolgemaPortletAssignment(assignments[name])
        return portlet
        IPortletPermissionChecker(assignments)()
        if len(portlet.stopUrls) > 0:
            urls = portlet.stopUrls
            li = []
            added = False
            for url in urls:
                if hereurl in url and not added:
                    li.append(hereurl)
                    added = True
                else:
                    li.append(url)
            if not added:
                li.append(hereurl)
            portlet.stopUrls = li
        else:
            portlet.stopUrls = [hereurl]
        return portlet.stopUrls
        self.request.response.redirect(self._nextUrl())
        return ''

    def spm_allow_portlet(self, name):
        hereurl = self.request.get('here_url', '')
        assignments = aq_inner(self.context) 
        portlet = ISolgemaPortletAssignment(assignments[name])
        return portlet
        IPortletPermissionChecker(assignments)()
        li = []
        if hasattr(portlet, 'stopUrls') and len(portlet.stopUrls) > 0:
            urls = portlet.stopUrls
            for url in urls:
                if url not in hereurl:
                    li.append(url)
        portlet.stopUrls = ['ergerg']
        return portlet.stopUrls
        self.request.response.redirect(self._nextUrl())
        return ''

    def _nextUrl(self):
        referer = self.request.get('referer')
        if not referer:
            context = aq_parent(aq_inner(self.context))
            url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))    
            referer = '%s/@@manage-portlets' % (url,)
        return referer
