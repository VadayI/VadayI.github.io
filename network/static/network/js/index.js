let filter = null
let current_page = 1

document.addEventListener('DOMContentLoaded', () => {
    const new_post_form = document.querySelector('#new_post_form');
    generate_post_list();  
})

function add_new_post() {
    var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    var title = document.querySelector('#new_post_title').value
    var content = document.querySelector('#new_post_content').value
    let data = new FormData();
    data.append('new_post_title', title)
    data.append('new_post_content', content)
    data.append('csrfmiddlewaretoken', csrftoken)
    fetch('add_post', {
        method: 'POST',
        body: data,
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then();
    location.href=""
}

async function get_posts() {
    var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    let data = new FormData();
    data.append('filter', filter)
    data.append('page_number', current_page)
    data.append('csrfmiddlewaretoken', csrftoken)
    try {
        const response = await fetch('get_posts', {
                                                    method: 'POST',
                                                    body: data
                                                });
        const post_list = await response.json();
        filter = filter
        current_page = post_list['current_page']

        if (current_page <= 1) document.querySelector('#previous_page').style.display = 'none'
        else document.querySelector('#previous_page').style.display = 'block'
    
        if (current_page == post_list['last_page']) document.querySelector('#next_page').style.display = 'none'
        else document.querySelector('#next_page').style.display = 'block'

        return post_list['posts'];
    } catch (error) {
        console.error(error);
    }
}

async function generate_post_list() {

    document.querySelectorAll('div.post').forEach(post => {
        post.remove();
    })

    document.querySelector('#new_post').style.display = 'block'
    const user_id = JSON.parse(document.getElementById("user_id").textContent);

    posts = await get_posts(); 
    for (const post of posts) {
        let edit_tag = ''
        if (post['author_id'] == user_id) {
            edit_tag = `<p><button onclick="edit_post(${post['id']})" class="pe-auto text-primary">Edit</button></p>`
        }
            
        d = new Date(post['modificate_date']);
        let post_element = document.createElement('div');
        post_element.className = 'post bg-light border rounded-3 pl-1'
        post_element.id = post['id']
        post_element.setAttribute('data-author_id', post['author_id'])
        post_element.innerHTML = `<h3>${post['title']}</h3> ${edit_tag}<div class="text_content" data-post_id=${post['id']}><p class='post_content text-justify lh-base m-1' data-post_id=${post['id']}>${post['content']}</p></div><p><a href="profile?id=${post['author_id']}" class="pe-auto text-primary">${post['author']}</a></p><div class='mb-1 text-muted'>${formatDate(d)}</div><i class="btn_like btn fas fa-heart" data-post_id=${post['id']} style="color: red" onclick ='liking(${post['id']})'>${post['likes_number']}</i><hr>`
        post_element.innerHTML = post_element.innerHTML.replace(/\n/g, '<br />');
        document.querySelector('#posts').append(post_element)
    }
}

function formatDate(date) {
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var ampm = hours >= 12 ? 'pm' : 'am';
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    minutes = minutes < 10 ? '0'+minutes : minutes;
    var strTime = hours + ':' + minutes + ' ' + ampm;
    return (date.getMonth()+1) + "/" + date.getDate() + "/" + date.getFullYear() + "  " + strTime;
  }
  
async function following(follow_user_id, followers_count) {
    var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    let data = new FormData();
    data.append('follow_user_id', follow_user_id)
    data.append('csrfmiddlewaretoken', csrftoken)
    try {
        const response = await fetch('following', {
            method: 'POST',
            body: data
        });
        const result = await response.json();
        document.querySelector('#followers_count').innerHTML = `Followers: ${result['followers_count']}`
        if (result['followers_count'] > followers_count) {
            document.querySelector('#unfollowing_btn').style.display = 'block'
            document.querySelector('#follow_btn').style.display = 'none'
        }
        else {
            document.querySelector('#unfollowing_btn').style.display = 'none'
            document.querySelector('#follow_btn').style.display = 'block'
        }
    } catch (error) {
        console.log(error);
    }
}

async function liking(post_id) {
    var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    let data = new FormData();
    data.append('post_id', post_id)
    data.append('csrfmiddlewaretoken', csrftoken)

    await fetch('liking', {
        method: 'POST',
        body: data,
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data['valid']) {
            document.querySelector(`i.btn_like[data-post_id="${post_id}"]`).innerHTML = data['likes_number']
        }
    });
}

async function following_users_posts() {
    current_page = 1
    generate_post_list(filter='following'); 
    document.querySelector('#new_post').style.display = 'none'
}

function pages(value) {
    if (value === '-1') current_page--
    else current_page++
    generate_post_list();
}

function edit_post(post_id) {
    let div_post_content =  document.querySelector(`div.text_content[data-post_id="${post_id}"]`);
    let post_content = document.querySelector(`p.post_content[data-post_id="${post_id}"]`);
    post_content.style.display = 'none';

    var textarea = document.querySelector(`textarea.edit_content[data-post_id="${post_id}"]`)
    var button = document.querySelector(`button.sava_btn[data-post_id="${post_id}"]`)
    if (textarea !== null) {
        textarea.remove();
        button.remove();
        post_content.style.display = 'block';
    }
    else {
        var content = post_content.innerHTML.replace(/<br>/g,'\n' );
        let post_element = document.createElement('textarea');
        post_element.className = 'edit_content col-12 form-control';
        post_element.setAttribute('data-post_id', post_id);
        post_element.innerHTML = content;
        div_post_content.append(post_element);
        var textarea = document.querySelector(`textarea.edit_content[data-post_id="${post_id}"]`)
    
        textarea = document.querySelector(`textarea.edit_content[data-post_id="${post_id}"]`)
        textarea.style.height = (25+textarea.scrollHeight)+"px";

        let button = document.createElement('button');
        button.className = 'sava_btn btn btn-primary';
        button.setAttribute('data-post_id', post_id);
        button.innerHTML = 'Save'
        div_post_content.append(button);
        document.querySelector(`button.sava_btn[data-post_id="${post_id}"]`).addEventListener('click', update_Post)
    }
}

async function update_Post() {

    var post_id = this.dataset.post_id
    let post_content = document.querySelector(`p.post_content[data-post_id="${post_id}"]`);
    let edit_content = document.querySelector(`textarea.edit_content[data-post_id="${post_id}"]`);

    var content = edit_content.value
    var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    let data = new FormData();
    data.append('post_id', post_id)
    data.append('content', content)
    data.append('csrfmiddlewaretoken', csrftoken)

    await fetch('update_post', {
        method: 'POST',
        body: data,
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        post_content.innerHTML = data['content'].replace(/\n/g, '<br />');
        this.remove();
        edit_content.remove()
        post_content.style.display = 'block';
    });


}