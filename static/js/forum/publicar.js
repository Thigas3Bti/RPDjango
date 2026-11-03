(() => {
        const photoInput = document.getElementById("id_foto");
        const photoPreview = document.getElementById("publish-photo-preview");
        const photoName = document.getElementById("publish-photo-name");
        let previewUrl = null;

        photoInput.addEventListener("change", () => {
            const file = photoInput.files[0];
            if (previewUrl) {
                URL.revokeObjectURL(previewUrl);
                previewUrl = null;
            }
            photoPreview.removeAttribute("src");
            photoPreview.style.display = "none";
            photoName.textContent = "";
            if (!file) return;
            photoName.textContent = file.name;
            previewUrl = URL.createObjectURL(file);
            photoPreview.src = previewUrl;
            photoPreview.style.display = "block";
        });
})();