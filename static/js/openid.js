/**
 * Created by guzhicheng on 12/13/16.
 */

(function() {
    window.getQueryParams = function(qs) {
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
        var openIdUrl = '/api/welcome/openid/';
        if(isAccountBind)
        {
            openIdUrl = '/api/welcome/userinfo/';
        }
        $.get(openIdUrl, {
            'code': getQueryParams(document.location.search).code
        }, function(data){
            next(data.data.open_id);
        });
    };
})();
