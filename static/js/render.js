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

    window.getMobileOperatingSystem = function() {
        var userAgent = navigator.userAgent || navigator.vendor || window.opera;
         // Windows Phone must come first because its UA also contains "Android"
        if (/windows phone/i.test(userAgent)) {
            return "Windows Phone";
        }
        if (/android/i.test(userAgent)) {
            return "Android";
        }
        if (/iPad|iPhone|iPod/.test(userAgent) && !window.MSStream) {
            return "iOS";
        }
        return "unknown";
    };
})();
