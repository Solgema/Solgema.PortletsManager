domain=Solgema.PortletsManager
../../../../../bin/i18ndude rebuild-pot --pot $domain.pot --create $domain ../
../../../../../bin/i18ndude sync --pot $domain.pot */LC_MESSAGES/$domain.po
