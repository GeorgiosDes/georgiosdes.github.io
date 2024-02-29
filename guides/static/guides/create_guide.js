document.addEventListener('DOMContentLoaded', function() {
  let count = 1;

  document.querySelector('#add-section').addEventListener('click', () => {
    addSection(count);
    count++;
  })

  document.querySelector('#remove-section').addEventListener('click', () => {
    removeSection(count);
    count--;
  })
});

function addSection(count) {
  const scroll = document.querySelector('#add-section');
  const container = document.querySelector('.section-container');
  const divTitle = document.createElement('div');
  const divContent = document.createElement('div');
  const divImage = document.createElement('div');
  divTitle.className = "form-group p-1 mt-3 border-primary border-top border-start border-end rounded-top";
  divTitle.id = `sec${count}-title`;
  divTitle.innerHTML = `
    <label for="section${count}-title">Section Title</label>
    <input class="form-control rounded-2" type="text" name="section${count}-title" id="section${count}-title" placeholder="Section Title" required>
  `;
  divContent.className = "form-group p-1 border-primary border-start border-end";
  divContent.id = `sec${count}-content`;
  divContent.innerHTML = `
    <label for="section${count}-content">Section Content</label>
    <textarea class="form-control rounded-2" type="text" name="section${count}-content" id="section${count}-content" rows="6" placeholder="Section Content" required></textarea>
  `;
  divImage.className = "form-group p-1 mb-4 border-primary border-start border-bottom border-end rounded-bottom";
  divImage.id = `sec${count}-image`;
  divImage.innerHTML = `
    <label for="section${count}-image">Section Image:</label>
    <input type="file" name="section${count}-image" id="section${count}-image">
  `;
  container.appendChild(divTitle);
  container.appendChild(divContent);
  container.appendChild(divImage);
  scroll.scrollIntoView({behavior:'smooth'});
  document.querySelector('#remove-section').hidden = false;
}

function removeSection(count) {
  const title = document.querySelector(`#sec${count - 1}-title`);
  const content = document.querySelector(`#sec${count - 1}-content`);
  const image = document.querySelector(`#sec${count - 1}-image`);

  title.remove();
  content.remove();
  image.remove();
  if (count == 2) {
    document.querySelector("#remove-section").hidden = true;
  }
}