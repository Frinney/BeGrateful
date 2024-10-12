document.addEventListener('DOMContentLoaded', function () {
    const deleteButtons = document.querySelectorAll('.delete-friend');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function () {
            const friendId = this.dataset.friendId;

            fetch(`/delete_friend/${friendId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.closest('.friends-list__friend').remove();
                } else {
                    alert(data.error || 'An error occurred while deleting the friend.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while deleting the friend.');
            });
        });
    });
});