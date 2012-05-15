import logging
from Products.CMFCore.utils import getToolByName

def doNothing(context):
    pass

def reinstall(context):
    portal_quickinstaller = getToolByName(context, 'portal_quickinstaller')
    portal_setup = getToolByName(context, 'portal_setup')
    portal_setup.runAllImportStepsFromProfile('profile-Solgema.PortletsManager:default')

def upgrade06(context):
    portal_quickinstaller = getToolByName(context, 'portal_quickinstaller')
    portal_setup = getToolByName(context, 'portal_setup')
    portal_setup.runAllImportStepsFromProfile('profile-Solgema.PortletsManager:upgrade06')
    jstool = getToolByName(context, 'portal_javascripts')
    jstool.cookResources()
    csstool = getToolByName(context, 'portal_css')
    csstool.cookResources()

