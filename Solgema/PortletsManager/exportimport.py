from plone.app.portlets.exportimport.portlets import PropertyPortletAssignmentExportImportHandler
from persistent.dict import PersistentDict
from Solgema.PortletsManager import ATTR

class SolgemaPortletAssignmentImportExportHandler(PropertyPortletAssignmentExportImportHandler):

    def import_stopUrls(self, node):
        try:
            stopUrls = node.getAttribute('stopUrls')
        except:
            return

        if not hasattr(self.assignment, ATTR):
            setattr(self.assignment, ATTR, PersistentDict())
        getattr(self.assignment, ATTR)['stopUrls'] = stopUrls

    def export_stopUrls(self, doc, node):
        stopUrls = getattr(self.assignment, ATTR, {}).get('stopUrls')
        if stopUrls is None:
            return
        node.setAttribute('stopUrls', stopUrls)

    def import_assignment(self, interface, node):
        self.import_stopUrls(node)
        PropertyPortletAssignmentExportImportHandler.import_assignment(self, interface, node)

    def export_assignment(self, interface, doc, node):
        self.export_stopUrls(doc, node)
        PropertyPortletAssignmentExportImportHandler.export_assignment(self, interface, doc, node)
