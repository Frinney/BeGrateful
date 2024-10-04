document.getElementById('nickname').addEventListener('input', async function() {
    const query = this.value;
    const suggestionsContainer = document.getElementById('suggestions');

    if (query.length > 0) {
        try {
            const response = await fetch(`/search_users?query=${query}`);
            if (!response.ok) {
                console.error("Ошибка при запросе:", response.statusText);
                return;
            }

            const users = await response.json();
            suggestionsContainer.innerHTML = '';

            if (users.length > 0) {
                users.forEach(user => {
                    const suggestionItem = document.createElement('div');
                    suggestionItem.textContent = user.login;
                    suggestionItem.classList.add('suggestion-item');

                    suggestionItem.onclick = () => {
                        window.location.href = `/user/${user.id}`;
                    };

                    suggestionsContainer.appendChild(suggestionItem);
                });
            } else {
                const noResults = document.createElement('div');
                noResults.textContent = "Немає результатів";
                noResults.classList.add('suggestion-item');
                suggestionsContainer.appendChild(noResults);
            }

            suggestionsContainer.style.display = 'block';
        } catch (error) {
            console.error("Ошибка выполнения запроса:", error);
        }
    } else {
        suggestionsContainer.innerHTML = '';
        suggestionsContainer.style.display = 'none';
    }
});

document.addEventListener('click', function(event) {
    const suggestionsContainer = document.getElementById('suggestions');
    const nicknameInput = document.getElementById('nickname');

    if (!nicknameInput.contains(event.target) && !suggestionsContainer.contains(event.target)) {
        suggestionsContainer.innerHTML = ''; 
        suggestionsContainer.style.display = 'none'; 
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const showSearchButton = document.getElementById('showSearch');
    const showFriendsListButton = document.getElementById('showFriendsList');
    const searchSection = document.getElementById('searchSection');
    const friendsListSection = document.getElementById('friendsListSection');

    showSearchButton.addEventListener('click', function() {
        searchSection.style.display = 'block';
        friendsListSection.style.display = 'none';
    });

    showFriendsListButton.addEventListener('click', function() {
        searchSection.style.display = 'none';
        friendsListSection.style.display = 'block';
    });
});
