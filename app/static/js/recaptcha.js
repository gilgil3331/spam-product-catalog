// External file — required by CSP (no unsafe-inline allowed).
// Reads site key and action from form data attributes.
document.addEventListener('DOMContentLoaded', function () {
    var form = document.querySelector('[data-recaptcha-action]');
    if (!form) return;

    var siteKey = form.dataset.sitekey;
    var action  = form.dataset.recaptchaAction;
    var btn     = form.querySelector('[type="submit"]');

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        var f = this;

        if (btn) btn.disabled = true;

        // Poll until the reCAPTCHA API script has finished loading
        function waitForRecaptcha(attempts) {
            if (typeof grecaptcha === 'undefined') {
                if (attempts > 20) {
                    // API never loaded — submit anyway; server will reject the empty token
                    f.submit();
                    return;
                }
                setTimeout(function () { waitForRecaptcha(attempts + 1); }, 200);
                return;
            }
            grecaptcha.ready(function () {
                try {
                    grecaptcha.execute(siteKey, { action: action }).then(function (token) {
                        f.querySelector('[name="g-recaptcha-response"]').value = token;
                        f.submit();
                    }).catch(function () {
                        if (btn) btn.disabled = false;
                        f.submit();
                    });
                } catch (err) {
                    // execute() threw synchronously (e.g. key not registered) — unblock the form
                    if (btn) btn.disabled = false;
                    f.submit();
                }
            });
        }

        waitForRecaptcha(0);
    });
});
