/**
 * Created by xsx19 on 2016/12/6.
 */

function showBind(isBinded) {
    if (!isBinded) {
        hideElem('my_course_holder')
        showElem('unbind_error_holder');
    }
    else {
        hideElem('unbind_error_holder')
        showElem('my_course_holder');
    }
}

function loadsCourses(courseList){
    var result = {  1:  [],
                    2:  [],
                    3:  [],
                    4:  [],
                    5:  [],
                    6:  [],
                    7:  []};
    var len = courseList.length;
    var i;
    for (i = 0;i < len;i++){
        result[courseList[i]['课程星期']].push(courseList[i]);
    }
    return result;
}

function showCourses(courseDic) {
    var i, j;
    dic = { 1:  'monday',
            2:  'tuesday',
            3:  'wednesday',
            4:  'thursday',
            5:  'friday',
            6:  'saturday',
            7:  'sunday'};
    for (i = 1;i < 8;i++){
        var len = courseDic[i].length;
        if(len == 0){
            //createCourse(dic[i] + '_courses', 'javascript:void(0);', '课程名称', '课程时间');
            hideElem(dic[i])
        }
        else{
            for(j = 0;j < len;j++){
                createCourse(dic[i] + '_courses', origin + '/learn/course_info?openid=' + urlParam.openid + '&course_id=' + courseDic[i][j]['课程代号'], courseDic[i][j]['课程名称'], courseDic[i][j]['课程时间']);
            }
        }
    }
}

function createCourse(parentId, href, courseName, courseTime) {
    var a = document.createElement('a');
    var div = document.createElement('div');
    var h4 = document.createElement('h4');
    var p = document.createElement('p');
    p.setAttribute('class', 'weui-media-box__desc');
    p.innerText = courseTime;
    h4.setAttribute('class', 'weui-media-box__title');
    h4.innerText = courseName;
    div.setAttribute('class', 'weui-media-box__bd');
    a.setAttribute('class', 'weui-media-box weui-media-box_appmsg');
    a.href = href;
    div.appendChild(h4);
    div.appendChild(p);
    a.appendChild(div);
    document.getElementById(parentId).appendChild(a);
}