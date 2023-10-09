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
        // Handle the error message here (create and display the popup)
        var popup = document.createElement('div');
        popup.className = 'popup';
        popup.textContent = data.error;

        // Append the popup to the body
        document.body.appendChild(popup);

        // Close the popup after a certain duration (e.g., 3 seconds)
        setTimeout(function() {
            document.body.removeChild(popup);
        }, 3000); // 3000 milliseconds = 3 seconds

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
