leftBtns = 3;

// alert(localStorage.getItem('party'));
function getQrParty() {
    fetch('http://150.230.138.173:9876/generate_qr', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',  // ✅ Ensures cookies (sessions) are sent
        body: JSON.stringify({ url: getParam('party')})  
    })
    .then(response => {
        if (!response.ok) throw new Error("Failed to fetch QR code");
        return response.blob();  // Get binary image data
    })
    .then(blob => {
        let imgUrl = URL.createObjectURL(blob);
        document.getElementById("qr-code").src = imgUrl;  // Display QR
    })
    .catch(error => console.error('Error:', error));
}


function btn(n){
    getQrParty();
    var i;
    for(i=1; i<=leftBtns; i++){
        document.getElementById("btn"+i).classList.add("menu-item-hide");
    }
    openMenu(n);
}

function openMenu(n){
    document.getElementById("menu"+n).classList.add("menu-mid-act");
}

function CloseMenu(){
    var i;
    for(i=1; i<=leftBtns; i++){
        document.getElementById("btn"+i).classList.remove("menu-item-hide");
        document.getElementById("menu"+i).classList.remove("menu-mid-act");
    }
}