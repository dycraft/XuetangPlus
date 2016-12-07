(function() {
    window.render = function(tpl_id, data) {
        $('#content').html(swig.render($('#tpl-'+tpl_id).html(), {locals: data}));
    };
})();
