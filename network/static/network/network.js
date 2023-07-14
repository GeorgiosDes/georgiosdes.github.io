document.addEventListener('DOMContentLoaded', function() {

  // Toggle Profile view
  const navProfile = document.querySelector('#nav-profile');
  if (navProfile) {
    navProfile.addEventListener('click', (event) => {
      event.preventDefault();
      const username = event.target.innerHTML;
      loadProfile(username, 1);
    })
  }

  // Toggle All Posts view
  document.querySelector('#all-posts').addEventListener('click', (event) => {
    event.preventDefault();
    loadPosts(1);
  });

  // Toggle Following view
  const followingPosts = document.querySelector('#following-posts');
  if (followingPosts) {
    followingPosts.addEventListener('click', (event) => {
      event.preventDefault();
      loadFollowing(1);
    })
  }

  // Handle new post input
  const newPostInput = document.querySelector('#new-post-text');
  if (newPostInput) {
    newPostInput.addEventListener('input', () => {
      if (newPostInput.value.trim() !== '') {
        document.querySelector('#submit-post').hidden = false;
      } else {
        document.querySelector('#submit-post').hidden = true;
      }
    })
    newPostInput.addEventListener('blur', () => {
      setTimeout(() => {
        newPostInput.value = '';
        newPostInput.style.height = "46px";
        document.querySelector('#submit-post').hidden = true;
      }, 150);
    });
  }

  // Submit new post
  const postSubmit = document.querySelector('#new-post-form');
  if (postSubmit) {
    postSubmit.onsubmit = () => handleNewPost();
  }

  // Add follow or unfollow button to profiles you are viewing as authenticated user
  const followBtn = document.querySelector('#follow');
  const unfollowBtn = document.querySelector('#unfollow');
  if (followBtn) {
    followBtn.addEventListener('click', (event) => {
      event.preventDefault();
      handleFollow('follow');
    })
  }
  
  if (unfollowBtn) {
    unfollowBtn.addEventListener('click', (event) => {
      event.preventDefault();
      handleFollow('unfollow');
    })
  }

  // By default load All Posts
  loadPosts(1);
});

function loadPosts(page) {

  // Show all posts and hide the other views
  document.querySelector('#title-view').innerHTML = ' All Posts';
  document.querySelector('#title-view').className = 'bi bi-mailbox';
  document.querySelector('#title-view').style.color = '#007bff';
  document.querySelector('#follow-count').style.display = 'none';
  document.querySelector('#profile-view').style.display = 'none';
  document.querySelector('#posts-view').style.display = 'block';
  const currentUser = document.querySelector('#current-user').value;
  if (currentUser !== 'AnonymousUser') {
    document.querySelector('#follow-action').style.display = 'none';
  }

  // Clear out previous views
  document.querySelector('#profile-view').innerHTML = '';
  document.querySelector('#posts-view').innerHTML = '';

  const newPost = document.querySelector('#new-post-form');
  if (newPost) {
    document.querySelector('#new-post').style.display = 'block';
  }
  
  fetch(`posts/all/${page}`)
  .then(response => response.json())
  .then(data => {
    const posts = data.posts;
    const liked = data.likes;
    const comments = data.comments;
    const pagination = data.pagination;

    // Display each post
    handlePost(posts, liked, comments);

    // Paginate
    handlePagination(pagination, posts, 'loadPosts');
  })
  .catch(error => {
    console.log("Error", error);
  });
}

function loadProfile(username, page) {

  // Show profile and hide the other views
  document.querySelector('#title-view').innerHTML = ` ${username}`;
  document.querySelector('#title-view').className = 'bi bi-person';
  document.querySelector('#title-view').style.color = '#fff';
  document.querySelector('#posts-view').style.display = 'none';
  document.querySelector('#profile-view').style.display = 'block';
  document.querySelector('#follow-count').style.display = 'inline-block';
  const currentUser = document.querySelector('#current-user').value;
  if (currentUser !== 'AnonymousUser' && username !== currentUser) {
    document.querySelector('#follow-action').style.display = 'inline-block';
  } else if (currentUser !== 'AnonymousUser') {
    document.querySelector('#follow-action').style.display = 'none';
  }

  const newPost = document.querySelector('#new-post-form');
  if (newPost) {
    document.querySelector('#new-post').style.display = 'none';
  }
  
  // Clear out previous views
  document.querySelector('#profile-view').innerHTML = '';
  document.querySelector('#posts-view').innerHTML = '';

  fetch(`profile/${username}/${page}`)
  .then(response => response.json())
  .then(data => {
    const posts = data.posts;
    const follow = data.follow;
    const liked = data.likes;
    const comments = data.comments;
    const pagination = data.pagination;

    if (posts.length === 0) {
      document.querySelector('#profile-view').innerHTML = "You haven't posted anything yet";
    }
  
    // Display each post
    handlePost(posts, liked, comments, true);

    // Display Following and Followers count
    const following = document.querySelector('#following');
    const followers = document.querySelector('#followers');
    following.innerHTML = data.following;
    followers.innerHTML = data.followers;


    // Paginate
    handlePagination(pagination, posts, 'loadProfile', username);
    
    // Display Follow or Unfollow button
    const followBtn = document.querySelector('#follow');
    const unfollowBtn = document.querySelector('#unfollow');

    if (follow) {
      followBtn.style.display = 'none';
      unfollowBtn.style.display = 'block'
    } else {
      followBtn.style.display = 'block';
      unfollowBtn.style.display = 'none';
    }
  })
  .catch(error => {
    console.log("Error", error);
  });
}

function loadFollowing(page) {

  // Show all posts and hide the other views
  document.querySelector('#title-view').innerHTML = ' Following';
  document.querySelector('#title-view').className = 'bi bi-people';
  document.querySelector('#title-view').style.color = '#17a2b8';
  document.querySelector('#follow-count').style.display = 'none';
  document.querySelector('#profile-view').style.display = 'none';
  document.querySelector('#posts-view').style.display = 'block';
  const currentUser = document.querySelector('#current-user').value;
  if (currentUser !== 'AnonymousUser') {
    document.querySelector('#follow-action').style.display = 'none';
  }

  const newPost = document.querySelector('#new-post-form');
  if (newPost) {
    document.querySelector('#new-post').style.display = 'none';
  }

  // Clear out previous views
  document.querySelector('#profile-view').innerHTML = '';
  document.querySelector('#posts-view').innerHTML = '';
  
  fetch(`posts/following/${page}`)
  .then(response => response.json())
  .then(data => {
    const posts = data.posts;
    const liked = data.likes;
    const comments = data.comments;
    const pagination = data.pagination;

    if (posts.length === 0) {
      document.querySelector('#posts-view').innerHTML = "You don't follow anyone yet";
    }

    // Display each post
    handlePost(posts, liked, comments);

    // Paginate
    handlePagination(pagination, posts, 'loadFollowing');
  })
  .catch(error => {
    console.log("Error", error);
  });
}

function handleNewPost() {
  
  // Submit new post
  const content = document.querySelector('#new-post-text').value;
  const username = document.querySelector('#current-user').value;

  fetch('/posts', {
    method: 'POST',
    body: JSON.stringify({
      username: username,
      content: content
    })
  })
  .then(response => response.json())
  .then(result => {
    console.log(result);
    loadPosts(1);
  })
  .catch(error => {
    console.log("Error", error);
  });
}

function handleFollow(action) {
  const user = document.querySelector('#current-user').value;
  const username = document.querySelector('#title-view').innerHTML.trim();

  fetch(`profile/${action}`, {
    method: 'POST',
    body: JSON.stringify({
      user: user,
      following: username
    })
  })
  .then(response => response.json())
  .then(result => {
    if (result.follow) {
      document.getElementById('follow').style.display = 'none';
      document.getElementById('unfollow').style.display = 'block';
      document.getElementById('followers').innerHTML = result.followers;
    } else {
      document.getElementById('follow').style.display = 'block';
      document.getElementById('unfollow').style.display = 'none';
      document.getElementById('followers').innerHTML = result.followers;
    }
    console.log(result);
  })
  .catch(error => {
    console.log("Error", error);
  });
}

function handleEdit(post) {
  content = document.querySelector(`#content${post}`);
  contentDiv = document.querySelector(`.content-div${post}`);

  if (content.disabled) {
    content.disabled = false;
    contentDiv.className = "content-div-active";
    const editButton = document.querySelectorAll('.edit');
    editButton.forEach(button => {
      button.innerHTML = '';
    });
    const cancel = document.createElement('button');
    const save = document.createElement('button');
    cancel.className = 'btn btn-danger btn-sm';
    cancel.id = `cancel${post}`;
    cancel.innerHTML = 'Cancel';
    save.className = 'btn btn-success btn-sm';
    save.id = `save${post}`;
    save.innerHTML = 'Save';
    content.parentElement.append(save);
    content.parentElement.append(cancel);

    // Clicking somewhere off textarea
    content.addEventListener('blur', () => {
      setTimeout(() => {
        content.disabled = true;
        contentDiv.className = `content-div${post}`;
        const editButton = document.querySelectorAll('.edit');
        editButton.forEach(button => {
          button.innerHTML = 'Edit';
        });
        cancel.remove();
        save.remove();
      }, 150);
    })

    // Cancel button event listener
    cancel.addEventListener('click', (event) => {
      event.preventDefault();
      content.disabled = true;
      contentDiv.className = `content-div${post}`;
      const editButton = document.querySelectorAll('.edit');
      editButton.forEach(button => {
        button.innerHTML = 'Edit';
      });
      cancel.remove();
      save.remove();
    })

    // Save button event listener
    save.addEventListener('click', (event) => {
      event.preventDefault();
      content.disabled = true;
      contentDiv.className = `content-div${post}`;
      const editButton = document.querySelectorAll('.edit');
      editButton.forEach(button => {
        button.innerHTML = '';
      });
      cancel.remove();
      save.remove();

      fetch(`posts/edit/${post}`, {
        method: 'POST',
        body: JSON.stringify({
          content: content.value
        })
      })
      .then(response => response.json())
      .then(result => {
        if (result.edited) {
          document.getElementById(`content${post}`).innerHTML = content.value;
          document.getElementById(`edited${post}`).hidden = false;
        }
        console.log(result);
      })
      .catch(error => {
        console.log("Error", error);
      });
    })
  }

  const end = content.value.length;
  content.setSelectionRange(end, end);
  content.focus();
}

function handlePagination(pagination, posts, location, username) {
  const pageLinks = document.querySelector('.pagination');
  pageLinks.innerHTML = '';
  pageLinks.style.display = 'none';

  if (posts.length !== 0) {
    pageLinks.style.display = 'flex';

    if (pagination.has_previous) {
      const previous = document.createElement('li');
      previous.className = 'page-item';
      previous.innerHTML = `<a class="page-link" href="?page=${pagination.previous_page_number}">< Previous</a>`;
      pageLinks.appendChild(previous);
    }

    for (let i = 1; i <= pagination.total_pages; i++) {
      const link = document.createElement('li');
      link.className = 'page-item';
      link.innerHTML = `<a class="page-link" href="?page=${i}">${i}</a>`;
      if (i === pagination.current_page) {
        link.classList.add('active');
      }
      pageLinks.appendChild(link);
    }

    if (pagination.has_next) {
      const next = document.createElement('li');
      next.className = 'page-item';
      next.innerHTML = `<a class="page-link" href="?page=${pagination.next_page_number}">Next ></a>`;
      pageLinks.appendChild(next);
    }

    const links = document.querySelectorAll('.page-link');  
    links.forEach(link => {
      link.addEventListener('click', (event) => {
        event.preventDefault();
        if (link.innerHTML === '&lt; Previous') {
          const page = parseInt(document.querySelector('.active').firstChild.innerHTML) - 1;
          console.log(page);
          if (location === 'loadPosts') {
            loadPosts(page);
          } else if (location === 'loadProfile') {
            loadProfile(username, page);
          } else if (location === 'loadFollowing') {
            loadFollowing(page);
          }
        } else if (link.innerHTML === 'Next &gt;') {
          const page = parseInt(document.querySelector('.active').firstChild.innerHTML) + 1;
          console.log(page);
          if (location === 'loadPosts') {
            loadPosts(page);
          } else if (location === 'loadProfile') {
            loadProfile(username, page);
          } else if (location === 'loadFollowing') {
            loadFollowing(page);
          }          
        } else {
          const page = parseInt(link.innerHTML);
          console.log(page);
          if (location === 'loadPosts') {
            loadPosts(page);
          } else if (location === 'loadProfile') {
            loadProfile(username, page);
          } else if (location === 'loadFollowing') {
            loadFollowing(page);
          }
        }
      })
    })
  }
}

function handlePost(posts, liked, comments, profile) {
  posts.forEach(post => {
    const div = document.createElement('div');
    const author = document.createElement('div');
    const edit = document.createElement('div');
    const content = document.createElement('div');
    const timestamp = document.createElement('div');
    const likes = document.createElement('div');
    const commentForm = document.createElement('form');
    const comment = document.createElement('div');
    const allComments = document.createElement('div');
    const currentUser = document.querySelector('#current-user');
    const contentRows = post.content.split("\n");

    // Build the divs
    div.id = `post${post.id}`;
    div.className = "posts-div";
    if (profile) {
      document.querySelector('#profile-view').append(div);
    } else {
      document.querySelector('#posts-view').append(div);
    }
    author.className = "author";
    if (profile) {
      author.innerHTML = `<h5><span>${post.user}</span></h5>`;
    } else {
      author.innerHTML = `<h5><a href="#" class="profile" id="${post.id}">${post.user}</a></h5>`;
    }
    edit.innerHTML = `<a href="#" class="edit" id="edit${post.id}">Edit</a>`;
    content.className = `content-div${post.id}`;
    if (!post.edited) {
      content.innerHTML = `
      <textarea disabled class="post-content" id="content${post.id}" rows="${contentRows.length}" oninput="grow(this)">${post.content}</textarea>
      <small class="edited" id="edited${post.id}" hidden>(edited)</small>`;
    } else {
      content.innerHTML = `
      <textarea disabled class="post-content" id="content${post.id}" rows="${contentRows.length}" oninput="grow(this)">${post.content}</textarea>
      <small class="edited" id="edited${post.id}">(edited)</small>`;
    }
    timestamp.innerHTML =`<span class="timestamp">${post.date_created}</span>`;
    likes.innerHTML = `
    <div class="likes">
      <span id="heart${post.id}" class="bi bi-heart"></span>
      <span id="likes${post.id}">${post.likes}</span>
    </div>`;
    commentForm.id = `new-comment-form${post.id}`;
    comment.innerHTML = `<textarea class="comment" id="commentInput${post.id}" placeholder="Comment" oninput="grow(this)"></textarea>
    <input type="submit" class="btn btn-primary btn-sm" id="submit-comment${post.id}" value="Post" hidden>`;
    div.appendChild(author);
    author.appendChild(timestamp);

    // Make the profile name redirect you to the profile page, unless you are already in said profile page
    if (!profile) {
      document.getElementById(`${post.id}`).addEventListener('click', (event) => {
        event.preventDefault();
        loadProfile(post.username, 1);
      });
    }

    // Add edit button to every post made by the current user
    if (post.user === currentUser.value) {
      author.appendChild(edit);
      document.getElementById(`edit${post.id}`).addEventListener('click', (event) => {
        event.preventDefault();
        handleEdit(post.id);
      })
    }
    div.appendChild(content);

    // Add like button
    div.appendChild(likes);
    if (liked) {
      for (let i = 0; i < liked.length; i++) {
        const heart = document.getElementById(`heart${liked[i]}`);
        if (heart) {
          heart.className = 'bi bi-heart-fill';
        }
      }
    }
    if (currentUser.value !== 'AnonymousUser') {
      document.getElementById(`heart${post.id}`).addEventListener('click', (event) => {
        event.preventDefault();
        handleLike(post.id);
      })
    }

    // Add all comments
    allComments.className = 'all-comments';
    allComments.id = `all-comments-${post.id}`;
    allComments.hidden = true;
    allComments.innerHTML = '<span class="comments">Comments:</span>';
    div.appendChild(allComments);
    if (comments) {
      for (let i = 0; i < comments.length; i++) {
        if (comments[i][0] === post.id) {
          allComments.hidden = false;
          const commentDiv = document.createElement('div');
          commentDiv.id = `comment${i}`;
          commentDiv.innerHTML = `
          <h6 class="comment-user">${comments[i][2]}</h6>
          <span class="comment-content">${comments[i][1]}</span>`;
          allComments.appendChild(commentDiv);
        }
      }
    }

    // Add comment input field
    if (currentUser.value !== 'AnonymousUser') {
      div.appendChild(commentForm);
      commentForm.appendChild(comment);
    }
    const commentInput = document.querySelector(`#commentInput${post.id}`);
    if (commentInput) {
      commentInput.addEventListener('input', () => {
        if (commentInput.value.trim() !== '' ) {
          document.querySelector(`#submit-comment${post.id}`).hidden = false;
        } else {
          document.querySelector(`#submit-comment${post.id}`).hidden = true;
        }
      })
      commentInput.addEventListener('blur', function() {
        setTimeout(() => {
          commentInput.value = '';
          commentInput.style.height = "34px";
          document.querySelector(`#submit-comment${post.id}`).hidden = true;
        }, 150);
      });
    }

    // Handle new comment
    const commentSubmit = document.querySelector(`#new-comment-form${post.id}`);
    if (commentSubmit) {
      commentSubmit.onsubmit = (event) => {
        event.preventDefault();
        handleNewComment(post.id);
      }
    }
  });
}

function handleLike(post) {
  const heart = document.getElementById(`heart${post}`);
  if (heart.className === 'bi bi-heart') {
    heart.className = 'bi bi-heart-fill';
    var action = "like";
  } else if (heart.className === 'bi bi-heart-fill') {
    heart.className = 'bi bi-heart';
    var action = "unlike";
  }
  
  fetch(`posts/${action}`, {
    method: 'POST',
    body: JSON.stringify({
      post_id: post
    })
  })
  .then(response => response.json())
  .then(result => {
    if (result.ok) {
      const likeCount = document.getElementById(`likes${post}`);
      likeCount.innerHTML = result.likes;
    }
    console.log(result);
  })
  .catch(error => {
    console.log("Error", error);
  });
}

function handleNewComment(post) {
  // Submit new comment
  const content = document.querySelector(`#commentInput${post}`).value;
  const username = document.querySelector('#current-user').value;

  fetch('comment', {
    method: 'POST',
    body: JSON.stringify({
      username: username,
      content: content,
      post_id: post
    })
  })
  .then(response => response.json())
  .then(result => {
    if (result.comment) {
      const comments = document.getElementById(`all-comments-${post}`);
      const commentDiv = document.createElement('div');
      const commentUser = document.createElement('h6');
      const commentText = document.createElement('span');
      comments.hidden = false;
      commentDiv.className = 'comment-temp';
      commentUser.className = 'comment-user';
      commentUser.innerHTML = username;
      commentText.className = 'comment-content';
      commentText.innerHTML = result.comment;
      commentDiv.append(commentUser);
      commentDiv.append(commentText);
      comments.append(commentDiv);
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