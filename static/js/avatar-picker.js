// Resizes an image file client-side to a small JPEG data URI, so it can be
// stored as base64 text (matching User.profile_photo / Child.photo) without
// needing a file upload endpoint or persistent disk storage.
function resizeImageToDataUrl(file, maxSize) {
    maxSize = maxSize || 256;
    return new Promise(function (resolve) {
        var img = new Image();
        var url = URL.createObjectURL(file);
        img.onload = function () {
            var scale = Math.min(maxSize / img.width, maxSize / img.height, 1);
            var canvas = document.createElement('canvas');
            canvas.width = img.width * scale;
            canvas.height = img.height * scale;
            canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height);
            URL.revokeObjectURL(url);
            resolve(canvas.toDataURL('image/jpeg', 0.85));
        };
        img.src = url;
    });
}

// Wires a circular "click to change" avatar picker: clicking `trigger` opens
// `fileInput`; picking a file resizes it, writes the data URI into
// `dataInput.value`, and swaps `preview` to an <img> showing it. `onChange`
// (optional) runs after the data URI is set, e.g. to auto-submit a form.
function setupAvatarPicker({ trigger, fileInput, dataInput, preview, onChange }) {
    trigger.addEventListener('click', function () { fileInput.click(); });

    fileInput.addEventListener('change', function () {
        var file = fileInput.files && fileInput.files[0];
        if (!file) return;

        resizeImageToDataUrl(file).then(function (dataUrl) {
            dataInput.value = dataUrl;

            if (preview.tagName === 'IMG') {
                preview.src = dataUrl;
            } else {
                var img = document.createElement('img');
                img.id = preview.id;
                img.alt = 'Photo';
                img.className = 'w-full h-full object-cover';
                img.src = dataUrl;
                preview.replaceWith(img);
                preview = img;
            }

            if (onChange) onChange(dataUrl);
        });
    });
}
