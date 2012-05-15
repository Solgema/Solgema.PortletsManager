import sys
from Acquisition import Explicit, aq_parent, aq_inner
from zope.component import adapts, getMultiAdapter, queryMultiAdapter, getUtility, queryAdapter
from zope.interface import implements, Interface
from zope.annotation.interfaces import IAnnotations

from Products.CMFCore.utils import getToolByName

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import ILocalPortletAssignable
from plone.portlets.interfaces import IPortletContext
from plone.portlets.constants import CONTEXT_ASSIGNMENT_KEY
from plone.portlets.constants import CONTEXT_BLACKLIST_STATUS_KEY
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.utils import hashPortletInfo
from plone.portlets.retriever import PortletRetriever as basePortletRetriever
from plone.memoize.instance import memoize

from Solgema.PortletsManager.interfaces import ISolgemaPortletAssignment

class SolgemaPortletRetriever(basePortletRetriever):
    """The Solgema portlet retriever.

    It does the same job as the standard retriver but orders the portlets from
    a list stored in the attribute 'listAllManagedPortlets' of the IPortletManager utility
    """

    def getPortlets(self):

        portal_state = getMultiAdapter((self.context, self.context.REQUEST), name=u'plone_portal_state')
        portal = portal_state.portal()
        pcontext = IPortletContext(self.context, None)
        if pcontext is None:
            return []

        categories = [] 

        blacklisted = {}

        manager = self.storage.__name__

        for category, key in pcontext.globalPortletCategories(False):
            blacklisted[category] = None

        current = self.context
        currentpc = pcontext
        blacklistFetched = set()
        parentsBlocked = False
        
        while current is not None and currentpc is not None:
            if ILocalPortletAssignable.providedBy(current):
                assignable = current
            else:
                assignable = queryAdapter(current, ILocalPortletAssignable)

            if assignable is not None:
                if IAnnotations.providedBy(assignable):
                    annotations = assignable
                else:
                    annotations = queryAdapter(assignable, IAnnotations)
                
                if not parentsBlocked:
                    local = annotations.get(CONTEXT_ASSIGNMENT_KEY, None)
                    if local is not None:
                        localManager = local.get(manager, None)
                        if localManager is not None:
                            categories.extend([(CONTEXT_CATEGORY, currentpc.uid, a) for a in localManager.values()])

                blacklistStatus = annotations.get(CONTEXT_BLACKLIST_STATUS_KEY, {}).get(manager, None)
                if blacklistStatus is not None:
                    for cat, status in blacklistStatus.items():
                        if cat == CONTEXT_CATEGORY:
                            if not parentsBlocked and status == True:
                                parentsBlocked = True
                        else: # global portlet categories
                            if blacklisted.get(cat, False) is None:
                                blacklisted[cat] = status
                            if status is not None:
                                blacklistFetched.add(cat)

            if parentsBlocked and len(blacklistFetched) == len(blacklisted):
                break
            current = currentpc.getParent()
            if current is not None:
                if IPortletContext.providedBy(current):
                    currentpc = current
                else:
                    currentpc = queryAdapter(current, IPortletContext)

        for category, key in pcontext.globalPortletCategories(False):
            if not blacklisted[category]:
                mapping = self.storage.get(category, None)
                if mapping is not None:
                    for a in mapping.get(key, {}).values():
                        categories.append((category, key, a,))

        managerUtility = getUtility(IPortletManager, manager, portal)

        here_url = '/'.join(aq_inner(self.context).getPhysicalPath())

        assignments = []
        for category, key, assignment in categories:
            assigned = ISolgemaPortletAssignment(assignment)
            portletHash = hashPortletInfo(dict(manager=manager, category=category, key=key, name =assignment.__name__,))
            if not getattr(assigned, 'stopUrls', False) or len([stopUrl for stopUrl in getattr(assigned, 'stopUrls', []) if stopUrl in here_url])==0:
                assignments.append({'category'    : category,
                                    'key'         : key,
                                    'name'        : assignment.__name__,
                                    'assignment'  : assignment,
                                    'hash'        : hashPortletInfo(dict(manager=manager, category=category, key=key, name =assignment.__name__,)),
                                    'stopUrls'    : ISolgemaPortletAssignment(assignment).stopUrls,
                                    })
        
        if hasattr(managerUtility, 'listAllManagedPortlets'):
            hashlist = managerUtility.listAllManagedPortlets
            assignments.sort(lambda a,b:cmp(hashlist.count(a['hash'])>0 and hashlist.index(a['hash']) or 0, hashlist.count(b['hash'])>0 and hashlist.index(b['hash']) or 0))

        return assignments
