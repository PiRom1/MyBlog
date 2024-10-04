document.addEventListener('DOMContentLoaded', function () {
    var loadMoreBtn = document.getElementById('load-more');
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    loadMoreBtn.addEventListener('click', function () {
        console.log('Load more button clicked');
        var page = parseInt(loadMoreBtn.getAttribute('data-next-page'), 10);
        var session = document.querySelector('.container').id;
        console.log(page);

        // Requête AJAX pour obtenir plus de messages
        url = `/${session}/?page=${page}`;

        fetch(url, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'  // Ajoute cet en-tête pour indiquer qu'il s'agit d'une requête AJAX
            }
        })
        .then(response => {
            console.log(response);
        })
        .then(response => response.json())
        .then(data => {
            var messagesContainer = document.querySelector('.messages');
            messagesContainer.innerHTML = '';
            // Ajouter les nouveaux messages au début
            messagesContainer.insertAdjacentHTML('afterbegin', data.messages_html);

            // Met à jour l'offset
            loadMoreBtn.setAttribute('data-next-page', page + 1);
        });
    });

    function reloadMessages() {
        var session = document.querySelector('.container').id;
        var messagesContainer = document.querySelector('.messages');
        var new_message = document.querySelector('.new-message');
        console.log('new_message', new_message);
        url = `/${session}/#bottom`;

        fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest', // Ajoute cet en-tête pour indiquer qu'il s'agit d'une requête AJAX
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            mode: 'same-origin',
            body: JSON.stringify({
                reload: true,
                last_message_id: messagesContainer.getAttribute('last-message-id'),
                new_message: document.querySelector('.new-message') !== null
            })
        })
        .then(response => response.json())
        .then(data => {
            // messagesContainer.innerHTML = '';
            // Ajouter les nouveaux messages au début
            messagesContainer.insertAdjacentHTML('beforeend', data.messages_html);

            // Met à jour l'offset
            var loadMoreBtn = document.getElementById('load-more');
            loadMoreBtn.setAttribute('data-next-page', 2);

            // Met à jour l'id du dernier message
            messagesContainer.setAttribute('last-message-id', data.last_message_id);
        });
    }
    

    function incrementCounter() {
        
        fetch('/increment/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken  // Récupération du token CSRF
            },
            body: JSON.stringify({})
        }).then(response => response.json())
        .then(data => console.log(data));
    }

    setInterval(reloadMessages, 60000);
});
