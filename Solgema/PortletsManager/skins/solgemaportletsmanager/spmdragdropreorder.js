var SPMLeftDnDReorder = {};

SPMLeftDnDReorder.dragging = null;
SPMLeftDnDReorder.table = null;
SPMLeftDnDReorder.tableid = null;
SPMLeftDnDReorder.rows = null;
SPMLeftDnDReorder.viewname = null;

SPMLeftDnDReorder.doDown = function(e) {
    var dragging =  $(this).parents('.draggable:first');
    if (!dragging.length) return;
    dragging.mouseup(SPMLeftDnDReorder.doUp);
    SPMLeftDnDReorder.rows.mousemove(SPMLeftDnDReorder.doDrag);
    SPMLeftDnDReorder.dragging = dragging;
    dragging._position = SPMLeftDnDReorder.getPos(dragging);
    dragging.addClass("dragging");
    return false;
};

SPMLeftDnDReorder.getPos = function(node) {
    var pos = node.parent().children('.draggable').index(node[0]);
    return pos == -1 ? null : pos;
};

SPMLeftDnDReorder.doDrag = function(e) {
    var dragging = SPMLeftDnDReorder.dragging;
    if (!dragging) return;
    var target = this;
    if (!target) return;
    if ($(target).attr('id') != dragging.attr('id')) {
        SPMLeftDnDReorder.swapElements($(target), dragging);
    };
    return false;
};

SPMLeftDnDReorder.swapElements = function(child1, child2) {
    var parent = child1.parent();
    var items = parent.children('[id]');

    if (child1[0].swapNode) {
        // IE proprietary method
        child1[0].swapNode(child2[0]);
    } else {
        // swap the two elements, using a textnode as a position marker
        var t = parent[0].insertBefore(document.createTextNode(''),
                                       child1[0]);
        child1.insertBefore(child2);
        child2.insertBefore(t);
        $(t).remove();
    };

};

SPMLeftDnDReorder.doUp = function(e) {
    var dragging = SPMLeftDnDReorder.dragging;
    if (!dragging) return;
    dragging.unbind('mouseup', SPMLeftDnDReorder.doUp);
    dragging.removeClass("dragging");
    SPMLeftDnDReorder.updatePositionOnServer();
    dragging._position = null;
    try {
        delete dragging._position;
    } catch(e) {};
    dragging = null;
    SPMLeftDnDReorder.rows.unbind('mousemove', SPMLeftDnDReorder.doDrag);
    return false;
};

SPMLeftDnDReorder.updatePositionOnServer = function() {
    var dragging = SPMLeftDnDReorder.dragging;
    if (!dragging) return;

    var delta = SPMLeftDnDReorder.getPos(dragging) - dragging._position;

    if (delta == 0) {
        // nothing changed
        return;
    };
    // Strip off id prefix
    var args = {
        portlethash: dragging.attr('id').substr('portlet'.length)
    };
    args['viewname'] = SPMLeftDnDReorder.viewname;
    args['delta:int'] = delta;
    args['side'] = 'left';
    jQuery.post('spmMovePortletDelta', args)
};

var SPMRightDnDReorder = {};

SPMRightDnDReorder.dragging = null;
SPMRightDnDReorder.table = null;
SPMRightDnDReorder.tableid = null;
SPMRightDnDReorder.rows = null;
SPMRightDnDReorder.viewname = null;

SPMRightDnDReorder.doDown = function(e) {
    var dragging =  $(this).parents('.draggable:first');
    if (!dragging.length) return;
    dragging.mouseup(SPMRightDnDReorder.doUp);
    SPMRightDnDReorder.rows.mousemove(SPMRightDnDReorder.doDrag);
    SPMRightDnDReorder.dragging = dragging;
    dragging._position = SPMRightDnDReorder.getPos(dragging);
    dragging.addClass("dragging");
    return false;
};

SPMRightDnDReorder.getPos = function(node) {
    var pos = node.parent().children('.draggable').index(node[0]);
    return pos == -1 ? null : pos;
};

SPMRightDnDReorder.doDrag = function(e) {
    var dragging = SPMRightDnDReorder.dragging;
    if (!dragging) return;
    var target = this;
    if (!target) return;
    if ($(target).attr('id') != dragging.attr('id')) {
        SPMRightDnDReorder.swapElements($(target), dragging);
    };
    return false;
};

SPMRightDnDReorder.swapElements = function(child1, child2) {
    var parent = child1.parent();
    var items = parent.children('[id]');

    if (child1[0].swapNode) {
        // IE proprietary method
        child1[0].swapNode(child2[0]);
    } else {
        // swap the two elements, using a textnode as a position marker
        var t = parent[0].insertBefore(document.createTextNode(''),
                                       child1[0]);
        child1.insertBefore(child2);
        child2.insertBefore(t);
        $(t).remove();
    };

};

SPMRightDnDReorder.doUp = function(e) {
    var dragging = SPMRightDnDReorder.dragging;
    if (!dragging) return;
    dragging.unbind('mouseup', SPMRightDnDReorder.doUp);
    dragging.removeClass("dragging");
    SPMRightDnDReorder.updatePositionOnServer();
    dragging._position = null;
    try {
        delete dragging._position;
    } catch(e) {};
    dragging = null;
    SPMRightDnDReorder.rows.unbind('mousemove', SPMRightDnDReorder.doDrag);
//    reloadColumn();
    return false;
};

SPMRightDnDReorder.updatePositionOnServer = function() {
    var dragging = SPMRightDnDReorder.dragging;
    if (!dragging) return;

    var delta = SPMRightDnDReorder.getPos(dragging) - dragging._position;

    if (delta == 0) {
        // nothing changed
        return;
    };
    // Strip off id prefix
    var args = {
        portlethash: dragging.attr('id').substr('portlet'.length)
    };
    args['viewname'] = SPMRightDnDReorder.viewname;
    args['delta:int'] = delta;
    args['side'] = 'left';
    jQuery.post('spmMovePortletDelta', args)
};
