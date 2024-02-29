document.addEventListener('DOMContentLoaded', function() {

  // Submit new comment
  const newComment = document.querySelector('#new-comment-form');
  const content = document.querySelector('#new-comment-text');
  const type = document.querySelector('#type').value;
  const id = document.querySelector('#id').value;
  newComment.onsubmit = (event) => {
    event.preventDefault();
    handleNewComment(type, id);
    content.value = '';
  }
});

function handleNewComment(type, id) {
  
  // Submit new comment
  const content = document.querySelector('#new-comment-text').value;

  fetch('/comment', {
    method: 'POST',
    body: JSON.stringify({
      type: type,
      id: id,
      content: content
    })
  })
  .then(response => response.json())
  .then(result => {
    if (result.comment) {
      const noComments = document.querySelector('#no-comments');
      const latest = document.querySelector('#latest-comment');
      const username = document.querySelector('#username').value;
      const commentDiv = document.createElement('div');
      const commentUser = document.createElement('h6');
      const commentText = document.createElement('h6');
      commentDiv.className = 'border border-1 rounded-2';
      commentUser.className = 'mt-2';
      commentUser.innerHTML = `${username}&nbsp;&nbsp;&nbsp;&nbsp;Just now.`;
      commentText.innerHTML = result.comment;
      commentDiv.append(commentUser);
      commentDiv.append(commentText);
      latest.append(commentDiv);
      latest.hidden = false;

      if (noComments) {
        noComments.hidden = true;
      }
    }
    console.log(result);
  })
  .catch(error => {
    console.log("Error", error);
  });
}

function grow(content) {
  content.style.height = "5px";
  content.style.height = (content.scrollHeight) + "px";
}