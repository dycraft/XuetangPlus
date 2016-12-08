(function() {
    window.render = function(tpl_id, data) {
        $('#content').html(swig.render($('#tpl-'+tpl_id).html(), {locals: data}));
    };

    window.showToolTips = function(tips_id) {
        var $tooltips = $('#'+tips_id);
        if ($tooltips.css('display') != 'none') return;
        $('.page.cell').removeClass('slideIn');
        $tooltips.css('display', 'block');
        setTimeout(function() {
            $tooltips.css('display', 'none');
        }, 2000);
    };
})();
