// Blocks Saturday/Sunday selection on date inputs marked with the
// "weekday-only-date" class. Client-side convenience only - the real
// enforcement is server-side (Attendance.clean() / AttendanceForm.clean_date()
// / AttendanceSerializer.validate_date()).
function isWeekend(dateString) {
    var parts = dateString.split("-").map(Number);
    if (parts.length !== 3 || parts.some(isNaN)) return false;
    var utcDate = new Date(Date.UTC(parts[0], parts[1] - 1, parts[2]));
    var day = utcDate.getUTCDay();
    return day === 0 || day === 6;
}

function validateWeekdayInput(input) {
    if (input.value && isWeekend(input.value)) {
        input.setCustomValidity("Attendance can only be recorded for weekdays (Monday–Friday).");
    } else {
        input.setCustomValidity("");
    }
    input.reportValidity();
}

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".weekday-only-date").forEach(function (input) {
        validateWeekdayInput(input);
        input.addEventListener("input", function () { validateWeekdayInput(input); });
        input.addEventListener("change", function () { validateWeekdayInput(input); });
    });
});
