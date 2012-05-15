from zope.interface import implements
from zope.component import getUtility, getAdapters, getMultiAdapter
from Acquisition import aq_parent, aq_inner

from plone.app.kss.interfaces import IPloneKSSView
from plone.app.kss.plonekssview import PloneKSSView as basePloneKSSView

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletManagerRenderer
from plone.portlets.interfaces import IPortletAssignmentMapping
from Solgema.PortletsManager.interfaces import ISolgemaPortletManagerRetriever
from Solgema.PortletsManager.interfaces import ISolgemaPortletAssignment

from plone.portlets.utils import unhashPortletInfo
from plone.app.portlets.utils import assignment_mapping_from_key
from plone.app.portlets.interfaces import IPortletPermissionChecker

from plone.portlets.constants import USER_CATEGORY
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.constants import CONTENT_TYPE_CATEGORY
from plone.portlets.constants import CONTEXT_CATEGORY

class PortletManagerKSS(basePloneKSSView):
    """Opertions on portlets done using KSS
    """
    implements(IPloneKSSView)

    def spm_move_portlet_delta(self, portlethash, viewname, delta):
        portal_state = getMultiAdapter((self.context, self.context.REQUEST), name=u'plone_portal_state')
        portal = portal_state.portal()
        info = unhashPortletInfo(portlethash)
        manager = getUtility(IPortletManager, name=info['manager'], context=portal)
        listhashes = manager.listAllManagedPortlets
        retriever = getMultiAdapter((self.context, manager), ISolgemaPortletManagerRetriever)
        managedPortletsHashes = [a['hash'] for a in retriever.getManagedPortlets()]
        if portlethash in listhashes:
            hashBefore = managedPortletsHashes[managedPortletsHashes.index(portlethash)+delta]
            listhashes.remove(portlethash)
            listhashes.insert(listhashes.index(hashBefore), portlethash)
            manager.listAllManagedPortlets = listhashes
        else:
            manager.listAllManagedPortlets = listhashes.insert(delta,portlethash)
        self._render_column(info, viewname)
        return 'done'

    def spm_move_portlet_up(self, portlethash, viewname):
        info = unhashPortletInfo(portlethash)
        assignments = assignment_mapping_from_key(self.context, 
                        info['manager'], info['category'], info['key'])
        
        IPortletPermissionChecker(assignments.__of__(aq_inner(self.context)))()
        
        portal_state = getMultiAdapter((self.context, self.context.REQUEST), name=u'plone_portal_state')
        portal = portal_state.portal()
#        manager = getUtility(IPortletManager, name=info['manager'], context=portal)
        manager = getUtility(IPortletManager, name=info['manager'])
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

        return self._render_column(info, viewname)
        
        
    def spm_move_portlet_down(self, portlethash, viewname):
        info = unhashPortletInfo(portlethash)
        assignments = assignment_mapping_from_key(self.context, 
                        info['manager'], info['category'], info['key'])
        IPortletPermissionChecker(assignments.__of__(aq_inner(self.context)))()
        
        portal_state = getMultiAdapter((self.context, self.context.REQUEST), name=u'plone_portal_state')
        portal = portal_state.portal()
#        manager = getUtility(IPortletManager, name=info['manager'], context=portal)
        manager = getUtility(IPortletManager, name=info['manager'])
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

        return self._render_column(info, viewname)
        
    def spm_delete_portlet(self, portlethash, viewname):
        info = unhashPortletInfo(portlethash)
        assignments = assignment_mapping_from_key(self.context, 
                        info['manager'], info['category'], info['key'])
                        
        IPortletPermissionChecker(assignments.__of__(aq_inner(self.context)))()
        portal_state = getMultiAdapter((self.context, self.context.REQUEST), name=u'plone_portal_state')
        portal = portal_state.portal()
        manager = getUtility(IPortletManager, name=info['manager'], context=portal)
        listhashes = manager.listAllManagedPortlets
        del assignments[info['name']]
        listhashes.remove(portlethash)
        manager.listAllManagedPortlets = listhashes
        return self._render_column(info, viewname)

    def spm_stop_portlet(self, portlethash, viewname, hereurl):
        info = unhashPortletInfo(portlethash)
        assignments = assignment_mapping_from_key(self.context, 
                        info['manager'], info['category'], info['key'])
                        
        IPortletPermissionChecker(assignments.__of__(aq_inner(self.context)))()
        assigned = ISolgemaPortletAssignment(assignments[info['name']])
        if getattr(assigned, 'stopUrls', None) and len(getattr(assigned, 'stopUrls', [])) > 0:
            urls = assigned.stopUrls
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
            assigned.stopUrls = li
        else:
            assigned.stopUrls = [hereurl]
        return self._render_column(info, viewname)

    def spm_allow_portlet(self, portlethash, viewname, hereurl):
        info = unhashPortletInfo(portlethash)
        assignments = assignment_mapping_from_key(self.context, 
                        info['manager'], info['category'], info['key'])
                        
        IPortletPermissionChecker(assignments.__of__(aq_inner(self.context)))()
        li = []
        assigned = ISolgemaPortletAssignment(assignments[info['name']])
        if hasattr(assigned, 'stopUrls') and len(assigned.stopUrls) > 0:
            urls = assigned.stopUrls
            for url in urls:
                if url not in hereurl:
                    li.append(url)
        assigned.stopUrls = li
        return self._render_column(info, viewname)

    def spm_right_portlet(self, portlethash, viewname):
        portal_state = getMultiAdapter((self.context, self.context.REQUEST), name=u'plone_portal_state')
        portal = portal_state.portal()
        info = unhashPortletInfo(portlethash)

        assignments = assignment_mapping_from_key(self.context, 
                        info['manager'], info['category'], info['key'])
        IPortletPermissionChecker(assignments.__of__(aq_inner(self.context)))()

        if info['category'] == 'context':
            context = portal.restrictedTraverse(info['key'])
            rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=context)
            right = getMultiAdapter((context, rightColumn,), IPortletAssignmentMapping, context=context)
            right[info['name']] = assignments[info['name']]
        else:
            rightcolumn = getUtility(IPortletManager, name=u'plone.rightcolumn')
            leftcolumn = getUtility(IPortletManager, name=u'plone.leftcolumn')
            oldcategory = leftcolumn[ info['category'] ]
            oldstorage = oldcategory[ info['key'] ]
            portlet = oldstorage[ info['name'] ]
            newcategory = rightcolumn[ info['category'] ]
            newstorage = newcategory[ info['key'] ]
            newstorage[ info['name'] ] = portlet

        del assignments[info['name']]
        return self._render_both_column(info, viewname)

    def spm_left_portlet(self, portlethash, viewname):
        portal_state = getMultiAdapter((self.context, self.context.REQUEST), name=u'plone_portal_state')
        portal = portal_state.portal()
        info = unhashPortletInfo(portlethash)

        assignments = assignment_mapping_from_key(self.context, 
                        info['manager'], info['category'], info['key'])
        IPortletPermissionChecker(assignments.__of__(aq_inner(self.context)))()

        if info['category'] == 'context':
            context = portal.restrictedTraverse(info['key'])
            leftColumn = getUtility(IPortletManager, name=u'plone.leftcolumn', context=context)
            left = getMultiAdapter((context, leftColumn,), IPortletAssignmentMapping, context=context)
            left[info['name']] = assignments[info['name']]
        else:
            rightcolumn = getUtility(IPortletManager, name=u'plone.rightcolumn')
            leftcolumn = getUtility(IPortletManager, name=u'plone.leftcolumn')
            oldcategory = rightcolumn[ info['category'] ]
            oldstorage = oldcategory[ info['key'] ]
            portlet = oldstorage[ info['name'] ]
            newcategory = leftcolumn[ info['category'] ]
            newstorage = newcategory[ info['key'] ]
            newstorage[ info['name'] ] = portlet

        del assignments[info['name']]
        return self._render_both_column(info, viewname)
                
    def _render_column(self, info=None, viewname=None, portlethash=None):
        if portlethash:
            info = unhashPortletInfo(portlethash)
        ksscore = self.getCommandSet('core')
        selector = ksscore.getCssSelector('div#portletmanager-' + info['manager'].replace('.', '-'))
        context = aq_inner(self.context)
        request = aq_inner(self.request)
        view = getMultiAdapter((context, request), name=viewname)
        manager = getUtility(IPortletManager, name=info['manager'])
        
        request['key'] = info['key']
        
        request['viewname'] = viewname
        renderer = getMultiAdapter((context, request, view, manager,), IPortletManagerRenderer)
        renderer.update()
        ksscore.replaceInnerHTML(selector, renderer.__of__(context).render())
        return self.render()

    def _render_both_column(self, info, viewname):
        ksscore = self.getCommandSet('core')
        context = aq_inner(self.context)
        request = aq_inner(self.request)
        request['key'] = info['key']
        
        request['viewname'] = viewname
        view = getMultiAdapter((context, request), name=viewname)

        selectorA = ksscore.getCssSelector('div#portletmanager-plone-leftcolumn')
        managerA = getUtility(IPortletManager, name='plone.leftcolumn')
        rendererA = getMultiAdapter((context, request, view, managerA,), IPortletManagerRenderer)
        rendererA.update()
        ksscore.replaceInnerHTML(selectorA, rendererA.__of__(context).render())

        selectorB = ksscore.getCssSelector('div#portletmanager-plone-rightcolumn')
        managerB = getUtility(IPortletManager, name='plone.rightcolumn')
        rendererB = getMultiAdapter((context, request, view, managerB,), IPortletManagerRenderer)
        rendererB.update()
        ksscore.replaceInnerHTML(selectorB, rendererB.__of__(context).render())
        return self.render()
