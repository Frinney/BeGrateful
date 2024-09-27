document.addEventListener('DOMContentLoaded', function () {
  const fileInput = document.getElementById('gratitude__input');
  const imagePreview = document.getElementById('gratitude__images-preview');
  const fileLabel = document.querySelector('.gratitude__file-label');
  
  // Обработчик для загрузки изображений
  fileLabel.addEventListener('click', (event) => {
    event.preventDefault(); // Предотвращает любое лишнее действие
    fileInput.click(); // Открывает окно выбора файла при клике на скрепку
  });
  
  fileInput.addEventListener('change', function() {
    imagePreview.innerHTML = ''; // Очистка контейнера для превью при новой загрузке
    const files = this.files;
  
    if (files.length > 0) {
      for (const file of files) {
        const reader = new FileReader();
        reader.onload = function(e) {
          const img = document.createElement('img');
          img.src = e.target.result;
          imagePreview.appendChild(img); // Добавляем превью изображений
        };
        reader.readAsDataURL(file); // Чтение файлов в base64
      }
    }
  });
});
