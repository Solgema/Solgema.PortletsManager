Changelog for Solgema.PortletsManager

    (name of developer listed in brackets)

Solgema.PortletsManager - 0.1 Unreleased

    - Initial package structure.
      [zopeskel]

Solgema.PortletsManager - 0.5.1b1 Released

    - First public release.

Solgema.PortletsManager - 0.5.1b2 Released

    - Solgema.PortletsManager.interfaces
      ISolgemaPortletsManagerLayer class based on IDefaultPloneLayer and not Interface.
      (allows to have the product running with other plone skins than the default one.)
    - css changes
    - manage-portlets view template changed
    - i18n updated
    - migrations added and registered
    - javascript to allow drop down of the portlets
    - replaced characters that weren't displayed on IE

Solgema.PortletsManager - 0.5.5 Released

    - Moved portlet manager renderer from portlets/configure.zcml to overrides.zcml (group, types and users portlet weren't editable)
      Unfortunately it's not possible to customize the portlet renderer because it is already overriden in plone.app.portlets

