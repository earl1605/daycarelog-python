// Capitalizes the first letter of each word segment (segments split on space,
// hyphen, and apostrophe) without touching any other character - so deliberate
// casing like "McDonald" or "DeSilva" survives untouched. Runs on every
// keystroke; same-length output keeps cursor position restoration exact.
function capitalizeFirstLetters(value) {
    if (!value) return value;
    var result = "";
    var atSegmentStart = true;
    for (var i = 0; i < value.length; i++) {
        var char = value[i];
        result += atSegmentStart ? char.toUpperCase() : char;
        atSegmentStart = char === " " || char === "-" || char === "'";
    }
    return result;
}

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".capitalize-name").forEach(function (input) {
        input.setAttribute("autocapitalize", "words");
        input.addEventListener("input", function () {
            var start = input.selectionStart;
            var end = input.selectionEnd;
            var transformed = capitalizeFirstLetters(input.value);
            if (transformed !== input.value) {
                input.value = transformed;
                input.setSelectionRange(start, end);
            }
        });
    });
});
