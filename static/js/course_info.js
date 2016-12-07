/**
 * Created by xsx19 on 2016/12/6.
 */


function showCourseInfo(course) {
    if ('course_unread_notice' in course){
        showElem('communicate_holder');
        showElem('course_new_file_holder');
        showElem('course_unread_notice_holder');
        showElem('course_unsubmitted_operations_holder')
    }
    else{
        hideElem('communicate_holder');
        hideElem('course_new_file_holder');
        hideElem('course_unread_notice_holder');
        hideElem('course_unsubmitted_operations_holder');
    }
    list = ['course_id', 'course_name', 'course_time', 'course_week', 'course_new_file', 'course_teacher',
                'course_unread_notice', 'course_unsubmitted_operations', 'course_classroom'];

    var len = list.length;
    for(var i = 0;i < len;i++){
        if(list[i] in course){
            document.getElementById(list[i]).innerText = course[list[i]];
        }
        else{
            document.getElementById(list[i]).innerText = '——';
        }
    }
}