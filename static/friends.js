document.getElementById("addBtn").addEventListener('click', () => {
    let username = document.getElementById("user").value.toLowerCase();
    let errorBox = document.getElementById("errorBox");
    let checked = false;
    if (!username) {
        errorBox.innerText = "Error! you must enter an username";
        errorBox.classList.remove("d-none");
    }
    else {
        errorBox.innerText = "";
        errorBox.classList.add("d-none");
        if (username.search(" ") != -1) {
            errorBox.innerText = "Error! invalid username";
            errorBox.classList.remove("d-none");
        }
        else {
            errorBox.innerText = "";
            errorBox.classList.add("d-none");
            checked = true;
        }
    }
    if (checked) {
        let sentData = new FormData();
        sentData.append("user", username);
        sentData.append("type", "add");
        fetch(window.location.pathname, {method : "POST", body : sentData}).then((r) => {
            if (r.status == 452) {
                errorBox.innerText = "Error! username not found";
                errorBox.classList.remove("d-none");
            }
            else if (r.status == 453) {
                errorBox.innerText = "Error! username already in your friend list or in your sent request list";
                errorBox.classList.remove("d-none");
            }
            else if (r.status == 454) {
                errorBox.innerText = "Error! you can't add yourself";
                errorBox.classList.remove("d-none");
            }
            else if (r.status == 227) {
                errorBox.innerText = "";
                errorBox.classList.add("d-none");
                location.reload();
            }
            else {
                errorBox.innerText = "Something went wrong try again!";
                errorBox.classList.remove("d-none");
            }
        });
    }
});

document.querySelectorAll(".removeBtn").forEach((item) => {
    item.addEventListener('click', () => {
        let username = item.parentNode.parentNode.previousElementSibling.innerText.toLowerCase();
        let sentData = new FormData();
        sentData.append("user", username);
        sentData.append("type", "remove");
        fetch(window.location.pathname, {method : "POST", body : sentData}).then((r) => {
            if (r.status == 227) {
                errorBox.innerText = "";
                errorBox.classList.add("d-none");
                location.reload();
            }
            else {
                errorBox.innerText = "Something went wrong try to reload the page!";
                errorBox.classList.remove("d-none");
            }
        });
    });
});

document.querySelectorAll(".cancelBtn").forEach((item) => {
    item.addEventListener('click', () => {
        let username = item.parentNode.parentNode.previousElementSibling.innerText.toLowerCase();
        let sentData = new FormData();
        sentData.append("user", username);
        sentData.append("type", "cancel");
        fetch(window.location.pathname, {method : "POST", body : sentData}).then((r) => {
            if (r.status == 227) {
                errorBox.innerText = "";
                errorBox.classList.add("d-none");
                location.reload();
            }
            else {
                errorBox.innerText = "Something went wrong try to reload the page!";
                errorBox.classList.remove("d-none");
            }
        });
    });
});

document.querySelectorAll(".acceptBtn").forEach((item) => {
    item.addEventListener('click', () => {
        let username = item.parentNode.parentNode.previousElementSibling.innerText.toLowerCase();
        let sentData = new FormData();
        sentData.append("user", username);
        sentData.append("type", "accept");
        fetch(window.location.pathname, {method : "POST", body : sentData}).then((r) => {
            if (r.status == 227) {
                errorBox.innerText = "";
                errorBox.classList.add("d-none");
                location.reload();
            }
            else {
                errorBox.innerText = "Something went wrong try to reload the page!";
                errorBox.classList.remove("d-none");
            }
        });
    });
});

document.querySelectorAll(".declineBtn").forEach((item) => {
    item.addEventListener('click', () => {
        let username = item.parentNode.parentNode.previousElementSibling.innerText.toLowerCase();
        let sentData = new FormData();
        sentData.append("user", username);
        sentData.append("type", "decline");
        fetch(window.location.pathname, {method : "POST", body : sentData}).then((r) => {
            if (r.status == 227) {
                errorBox.innerText = "";
                errorBox.classList.add("d-none");
                location.reload();
            }
            else {
                errorBox.innerText = "Something went wrong try to reload the page!";
                errorBox.classList.remove("d-none");
            }
        });
    });
});