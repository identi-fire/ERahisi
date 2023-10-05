//export

const body = document.querySelector("body");
const modeToggle = document.querySelector(".mode-toggle");
const sidebar = document.querySelector("nav");
const sidebarToggle = document.querySelector(".sidebar-toggle");
const darkModeSwitch = document.querySelector(".switch");
//const axios = require('axios');

//const backendEndpoint = 'http://localhost:6969/login'; // Specify the backend endpoint here

// Make a POST request to the backend
axios.post(backendEndpoint, {
  // Request body data (if any)
})
  .then(response => {
    // Handle the response from the backend
    console.log(response.data);
  })
  .catch(error => {
    // Handle errors
    console.error(error);
  })

const menu = document.querySelector('#mobile-menu');
const menuLinks = document.querySelector('.navbar__menu');

menu.addEventListener('click', function() {
  menu.classList.toggle('is-active');
  menuLinks.classList.toggle('active');
})

// Function to toggle dark mode
// toggleDarkMode.js
function toggleDarkMode() {
  var body = document.body;
  body.classList.toggle("dark-mode"); // Toggle a CSS class for dark mode
}

// Check the initial dark mode status from local storage
let getMode = localStorage.getItem("mode");
if (getMode && getMode === "dark") {
  body.classList.add("dark");
}

// Add event listener to dark mode switch
if (darkModeSwitch) { // Check if the switch element exists
  darkModeSwitch.addEventListener("click", toggleDarkMode);
}