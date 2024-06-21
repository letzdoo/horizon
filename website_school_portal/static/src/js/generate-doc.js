odoo.define("website_school_portal.generate_doc", function (require) {
    "use strict";

    function getAjaxJsonRpc(route, vals, callback) {
        var ajax = require("web.ajax");
        ajax.jsonRpc(route, "call", vals).then(function (data) {
            callback(data);
        });
    }

    function displayGeneratedMessage(documentLink) {
        displayDialogContent('Le document a été généré. Vous pouvez le consulter <a href="' + documentLink + '"  target="_blank">ici</a>.')
    }

    function displayExistingMessage(documentLink) {
        displayDialogContent('Le document demandé existe déjà actuellement. Vous pouvez le consulter <a href="' + documentLink + '"  target="_blank">ici</a>.')
    }

    function displayErrorMessage() {
        displayDialogContent('Une erreur est survenue. Veuillez réessayer plus tard.')
    }

    function displayDialogContent(content) {
        const div = document.querySelector("#dialogContent");
        if (div) {
            div.innerHTML = "";
            var p = document.createElement("p");
            p.innerHTML = content;
            div.append(p);
        }
    }

    function showDialogLoader() {
        let dialog = document.querySelector("#generateDialog");
        dialog.showModal();
    }


    let buttonsCloseDialog = document.querySelectorAll(".buttonCloseDialog");
    buttonsCloseDialog.forEach(button => {
        button.addEventListener("click", function(event) {
            event.preventDefault();
            let dialog = document.querySelector("#generateDialog");
            dialog.close();
            window.location = window.location.pathname;
        })
    });

    const form = document.querySelector('#request_document_form');
    const btn = document.querySelector("#btn_request_doc_generation");
    if (btn) {
        btn.addEventListener("click", (event) => {
            if (form && form.reportValidity()) {
                event.preventDefault();
      
                var route = "/my/generate-document";
                var vals = {
                    document_to_generate: document.getElementById("document_to_generate").value,
                };

                showDialogLoader()
    
                getAjaxJsonRpc(route, vals, function (data) {
                    if (data.result === "success") {
                        if (data.existing) {
                            displayExistingMessage(data.documentlink)
                        } else {
                            displayGeneratedMessage(data.documentlink)
                        }
                    } else {
                        displayErrorMessage()
                    }
                });
            }
        });
    }
});
