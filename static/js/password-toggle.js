// Adds a show/hide eye button to every password input on the page, regardless
// of whether it came from hand-written template markup or Django's form.as_p
// (which gives no per-field hook to add markup around the input).
(function () {
    var EYE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="w-[18px] h-[18px]"><path d="M1.5 12S5 5 12 5s10.5 7 10.5 7-3.5 7-10.5 7S1.5 12 1.5 12Z"/><circle cx="12" cy="12" r="3"/></svg>';
    var EYE_OFF = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="w-[18px] h-[18px]"><path d="M3 3l18 18"/><path d="M10.6 5.1A10.6 10.6 0 0 1 12 5c7 0 10.5 7 10.5 7a13.6 13.6 0 0 1-3.1 4M6.6 6.6C3.5 8.6 1.5 12 1.5 12S5 19 12 19a10.7 10.7 0 0 0 4.4-.9"/><path d="M9.9 10.1a3 3 0 0 0 4 4"/></svg>';

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll('input[type="password"]').forEach(function (input) {
            var wrapper = document.createElement("div");
            wrapper.className = "password-toggle-wrapper";
            input.parentNode.insertBefore(wrapper, input);
            wrapper.appendChild(input);

            var btn = document.createElement("button");
            btn.type = "button";
            btn.className = "password-toggle-btn";
            btn.setAttribute("aria-label", "Show password");
            btn.innerHTML = EYE;
            wrapper.appendChild(btn);

            btn.addEventListener("click", function () {
                var isHidden = input.type === "password";
                input.type = isHidden ? "text" : "password";
                btn.innerHTML = isHidden ? EYE_OFF : EYE;
                btn.setAttribute("aria-label", isHidden ? "Hide password" : "Show password");
            });
        });
    });
})();
