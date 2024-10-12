document.addEventListener('DOMContentLoaded', function() {
    const friendsModal = document.getElementById('friendsModal');
    const closeFriendsModalBtn = document.getElementById('closeFriendsModalBtn');
    const friendsIcon = document.getElementById('friendsIcon');

    function openModal() {
        friendsModal.style.display = 'block';
    }

    function closeModal() {
        friendsModal.style.display = 'none';
    }

    friendsIcon.addEventListener('click', function(event) {
        event.preventDefault();
        openModal();
    });

    closeFriendsModalBtn.addEventListener('click', closeModal);

    window.addEventListener('click', function(event) {
        if (event.target === friendsModal) {
            closeModal();
        }
    });

    // Edit Profile Modal
    const modal = document.getElementById("editProfileModal");
    const btn = document.getElementById("editProfileButton");
    const span = document.getElementsByClassName("close")[0];

    btn.onclick = function() {
        modal.style.display = "block";
    }

    span.onclick = function() {
        modal.style.display = "none";
        clearPasswordFields();
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
            clearPasswordFields(); 
        }
    }

    function clearPasswordFields() {
        document.getElementById('current_password').value = '';
        document.getElementById('new_password').value = '';
    }

    // Delete Gratitude
    const deleteButtons = document.querySelectorAll('.delete-gratitude');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const gratitudeId = this.dataset.id; // Получаем ID благодарности
            
            if (confirm('Вы уверены, что хотите удалить эту благодарность?')) {
                deleteGratitude(gratitudeId);
            }
        });
    });
});

// Функция для переключения видимости пароля
function togglePassword(fieldId) {
    const passwordField = document.getElementById(fieldId);
    const type = passwordField.type === 'password' ? 'text' : 'password';
    passwordField.type = type;
}


function deleteGratitude(gratitudeId) {
    fetch(`/delete_gratitude/${gratitudeId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({}), 
    })
    .then(response => {
        if (response.ok) {
            const listItem = document.querySelector(`.global_gratitude[data-id='${gratitudeId}']`);
            if (listItem) {
                listItem.remove();
            }
        } else {
            alert('Ошибка при удалении благодарности.'); 
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
    });
}