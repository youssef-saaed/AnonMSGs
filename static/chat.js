let chatCont = document.getElementById("chatContainer");
let updateContScroll = () => {
    chatCont.scrollTop = chatCont.scrollHeight;
}

window.addEventListener('DOMContentLoaded', () => {
    updateContScroll();
});

document.getElementById("goBack").addEventListener('submit', (e) => {
    e.preventDefault();
    window.location.href = document.getElementById("goBack").dataset.target;
});

let sendBtn = document.getElementById("sendBtn");
sendBtn.addEventListener("click", () => {
    let msg = sendBtn.parentNode.previousElementSibling;
    if (msg.value) {
        let bodySent = new FormData();
        bodySent.append("msg", msg.value);
        fetch(window.location.pathname, {method : "POST", body : bodySent}).then((r) => {
            if (r.status == 227) {
                document.getElementById("chatMessages").innerHTML += `
                    <div class="w-100 d-flex justify-content-end">
                        <span class="bg-primary text-white p-2 rounded-3 my-2" style="max-width:75vw;">
                            ${msg.value}
                        </span>
                    </div>
                `;
                msg.value = '';
            }
            else {
                window.location.reload();
            }
        });
    }
});

window.setInterval(() => {
    fetch(window.location.pathname, {method : "GET"}).then((r) => {
        return r.text();
    }).then((html) => {
        let parser = new DOMParser();
        let doc = parser.parseFromString(html,"text/html");
        if (document.getElementById("chatMessages").innerHTML != doc.getElementById("chatMessages").innerHTML) {
            document.getElementById("chatMessages").innerHTML = doc.getElementById("chatMessages").innerHTML;
            updateContScroll();
        }
    });
}, 1000);