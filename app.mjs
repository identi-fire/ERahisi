//export

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
  });

const menu = document.querySelector('#mobile-menu');
const menuLinks = document.querySelector('.navbar__menu');

menu.addEventListener('click', function() {
  menu.classList.toggle('is-active');
  menuLinks.classList.toggle('active');
});
