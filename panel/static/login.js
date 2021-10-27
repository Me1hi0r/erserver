let button = byId("login-button");
let form = document.querySelector(".form").style;
let wrapper = byId("wrapper");
let text = byId("main_text");

button.addEventListener("click", btnLogin, false);

form.onsubmit = function() {
    return false;
};

function val(name) {
    return document.querySelector(name).value;
}

function byId(name) {
    return document.getElementById(name);
}

function btnLogin(event) {
    event.preventDefault();
    fetch('/accounts/check/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': val('input[name="csrfmiddlewaretoken"]'),
        },
        referrerPolicy: 'no-referrer',
        body: JSON.stringify({
            pass: val("#pass"),
            name: val("#user"),
        })
    }).then((response) => {
        return response.json();
    }).then((data) => {
        console.log(data);
        if (data['status'] == 'user-not-exist') {
            text.innerText = 'Name or pass is wrong!';
            setTimeout(() => {
                window.location.href = "/";
            }, 1000);
        }
        wrapper.classList.add("form-success");
        (function animHideForm() {
            (form.opacity -= 0.1) > 0
                ?
                setTimeout(animHideForm, 40) :
                (function redirect(path = '/panel') {
                    form.display = "hidden";
                    button.removeEventListener("click", btnLogin, false);
                    setTimeout(() => {
                        window.location.href = path;
                    }, 1000);
                })();
        })();
    });
}