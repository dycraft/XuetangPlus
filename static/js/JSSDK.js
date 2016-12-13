/**
 * Created by guzhicheng on 12/13/16.
 */

function callJSSDK(List) {
    $.get('/api/jssdk', {'url': window.location.href}, function (data) {
        wx.config({
            debug: false, // 开启调试模式,调用的所有api的返回值会在客户端alert出来，若要查看传入的参数，可以在pc端打开，参数信息会通过log打出，仅在pc端时才会打印。
            appId: data.data.app_id, // 必填，公众号的唯一标识
            timestamp: data.data.timestamp, // 必填，生成签名的时间戳
            nonceStr: data.data.nonce_str, // 必填，生成签名的随机串
            signature: data.data.signature,// 必填，签名，见附录1
            jsApiList: List // 必填，需要使用的JS接口列表，所有JS接口列表见附录2
        });
    });
}
