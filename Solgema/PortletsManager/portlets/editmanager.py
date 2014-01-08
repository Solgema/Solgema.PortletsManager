import logging
from zope.interface import implements, Interface
from zope.component import adapts, getMultiAdapter, queryMultiAdapter, getUtility, getAdapters
from Acquisition import Explicit, aq_parent, aq_inner

from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.utils import hashPortletInfo

from plone.app.portlets.interfaces import IDashboard, IPortletPermissionChecker
from plone.app.portlets.browser.editmanager import ManagePortletAssignments as newManagePortletAssignments

from Solgema.PortletsManager.interfaces import ISolgemaPortletAssignment, ISolgemaPortletManagerRetriever

LOG = logging.getLogger('Solgema.PortletsManager')

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
        manager = getUtility(IPortletManager, name=managerid, context=portal)
        listhashes = manager.listAllManagedPortlets

        if portlethash in listhashes:
            hashBefore = listhashes.index(portlethash)
            listhashes.remove(portlethash)
            listhashes.insert(hashBefore - 1, portlethash)
            manager.listAllManagedPortlets = listhashes
        else:
            manager.listAllManagedPortlets = listhashes.insert(0, portlethash)
        
        self.request.response.redirect(self._nextUrl())
        return 'OK'
    
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
        manager = getUtility(IPortletManager, name=managerid, context=portal)
        listhashes = manager.listAllManagedPortlets

        if portlethash in listhashes:
            hashAfter = listhashes.index(portlethash)
            listhashes.remove(portlethash)
            listhashes.insert(hashAfter + 1, portlethash)
            manager.listAllManagedPortlets = listhashes
        else:
            manager.listAllManagedPortlets = listhashes.append(portlethash)
        
        self.request.response.redirect(self._nextUrl())
        return 'OK'

    def spm_move_portlet_delta(self, name='', position=None, manager=''):
        position = self.request.get('position', position)
        managerid = self.request.get('manager', manager)
        name = self.request.get('name', name)
        assignments = aq_inner(self.context)
        parent = aq_parent(aq_inner(self.context))

        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()
        basemanagerid = assignments.id.split('++')[-1]
        manager = None
        if managerid:
            managerid = managerid.replace('portletmanager-','').replace('-','.')
            if managerid != basemanagerid:
                try:
                    manager = getUtility(IPortletManager, name=managerid, context=portal)
                except:
                    pass
                if manager:
                    newColumn = getUtility(IPortletManager, name=managerid, context=parent)
                    new = getMultiAdapter((parent, newColumn,), IPortletAssignmentMapping, context=parent)
                    new[name] = assignments[name]
                    del assignments[name]
        if not manager:
            managerid = basemanagerid
            manager = getUtility(IPortletManager, name=managerid, context=portal)
        key = '/'.join(parent.getPhysicalPath())
        portlethash = hashPortletInfo(dict(manager=managerid, category=CONTEXT_CATEGORY, key=key, name=name,))
        listhashes = manager.listAllManagedPortlets
        retriever = getMultiAdapter((self.context, manager), ISolgemaPortletManagerRetriever)
        managedPortletsHashes = [a['hash'] for a in retriever.getManagedPortlets()]
        if portlethash in listhashes:
            listhashes.remove(portlethash)
            listhashes.insert(position, portlethash)
            manager.listAllManagedPortlets = listhashes
        else:
            manager.listAllManagedPortlets = listhashes.insert(position,portlethash)
        if position == None:
            self.request.response.redirect(self._nextUrl())
        return 'OK'

    # view @@delete-portlet
    def spm_delete_portlet(self, name):
        assignments = aq_inner(self.context)
        IPortletPermissionChecker(assignments)()
        managerid = assignments.id.split('++')[-1]

        parent = aq_parent(aq_inner(self.context))
        key = '/'.join(parent.getPhysicalPath())
        portlethash = hashPortletInfo(dict(manager=managerid, category=CONTEXT_CATEGORY, key=key, name=name,))
        
        portal_state = getMultiAdapter((self.context, self.context.REQUEST), name=u'plone_portal_state')
        portal = portal_state.portal()
        manager = getUtility(IPortletManager, name=managerid, context=portal)
        listhashes = manager.listAllManagedPortlets
        del assignments[name]
        listhashes.remove(portlethash)
        manager.listAllManagedPortlets = listhashes
        if not self.request.get('ajax'):
            self.request.response.redirect(self._nextUrl())
        return 'OK'

    def spm_right_portlet(self, name):
        portal_state = getMultiAdapter((self.context, self.context.REQUEST), name=u'plone_portal_state')
        portal = portal_state.portal()
        assignments = aq_inner(self.context)
        context = aq_parent(assignments)
        rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=context)
        right = getMultiAdapter((context, rightColumn,), IPortletAssignmentMapping, context=context)
        right[name] = assignments[name]
        del assignments[name]
        self.request.response.redirect(self._nextUrl())
        return 'OK'

    def spm_left_portlet(self, name):
        portal_state = getMultiAdapter((self.context, self.context.REQUEST), name=u'plone_portal_state')
        portal = portal_state.portal()
        assignments = aq_inner(self.context)
        context = aq_parent(assignments)
        leftColumn = getUtility(IPortletManager, name=u'plone.leftcolumn', context=context)
        left = getMultiAdapter((context, leftColumn,), IPortletAssignmentMapping, context=context)

        left[name] = assignments[name]
        del assignments[name]
        self.request.response.redirect(self._nextUrl())
        return 'OK'

    def spm_stop_portlet(self, name):
        hereurl = self.request.get('here_url', '')
        assignments = aq_inner(self.context)
        portlet = ISolgemaPortletAssignment(assignments[name])
        IPortletPermissionChecker(assignments)()
        if len(getattr(portlet, 'stopUrls', [])) > 0:
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
        if not self.request.get('ajax'):
            self.request.response.redirect(self._nextUrl())
        return 'OK'

    def spm_allow_portlet(self, name):
        hereurl = self.request.get('here_url', '')
        assignments = aq_inner(self.context) 
        portlet = ISolgemaPortletAssignment(assignments[name])
        IPortletPermissionChecker(assignments)()
        li = []
        if len(getattr(portlet, 'stopUrls', [])) > 0:
            urls = portlet.stopUrls
            for url in urls:
                if url not in hereurl:
                    li.append(url)
        portlet.stopUrls = li
        if not self.request.get('ajax'):
            self.request.response.redirect(self._nextUrl())
        return 'OK'

    def _nextUrl(self):
        referer = self.request.get('referer')
        if not referer:
            context = aq_parent(aq_inner(self.context))
            url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))    
            referer = '%s/@@manage-portlets' % (url,)
        return referer
