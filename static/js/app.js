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
});

