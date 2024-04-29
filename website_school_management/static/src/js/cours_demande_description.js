function displaySuccessMessage() {
    const div = document.querySelector("#form_request_course_details");
    if (div) {
        div.innerHTML = "";
        var p = document.createElement("p");
        p.innerHTML = "Votre demande a bien été envoyée.";
        div.append(p);
    }
}

function displayErrorMessage() {
    const p = document.querySelector(".error_request_course_details");
    if (p) {
        p.innerHTML = "Une erreur est survenue. Veuillez réessayer plus tard.";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const btn = document.querySelector("#btn_request_course_details");
    if (btn) {
        btn.addEventListener("click", (event) => {
            event.preventDefault();

            var data = {'data': [
                {
                    "email": document.getElementById("request_email").value,
                    "first_name": document.getElementById("request_first_name").value,
                    "last_name": document.getElementById("request_last_name").value,
                    "course_id": document.getElementById("request_course_id").value,
                } ] 
            }
            json_data = JSON.stringify(data);

            let xhr = new XMLHttpRequest();
            xhr.open("POST", "/cours/cours_demande_description");
            // xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
            xhr.setRequestHeader("Content-Type", "application/json");
            // xhr.setRequestHeader('X-CSRF-Token', document.getElementById("request_csrf_token").value);
            xhr.onload = function () {
                if (xhr.status != 200) {
                    console.log("not 200")
                    displayErrorMessage();
                } else {
                    let response = JSON.parse(xhr.response);
                    if (response.result === "success") {
                        console.log("response success")
                        console.log(response)
                        displaySuccessMessage();
                    } else {
                        console.log("response failure")
                        console.log(response)
                        displayErrorMessage();
                    }
                }
            };
            xhr.onerror = function () {
                console.log("error")
                displayErrorMessage();
            };
            xhr.send(json_data);
        });
    }

});

