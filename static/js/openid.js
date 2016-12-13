/**
 * Created by guzhicheng on 12/13/16.
 */

var current_open_id = '';

function getQueryParams(qs) {
    qs = qs.split('+').join(' ');
    var params = {},
        tokens,
        re = /[?&]?([^=]+)=([^&]*)/g;

    while (tokens = re.exec(qs)) {
        params[decodeURIComponent(tokens[1])] = decodeURIComponent(tokens[2]);
    }

    return params;
}

(function () {
    $.get('/api/openid/', {
        'code':getQueryParams(document.location.search).code
    }, function(data){
        current_open_id = data.data.openid;
    });
})();
