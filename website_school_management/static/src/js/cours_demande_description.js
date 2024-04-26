

    function getAjaxJsonRpc(route, vals, callback) {
        var ajax = require("web.ajax");
        ajax.jsonRpc(route, "call", vals).then(function (data) {
            callback(data);
        });
    }

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

    const btn = document.querySelector("#btn_request_course_details");
    if (btn) {
        btn.addEventListener("click", (event) => {
            event.preventDefault();

            var route = "/cours/cours_demande_description";
            var vals = {
                email: document.getElementById("request_email").value,
                first_name: document.getElementById("request_first_name").value,
                last_name: document.getElementById("request_last_name").value,
                course_id: document.getElementById("request_course_id").value,
            };

            getAjaxJsonRpc(route, vals, function (data) {
                if (data.result === "success") {
                    displaySuccessMessage();
                } else {
                    displayErrorMessage();
                }
            });
        });
    }

