/**
 * Created by guzhicheng on 12/13/16.
 */

(function() {
    var getQueryParams = function(qs) {
        qs = qs.split('+').join(' ');
        var params = {},
            tokens,
            re = /[?&]?([^=]+)=([^&]*)/g;
        while ((tokens = re.exec(qs))) {
            params[decodeURIComponent(tokens[1])] = decodeURIComponent(tokens[2]);
        }
        return params;
    };

    window.getOpenId = function(next) {
        $.get('/api/welcome/openid/', {
            'code': getQueryParams(document.location.search).code
        }, function(data){
            next(data.data.open_id);
        });
    };
})();
