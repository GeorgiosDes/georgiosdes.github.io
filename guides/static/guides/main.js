document.addEventListener('DOMContentLoaded', function() {
  window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    const swarmLogo = document.querySelector('#swarm-logo');
    if (window.scrollY > 60) {
        navbar.classList.add('shrink');
        swarmLogo.style = 'height: 40px';
    } else {
        navbar.classList.remove('shrink');
        swarmLogo.style = 'height: 90px';
    }
  });

  let page = 2;

  document.querySelector('#more-button').addEventListener('click', (event) => {
    event.preventDefault();
    const type = document.querySelector('#type').value;
    const gameId = document.querySelector('#game_id').value;
    const amount = document.querySelector('#amount').value;
    const sort = document.querySelector('#sort').value;

    loadLatest(type, gameId, page, amount, sort);
    page++;
  })
});

function loadLatest(type, gameId, page, amount, sort) {
  fetch(`/show_more/${type}/${gameId}/${page}/${amount}/${sort}`)
  .then(response => response.json())
  .then(data => {
    const allData = data.guides;
    const pagination = data.pagination;

    allData.forEach(element => {
      handleShowMore(element, type);
    })

    handlePagination(pagination, allData);
  })
  .catch(error => {
    console.log("Error", error);
  });
}

function handleShowMore(element, type) {
  const div = document.querySelector(`#${type}-div`);
  const col = document.createElement('div');
  const container = document.createElement('div');
  const link = document.createElement('a');
  const title = document.createElement('div');
  const video = document.createElement('div');
  const user = document.createElement('div');
  const date = document.createElement('div');

  // Build the divs
  col.className = 'col';
  container.className = "bg-black border border-2 border-dark rounded-3 text-center";
  link.href = `/${type}/${element.id}`;
  link.className = "text-decoration-none text-white";
  title.className = "p-3 mt-3 mb-2 title-container";
  video.className = "guides-video";
  user.className = "text-secondary mt-1";
  date.className = "text-secondary";

  title.innerHTML = `<h6 class="title">${element.title}</h6>`;
  video.innerHTML = `<iframe class="border-2 border-bottom border-top border-dark" width="100%" height="100%" src="${element.video_link}" frameborder="0" allowfullscreen></iframe>`;
  user.innerHTML = `<span>${element.user}</span>`;
  date.innerHTML = `<span>${element.date_created}</span>`;

  div.appendChild(col);
  col.appendChild(container);
  container.appendChild(link);
  link.appendChild(title);
  container.appendChild(video);
  container.appendChild(user);
  container.appendChild(date);
}

function handlePagination(pagination, type) {
  const scroll = document.querySelector('#latest-scroll');

  if (type.length !== 0) {
    if (pagination.has_next) {
      scroll.scrollIntoView({ behavior: 'smooth' });
    } else {
      scroll.scrollIntoView({ behavior: 'smooth' });
      document.querySelector('#more-div').hidden = true;
    }
  }
}