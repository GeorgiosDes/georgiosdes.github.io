document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email(email) {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#email').style.display = 'none';

  if (email.id !== undefined) {
    // Pre-fill composition fields
    const re = "Re:";
    document.querySelector('#compose-recipients').value = email.sender;
    if (!email.subject.includes('Re:')) {
      document.querySelector('#compose-subject').value = `${re} ${email.subject}`;
    } else {
      document.querySelector('#compose-subject').value = `${email.subject}`;
    }
    if (!email.body.includes('wrote:')) {
      // In case there are multiple recipients, the following line will ensure that only the name of the user who replies will be in the "...replied:" line.
      const user = document.querySelector('#user').value;
      document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote: \n${email.body}\n\nOn ${email.timestamp} ${user} replied:\n`;
    } else {
      // In case there are multiple recipients, the following line will ensure that only the name of the user who replies will be in the "...replied:" line.
      const user = document.querySelector('#user').value;
      document.querySelector('#compose-body').value = `${email.body}\n\nOn ${email.timestamp} ${user} replied:\n`;
    }
    document.querySelector('#compose-body').focus();
  } else {
    // Clear out composition fields
    document.querySelector('#compose-recipients').value = '';
    document.querySelector('#compose-subject').value = '';
    document.querySelector('#compose-body').value = '';
  }

  // Send mail
  document.querySelector('#compose-form').onsubmit = (event) => {
    event.preventDefault();

    const recipients = document.querySelector('#compose-recipients').value;
    const subject = document.querySelector('#compose-subject').value;
    const body = document.querySelector('#compose-body').value;
  
    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
        recipients: recipients,
        subject: subject,
        body: body
      })
    })
    .then(response => response.json())
    .then(result => {
      console.log(result);
      load_mailbox('sent');
    });
  }
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Show the mailbox emails
  fetch(`emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    console.log(emails);
    if (mailbox === 'inbox' || mailbox === 'archive') {
      for (let i = 0; i < emails.length; i++) {
        const div = document.createElement('div');
        div.id = emails[i].id;
        div.className = 'emailsDiv';
        div.innerHTML = `<p>From: ${emails[i].sender}</p><p id="subject">Subject: ${emails[i].subject}</p><p id="timestamp">${emails[i].timestamp}</p>`;
        div.addEventListener('click', function() {
          showEmail(emails[i].id, mailbox);
          readState(emails[i].id, emails[i].read);
        })
        if (emails[i].read === false || emails[i].archived === true) {
          div.style.backgroundColor = 'white';
        } else {
          div.style.backgroundColor = '#a9a9a9';
        }
        document.querySelector('#emails-view').append(div);
      }
    } else {
      for (let i = 0; i < emails.length; i++) {
        const div = document.createElement('div');
        div.id = emails[i].id;
        div.className = 'emailsDiv';
        div.innerHTML = `<p>To :${emails[i].recipients}</p>\<p id="subject">Subject: ${emails[i].subject}</p>\<p id="timestamp">${emails[i].timestamp}</p>`;
        div.addEventListener('click', function() {
          showEmail(emails[i].id, mailbox);
        })
        document.querySelector('#emails-view').append(div);
      }
    }
  })
}

// Show email
function showEmail(email, mailbox) {
  fetch(`emails/${email}`)
  .then(response => response.json())
  .then(email => {
      console.log(email);

      // Show inbox
      if (mailbox === 'inbox') {
        const div = document.querySelector('#email');
        div.className = 'emailDiv';
        div.innerHTML = `
        <p><b>From: </b>${email.sender}</p>\
        <p><b>To: </b>${email.recipients}</p>\
        <p><b>Subject: </b>${email.subject}</p>\
        <p><b>Timestamp: </b>${email.timestamp}</p>\
        <button class="btn btn-sm btn-outline-primary" id="reply">Reply</button>\
        <button class="btn btn-sm btn-outline-primary" id="unread">Mark as unread</button>\
        <button class="btn btn-sm btn-outline-primary" id="archive">Archive</button>\
        <p style="margin-top: 30px;">${email.body}</p`;
        document.querySelector('#reply').addEventListener('click', function() {
          compose_email(email);
        })
        document.querySelector('#unread').addEventListener('click', function() {
          readState(email.id, email.read);
        })
        document.querySelector('#archive').addEventListener('click', function() {
          archivedState(email.id, email.archived);
        })
        document.querySelector('#emails-view').style.display = 'none';
        document.querySelector('#compose-view').style.display = 'none';
        document.querySelector('#email').style.display = 'block';

        // Show sent
      } else if (mailbox === 'sent') {
        const div = document.querySelector('#email');
        div.className = 'emailDiv';
        div.innerHTML = `
        <p><b>From: </b>${email.sender}</p>\
        <p><b>To: </b>${email.recipients}</p>\
        <p><b>Subject: </b>${email.subject}</p>\
        <p><b>Timestamp: </b>${email.timestamp}</p>\
        <p style="margin-top: 30px;">${email.body}</p`;
        document.querySelector('#emails-view').style.display = 'none';
        document.querySelector('#compose-view').style.display = 'none';
        document.querySelector('#email').style.display = 'block';

        // Show archived
      } else {
        const div = document.querySelector('#email');
        div.className = 'emailDiv';
        div.innerHTML = `
        <p><b>From: </b>${email.sender}</p>\
        <p><b>To: </b>${email.recipients}</p>\
        <p><b>Subject: </b>${email.subject}</p>\
        <p><b>Timestamp: </b>${email.timestamp}</p>\
        <button class="btn btn-sm btn-outline-primary" id="reply">Reply</button>\
        <button class="btn btn-sm btn-outline-primary" id="unarchive">Unarchive</button>\
        <p style="margin-top: 30px;">${email.body}</p`;
        document.querySelector('#reply').addEventListener('click', function() {
          compose_email(email);
        })
        document.querySelector('#unarchive').addEventListener('click', function() {
          archivedState(email.id, email.archived);
        })
        document.querySelector('#emails-view').style.display = 'none';
        document.querySelector('#compose-view').style.display = 'none';
        document.querySelector('#email').style.display = 'block';
      }
  });
}

// Change email read to true or false
function readState(email, read) {
  fetch(`/emails/${email}`, {
    method: 'PUT',
    body: JSON.stringify({
        read: !read
    })
  })
  load_mailbox('inbox');
}

// Change archived state to true or false
function archivedState(email, archived) {
  fetch(`/emails/${email}`, {
    method: 'PUT',
    body: JSON.stringify({
        archived: !archived
    })
  })
  location.reload();
}

function reply(email) {
  compose_email(email);
}