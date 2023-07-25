let makeUrl = () => {
    let origin = window.location.origin;
    let textBox = document.getElementById("user_url");
    let rUrl = textBox.value;
    textBox.value = origin + rUrl;
}

window.addEventListener("DOMContentLoaded", makeUrl);

document.querySelectorAll(".deleteMsg").forEach((item) => {
    item.addEventListener("click", () => {
        let id = item.previousElementSibling.value;
        var formData = new FormData();
        formData.append("msgID", id);
        fetch(window.location.pathname, {method : "POST", body : formData}).then((r) => {
            if (r.status == 200) {
                document.getElementById("errorBox").classList.add("d-none")
                item.parentNode.parentNode.parentNode.parentNode.remove();
                if (!document.querySelectorAll(".card").length) {
                    document.getElementById("messageContainer").innerHTML += `
                        <h2 class="my-3 text-body-secondary text-center" id="messageCard">No messages bro :(</h2>
                    `;
                    document.getElementById("noMsgSpace").remove();
                    makeUrl();
                }
            }
            else {
                document.getElementById("errorBox").classList.remove("d-none");
            }
        });
    });
});