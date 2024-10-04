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

    // Modal for editing profile
    const modal = document.getElementById("editProfileModal");
    const btn = document.getElementById("editProfileButton");
    const span = document.getElementsByClassName("close")[0];

    // When the user clicks the button, open the modal 
    btn.onclick = function() {
        modal.style.display = "block";
    }

    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
        modal.style.display = "none";
        clearPasswordFields(); // Clear password fields
    }

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
            clearPasswordFields(); // Clear password fields
        }
    }

    // Function to clear password fields when the modal closes
    function clearPasswordFields() {
        document.getElementById('current_password').value = '';
        document.getElementById('new_password').value = '';
    }
});
