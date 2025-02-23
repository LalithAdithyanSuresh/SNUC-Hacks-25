leftBtns = 3;

function btn(n){
    var i;
    for(i=1; i<=leftBtns; i++){
        document.getElementById("btn"+i).classList.remove("active");
    }
    document.getElementById("btn"+n).classList.add("active");
}