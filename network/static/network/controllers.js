function editPost(postId) {

    // Hide the content paragraph
    document.getElementById(`content-${postId}`).style.display = 'none';
    document.getElementById(`post-edit-${postId}`).style.display = 'none';

    // Show the edit form
    document.getElementById(`edit-post-form-${postId}`).style.display = 'block';

    // On form submit use fetch to post the data
    let form = document.getElementById(`edit-post-form-${postId}`);
    form.addEventListener('submit', function(event) {
        // Prevent the form from being submitted normally
        event.preventDefault();

        // Get the data from the input field
        let content = form.elements['id_content'].value;

        // Do something with the form data
        console.log('Form submitted!');
        console.log('Content:', content);

        // Get the CSRF token from the form
        let csrfToken = document.querySelector(`#edit-post-form-${postId} input[name="csrfmiddlewaretoken"]`).value;

        // Use fetch to post the data
        fetch(`/edit/${postId}`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: content
            })
        })
        .then(response => response.json())
        .then(() => {
            // Update the data for content field
            document.getElementById(`content-${postId}`).innerText = content;

            // Hide the content paragraph
            document.getElementById(`content-${postId}`).style.display = 'block';
            document.getElementById(`post-edit-${postId}`).style.display = 'block';

            // Show the edit form
            document.getElementById(`edit-post-form-${postId}`).style.display = 'none';
        })
    });
}

function like(postId) {

    // Get the likes value area
    let likesEl = document.getElementById(`likes-${postId}`);
    let currentValue = Number(likesEl.innerText);
    let newValue = currentValue + 1;
    

    // Get the CSRF token from the form
    let csrfToken = document.querySelector(`#edit-post-form-${postId} input[name="csrfmiddlewaretoken"]`).value;

    // Use fetch to post the data
    fetch(`/like/${postId}`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            newValue: newValue
        })
    })
    .then(response => response.json())
    .then(() => {
        likesEl.innerText = newValue;

        let likeBtn = document.getElementById(`like-${postId}`);
        likeBtn.setAttribute('id', `unlike-${postId}`);
        likeBtn.setAttribute('onclick', `unlike(${postId})`);
        likeBtn.innerText = 'Unlike';
    })
}

function unlike(postId) {

    // Get the likes value area
    let likesEl = document.getElementById(`likes-${postId}`);
    let currentValue = Number(likesEl.innerText);
    let newValue = currentValue - 1;
    

    // Get the CSRF token from the form
    let csrfToken = document.querySelector(`#edit-post-form-${postId} input[name="csrfmiddlewaretoken"]`).value;

    // Use fetch to post the data
    fetch(`/unlike/${postId}`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            newValue: newValue
        })
    })
    .then(response => response.json())
    .then(() => {
        likesEl.innerText = newValue;

        let unlikeBtn = document.getElementById(`unlike-${postId}`);
        unlikeBtn.setAttribute('id', `like-${postId}`);
        unlikeBtn.setAttribute('onclick', `like(${postId})`);
        unlikeBtn.innerText = 'Like';
    })
}