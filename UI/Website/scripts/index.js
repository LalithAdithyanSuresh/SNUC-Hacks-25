fetch('http://localhost:5500/UI/PHP/queries.php', { // Change to your local path if different
    method: 'POST', // or 'GET' based on your needs
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ key: 'value' }) // Send data if needed
})
.then(response => response.json()) // Assuming the PHP file returns JSON
.then(data => console.log(data)) // Handle the response data
.catch(error => console.error('Error:', error));
