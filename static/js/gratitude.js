document.addEventListener('DOMContentLoaded', function () {
    const fileInput = document.getElementById('gratitude__input');
    const imagePreview = document.getElementById('gratitude__images-preview');
    const fileLabel = document.querySelector('.gratitude__file-label');

    fileLabel.addEventListener('click', (event) => {
        event.preventDefault();
        fileInput.click();
    });

    fileInput.addEventListener('change', function() {
        imagePreview.innerHTML = '';
        const files = this.files;

        if (files.length > 0) {
            for (const file of files) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.style.maxWidth = '100%';
                    img.style.marginTop = '10px';
                    imagePreview.appendChild(img);
                };
                reader.readAsDataURL(file);
            }
        }
    });
});
