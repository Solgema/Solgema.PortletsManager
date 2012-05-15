
/* Use onDOMLoad event to initialize kukit
   earlier then the document is fully loaded,
   but after the DOM is at its place already.
*/

kukit.solgema = {};

/* This check must not result in a javascript error, even if jq is
 * not present. Such an error would case all subsequent kss plugin
 * (this file and any other plugins that are loaded later)
 * fail to load.
 *
 * For this reason, it must be guarded by a condition.
 */
if (window.jq) {
    jq(function() {
        kukit.log('KSS started by jQuery DOMLoad event.');
        kukit.bootstrapFromDOMLoad();
    });
}

/* Base kukit plugins for Solgema.PortletsManager*/

kukit.actionsGlobalRegistry.register("solgema-initLeftPortletDragAndDrop",
    function(oper) {
    oper.evaluateParameters(['table', 'viewname'], {}, 'solgema-initLeftPortletDragAndDrop action');
    var table = oper.parms.table;
    var viewname = oper.parms.viewname;
    SPMLeftDnDReorder.table = jq(table);
    SPMLeftDnDReorder.tableid = table;
    SPMLeftDnDReorder.viewname = viewname;
    if (!SPMLeftDnDReorder.table.length)
        return;
    SPMLeftDnDReorder.rows = jq(table + " > div.managedPortlet");
     jq(table + " > div.managedPortlet > div > span > span.draggable")
        .not('.notDraggable')
        .mousedown(SPMLeftDnDReorder.doDown)
        .addClass("draggingHook")
        .html('::');
});
kukit.commandsGlobalRegistry.registerFromAction('solgema-initLeftPortletDragAndDrop',
    kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register("solgema-initRightPortletDragAndDrop",
    function(oper) {
    oper.evaluateParameters(['table', 'viewname'], {}, 'solgema-initRightPortletDragAndDrop action');
    var table = oper.parms.table;
    var viewname = oper.parms.viewname;
    SPMRightDnDReorder.table = jq(table);
    SPMRightDnDReorder.tableid = table;
    SPMRightDnDReorder.viewname = viewname;
viewname
    if (!SPMRightDnDReorder.table.length)
        return;
    SPMRightDnDReorder.rows = jq(table + " > div.managedPortlet");
     jq(table + " > div.managedPortlet > div > span > span.draggable")
        .not('.notDraggable')
        .mousedown(SPMRightDnDReorder.doDown)
        .addClass("draggingHook")
        .html('::');
});
kukit.commandsGlobalRegistry.registerFromAction('solgema-initRightPortletDragAndDrop',
    kukit.cr.makeSelectorCommand);
