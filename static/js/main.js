const lightModeBtn = document.getElementById("lightModeBtn");
const darkModeBtn = document.getElementById("darkModeBtn");

lightModeBtn.addEventListener("click", () => {
  lightModeBtn.classList.add("d-none");
  darkModeBtn.classList.remove("d-none");

  // set data-bs-theme in <html> to dark
  const html = document.querySelector("html");
  html.attributes["data-bs-theme"].value = "light";

  //   add to local storage
  localStorage.setItem("theme", "light");
});

darkModeBtn.addEventListener("click", () => {
  darkModeBtn.classList.add("d-none");
  lightModeBtn.classList.remove("d-none");

  // set data-bs-theme in <html> to light
  const html = document.querySelector("html");
  html.attributes["data-bs-theme"].value = "dark";

  //   add to local storage
  localStorage.setItem("theme", "dark");
});

// on window load, check if data-bs-theme in <html> is dark
window.addEventListener("DOMContentLoaded", () => {
  const html = document.querySelector("html");
  const theme = localStorage.getItem("theme");

  //   check if theme is item in local storage
  if (!theme) {
    html.attributes["data-bs-theme"].value = "light";
    lightModeBtn.classList.add("d-none");
    darkModeBtn.classList.remove("d-none");
    return;
  }

  if (theme === "dark") {
    html.attributes["data-bs-theme"].value = "dark";
    darkModeBtn.classList.add("d-none");
    lightModeBtn.classList.remove("d-none");
  } else {
    html.attributes["data-bs-theme"].value = "light";
    lightModeBtn.classList.add("d-none");
    darkModeBtn.classList.remove("d-none");
  }
});
