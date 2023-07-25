document.querySelectorAll("#chatsContainer form button").forEach((item) => {
    item.addEventListener('click', () => {
        chat_id = item.previousElementSibling.value;
        let sentData = new FormData();
        sentData.append("chat_id", chat_id);
        fetch(window.location.pathname, {method : "POST", body : sentData}).then((r) => {
            console.log(r.status)
            if (r.status == 227) {
                document.getElementById("errorBox").classList.add("d-none");
                window.location.href = item.dataset.target;
            }
            else {
                document.getElementById("errorBox").classList.remove("d-none");
            }
        });
    });
});