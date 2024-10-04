let currentDate = new Date(2024, 9); // Октябрь 2024 года (месяцы начинаются с 0)

function renderCalendar() {
    const calendarElement = document.getElementById("calendar");
    const titleElement = document.getElementById("calendar-title");

    calendarElement.innerHTML = ""; // Очищаем календарь

    // Массив дней недели
    const weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"];

    // Добавляем дни недели
    weekdays.forEach(day => {
        const dayDiv = document.createElement("div");
        dayDiv.textContent = day;
        dayDiv.classList.add("weekday");
        calendarElement.appendChild(dayDiv);
    });

    // Получаем первый и последний дни месяца
    const firstDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
    const lastDay = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);

    titleElement.textContent = `${firstDay.toLocaleString('uk-UA', { month: 'long' })} ${currentDate.getFullYear()}`;

    // Добавляем пустые ячейки для предыдущего месяца
    const startDay = firstDay.getDay(); // Получаем день недели первого числа месяца
    const emptyCells = (startDay === 0 ? 6 : startDay - 1); // Преобразуем в число от 0 до 6, где 0 - это воскресенье

    for (let i = 0; i < emptyCells; i++) {
        const emptyDiv = document.createElement("div");
        calendarElement.appendChild(emptyDiv);
    }

    // Добавляем дни текущего месяца
    for (let day = 1; day <= lastDay.getDate(); day++) {
        const dayDiv = document.createElement("div");
        dayDiv.textContent = day;

        // Добавление обработчика событий для клика на день
        dayDiv.addEventListener("click", () => {
            const selectedDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
            const formattedDate = selectedDate.toISOString().split('T')[0]; // Форматирование даты в 'YYYY-MM-DD'
            window.location.href = `/gratitudes/${formattedDate}`; // Переход на страницу с благодарностями
        });

        // Добавление класса для стилей
        dayDiv.classList.add("calendar-day");

        calendarElement.appendChild(dayDiv);
    }
}

document.getElementById("prev-month").addEventListener("click", () => {
    currentDate.setMonth(currentDate.getMonth() - 1);
    renderCalendar();
});

document.getElementById("next-month").addEventListener("click", () => {
    currentDate.setMonth(currentDate.getMonth() + 1);
    renderCalendar();
});

// Инициализируем календарь
renderCalendar();
