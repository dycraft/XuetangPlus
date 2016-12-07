/**
 * Created by xsx19 on 2016/12/6.
 */


function showNotification(data) {
    console.log(data);
    var informs = data['notices'], works = data['assignments'], documents = data['files'];
    var len = informs.length;
    var i, j;
    for(i = 0, j = 0;i < len;i++){
        if(informs[i]['state'] == '未读'){
            createInform('inform_list', 'javascript:void(0);', informs[i]['title'], informs[i]['content']);
            j++;
            if(j == 5){
                break;
            }
        }
    }
    len = works.length;
    for(i = 0, j = 0;i < len;i++){
        if(works[i]['processing']){
            //createInform('inform_list', 'javascript:void(0);', works[i]['title'], '');
            createWork('work_list', 'javascript:void(0);', works[i]['title'], works[i]['detail'].slice(0, 200) + '...');
            j++;
            if(j == 5){
                break;
            }
        }
    }
    len = documents.length;
    for(i = 0, j = 0;i < len;i++){
        if(documents[i]['state'] == 'new'){
            createDocument('document_list', documents[i]['download_url'], documents[i]['title'], documents[i]['size'],
                documents[i]['updating_time'], documents[i]['explanation']);
            j++;
            if(j == 5){
                break;
            }
        }
    }
}

function createInform(parentId, href, itemName, content) {
    var a = document.createElement('a');
    var div = document.createElement('div');
    var h4 = document.createElement('h4');
    var p = document.createElement('p');
    p.setAttribute('class', 'weui-media-box__desc');
    if(content == ''){
        p.innerText = '无作业内容';
    }
    else{
        p.innerText = content;
    }
    h4.setAttribute('class', 'weui-media-box__title');
    h4.innerText = itemName;
    div.setAttribute('class', 'weui-media-box__bd');
    a.setAttribute('class', 'weui-media-box weui-media-box_appmsg');
    a.href = href;
    div.appendChild(h4);
    div.appendChild(p);
    a.appendChild(div);
    document.getElementById(parentId).appendChild(a);
}

function createWork(parentId, href, itemName, content) {
    var a = document.createElement('a');
    var div = document.createElement('div');
    var h4 = document.createElement('h4');
    var p = document.createElement('p');
    p.setAttribute('class', 'weui-media-box__desc');
    if(content == ''){
        p.innerText = '无作业内容';
    }
    else{
        p.innerText = content;
    }
    h4.setAttribute('class', 'weui-media-box__title');
    h4.innerText = itemName;
    div.setAttribute('class', 'weui-media-box weui-media-box_text');
    a.setAttribute('class', 'weui-media-box weui-media-box_appmsg');
    a.href = href;
    div.appendChild(h4);
    div.appendChild(p);
    a.appendChild(div);
    document.getElementById(parentId).appendChild(a);
}

function createDocument(parentId, href, documentName, documentSize, documentDate, documentExplanation) {
    var a = document.createElement('a');
    var div = document.createElement('div');
    var h4 = document.createElement('h4');
    var ul = document.createElement('p');
    var li1 = document.createElement('li');
    var li2 = document.createElement('li');
    var li3 = document.createElement('li');
    ul.setAttribute('class', 'weui-media-box__info');
    li1.setAttribute('class', 'weui-media-box__info__meta');
    li1.innerText = documentSize;
    ul.appendChild(li1);
    li2.setAttribute('class', 'weui-media-box__info__meta');
    li2.innerText = documentDate;
    ul.appendChild(li2);
    li3.setAttribute('class', 'weui-media-box__info__meta weui-media-box__info__meta_extra');
    if(documentExplanation == ''){
        li3.innerText = '无说明';
    }
    else{
        li3.innerText = documentExplanation;
    }
    ul.appendChild(li3);

    h4.setAttribute('class', 'weui-media-box__title');
    h4.innerText = documentName;
    div.setAttribute('class', 'weui-media-box weui-media-box_text');
    a.setAttribute('class', 'weui-media-box weui-media-box_appmsg');
    a.href = href;
    div.appendChild(h4);
    div.appendChild(ul);
    a.appendChild(div);
    document.getElementById(parentId).appendChild(a);
}