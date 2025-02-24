function Start(){
    name_ = document.getElementById("name").value;

    fetch('http://150.230.138.173:9876/api/addUser', { 
        method: 'POST', 
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: name_ }) // Adjust as needed
    })
    .then(response => response.json()) // Convert response to a Blob (binary data)
    .then(data => {
        console.log(data);
        localStorage.setItem("id", data.id);
        localStorage.setItem("name", data.name);
        localStorage.setItem('party', data.party);
    location.href = "main.html?id="+data.id+"&name="+data.name+"&party="+data.party;

    })
    .catch(error => console.error('Error:', error));
}


function getParam(param){
    const queryString = window.location.search;
    console.log(queryString);
    const urlParams = new URLSearchParams(queryString);
    return urlParams.get(param)
}