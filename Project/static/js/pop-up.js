fetch('/personality-test', {
    method: 'POST',
    body: yourData,  // Include your form data here
    headers: {
        'Content-Type': 'application/json'
    }
})
.then(response => response.json())
.then(data => {
    console.log(data); // Log the received data to the console for debugging
    
    if (data.error) {
        // Handle the error message here (you can use a popup or any other method)
        console.error(data.error); // Log the error message to the console for further inspection
    } else {
        // Handle other response data if necessary
        // Example: Update UI based on the successful response
    }
})
.catch(error => {
    // Handle other errors if needed
    console.error(error); // Log any unexpected errors to the console for debugging
});
