document.addEventListener('DOMContentLoaded', function() {
    const friendsModal = document.getElementById('friendsModal');
    const closeFriendsModalBtn = document.getElementById('closeFriendsModalBtn');
    const friendsIcon = document.getElementById('friendsIcon');

    // Функция для открытия модального окна
    function openModal() {
        friendsModal.style.display = 'block';
    }

    // Функция для закрытия модального окна
    function closeModal() {
        friendsModal.style.display = 'none';
    }

    // Открываем модальное окно по клику на иконку друзей
    friendsIcon.addEventListener('click', function(event) {
        event.preventDefault(); // Предотвращает переход по ссылке
        openModal(); // Открыть модальное окно
    });

    // Закрываем модальное окно по клику на кнопку закрытия
    closeFriendsModalBtn.addEventListener('click', closeModal);

    // Закрываем модальное окно при клике вне его содержимого
    window.addEventListener('click', function(event) {
        if (event.target === friendsModal) {
            closeModal();
        }
    });
});
