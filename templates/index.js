const selectors = {
  article: "[js-article]",
  content: "[js-content]",
  author: "[js-author]",
  colour: "[js-colour]",
  editLink: "[js-button-edit]",
};

document.addEventListener("DOMContentLoaded", () => {
  fetch("https://guestbook.dnswrsrx.com/", {
    headers: { Authorization: "Basic 844f30425b73ca1a6b80d0b483b758a5" },
  })
    .then((resp) => resp.json())
    .then((payload) => {
      const posts = localStorage.getItem("posts") || [];
      const template = document.getElementById("article-template");

      payload.forEach((data) => {
        const templateInstance = template.cloneNode(true).content;

        const article = templateInstance.querySelector(selectors.article);
        const content = templateInstance.querySelector(selectors.content);
        const author = templateInstance.querySelector(selectors.author);
        const colour = templateInstance.querySelector(selectors.colour);
        const editLink = templateInstance.querySelector(selectors.editLink);

        // modify template
        article.style.setProperty("--color-background", `${data.colour}`);
        content.innerHTML = data.text;
        author.innerHTML = data.author;
        colour.innerHTML = `${data.colour}`;

        if (posts.includes(data.id)) {
          editLink.id = data.id;
        } else {
          editLink.remove();
        }

        document.querySelector("section").appendChild(templateInstance);
      });

      _initEditButtons();
    })
    .catch((e) => console.log(e));
});

document.querySelector("form").addEventListener("submit", (e) => {
  e.preventDefault();
  const data = new FormData(e.target);

  fetch("https://guestbook.dnswrsrx.com/", {
    headers: { Authorization: "Basic 844f30425b73ca1a6b80d0b483b758a5" },
    method: "POST",
    body: data,
  })
    .then((resp) => resp.text())
    .then((id) => {
      const posts = localStorage.getItem("posts");
      if (!posts) {
        localStorage.setItem("posts", id);
      } else {
        localStorage.setItem("posts", `${posts},${id}`);
      }
      location.assign(location.href);
    });
});

const form = document.querySelector("form");
const formArticle = form.querySelector("article");
const formColorLabel = form.querySelector(".color-label");

form.querySelector("#color-picker").addEventListener("input", (e) => {
  _updateFormColour(e.target.value);
});

function _updateFormColour(colourCode) {
  formArticle.style.setProperty("--color-background", colourCode);
  formColorLabel.innerText = colourCode;
}

function _initEditButtons() {
  const editButtons = document.querySelectorAll("[js-button-edit]");

  editButtons.forEach((button) => {
    button.addEventListener("click", (e) => {
      const parentArticle = e.target.closest("article");
      const content = parentArticle.querySelector(selectors.content);
      const author = parentArticle.querySelector(selectors.author);
      const colour = parentArticle.querySelector(selectors.colour);
      form.setAttribute("data-form-state", "edit");
      form.text.value = content.innerText;
      form.author.value = author.innerText;
      _updateFormColour(colour.innerText);
    });
  });
}
