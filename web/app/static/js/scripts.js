document.addEventListener('DOMContentLoaded', function () {
    const flipButtons = document.querySelectorAll('.flip-button');
    flipButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            const card = button.closest('.card-inner');
            card.classList.toggle('flip');
        });
    });

    const checkboxes = document.querySelectorAll('.learned-card-checkbox');
    checkboxes.forEach(function (checkbox) {
        checkbox.addEventListener('change', function () {
            const cardId = this.dataset.cardId;
            const action = this.checked ? 'add' : 'remove';
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/learned_card', true);
            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            xhr.send('card_id=' + encodeURIComponent(cardId) + '&action=' + action);
        });
    });

    function confirmDelete(event) {
        if (!confirm("Вы уверены, что хотите удалить эту запись?")) {
            event.preventDefault();
        }
    }

    const deleteForms = document.querySelectorAll('.delete-form');
    deleteForms.forEach(function (form) {
        form.addEventListener('submit', confirmDelete);
    });
});