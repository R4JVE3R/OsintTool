function goUser(){
    document.getElementById('maininput').style.display = "none";
    document.getElementById('loader').style.display = "block";
    x = document.getElementById('username').value
    window.location = document.location+'/'+x
}
function goPhone(){
    document.getElementById('maininput').style.display = "none";
    document.getElementById('loader').style.display = "block";
    x = document.getElementById('phone').value
    window.location = document.location+'/'+x
}
function goSite(){
    document.getElementById('maininput').style.display = "none";
    document.getElementById('loader').style.display = "block";
    x = document.getElementById('site').value
    window.location = document.location+'/'+x
}
function goEmail(){
    document.getElementById('maininput').style.display = "none";
    document.getElementById('loader').style.display = "block";
    x = document.getElementById('email').value
    window.location = document.location+'/'+x
}