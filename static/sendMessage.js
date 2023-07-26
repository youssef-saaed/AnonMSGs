let recBtn = document.getElementById("recordBTN");
recBtn.addEventListener("click", () => {
    let btnState = recBtn.getAttribute("data-state");
    let recText = recBtn.getElementsByTagName("span")[0];
    if (btnState == "0" || btnState == "2"){
        let voiceRecording = function (stream) {
            window.aStream = stream;
            let options = {mimeType: 'audio/webm'};
            let recordedChunks = [];
            window.mediaRecorder = new MediaRecorder(stream, options);

            window.mediaRecorder.addEventListener('dataavailable', function(e) {
                if (e.data.size > 0) {
                    recordedChunks.push(e.data);
                }
            });

            window.mediaRecorder.addEventListener('stop', function() {
                window.voiceRec = new Blob(recordedChunks);
            });

            recBtn.setAttribute("data-state", "1");
            recBtn.classList.remove("btn-dark");
            recBtn.classList.remove("btn-success");
            recBtn.classList.add("btn-danger");

            window.mediaRecorder.start();

            recText.innerText = "00:00";
            let time = 0;
            window.recordTimer = window.setInterval(() => {
                time++;
                let secs = time % 60;
                let mins = (time - secs) / 60;
                let t = "";
                mins > 9 ? t += mins.toString() : t += "0" + mins.toString();
                t += ":"
                secs > 9 ? t += secs.toString() : t += "0" + secs.toString();
                recText.innerText = t;
                if (time >= 90) {
                    recBtn.click();
                }
            }, 1000);
        }
        navigator.mediaDevices.getUserMedia({"audio":true}).then(voiceRecording);
    }
    else if (btnState == "1"){
        recBtn.setAttribute("data-state", "2");
        recBtn.classList.remove("btn-danger");
        recBtn.classList.add("btn-success");
        window.mediaRecorder.stop();
        clearInterval(window.recordTimer);
        setTimeout(() => {
            recText.innerText = "Done! press again to retry";
        }, 1000);
        window.aStream.getTracks().forEach(function(track) {
            track.stop();
        });
    }
});

let msgF = document.querySelector("#msgForm form")

msgF.addEventListener("submit", (e) => {
    var formData = new FormData();
    formData.append("voice", window.voiceRec);
    if (msgF.querySelector("#anonCheck")) {
        if (!msgF.querySelector("#anonCheck").checked) {
            formData.append("sender", msgF.querySelector("#sender").value);
        }
    }
    formData.append("msg", msgF.getElementsByTagName("textarea")[0].value)
    formData.append("signature", "main")
    fetch(window.location.pathname, {
        method: "POST",
        body: formData,
    })
    .then((response) => response.text())
    .then((responseText) => {
       console.log(responseText);
    });
})