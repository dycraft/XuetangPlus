/**
 * Created with PyCharm.
 * User: Xsx
 * Date: 16-12-5
 * Time: 21:48
 */


function checkNotEmpty(input_id, hint) {
    input = document.getElementById(input_id)
    if (input.value.trim().length == 0) {
        input.setAttribute('placeholder', hint);
        return false;
    }
    return true;
}

function checkUsername() {
    return checkNotEmpty('id_username', '工号/学号不能为空');
}

function checkPassword() {
    return checkNotEmpty('id_password', '密码不能为空');
}

function submitValidation(openid, success, fail) {
    if (checkUsername() && checkPassword()) {
        var username = document.getElementById('id_username').value;
        var password = document.getElementById('id_password').value;
        var data = {openid: openid, username: username, password: password};
        api.post('/api/account/bind', data, success, fail);
        return true;
    }
    return false;
}

function showValidation(isValidated) {
    if (!isValidated) {
        hideElem('success_holder')
        showElem('validation_holder');
        document.getElementById('id_username').focus();
    }
    else {
        hideElem('validation_holder')
        showElem('success_holder');
    }
}