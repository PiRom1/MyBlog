//Import Class Badger from badger.js
import Badger from './badger.js';

document.addEventListener('DOMContentLoaded', function () {
    // Créer une instance de la classe Badger
    const badger = new Badger({
        size: 0.6,
        color: 'white',
        position: 'ne',
        //src: '/static/Blog/chat/img/86_icon.svg',
        onChange: function () {
            this._draw();
        }
    });
    badger.value = 0;

    var loadMoreBtn = document.getElementById('load-more');
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    

    loadMoreBtn.addEventListener('click', function () {
        console.log('Load more button clicked');
        var page = parseInt(loadMoreBtn.getAttribute('data-next-page'), 10);
        var session = document.querySelector('.container').id;
        console.log(page);

        // Requête AJAX pour obtenir plus de messages
        var url = `/${session}/?page=${page}`;

        fetch(url, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'  // Ajoute cet en-tête pour indiquer qu'il s'agit d'une requête AJAX
            }
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
        var last_message_id = messagesContainer.getAttribute('last-message-id');
        var url = `/${session}/#bottom`;

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
                last_message_id: last_message_id,
                new_message: new_message !== null
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.messages_html !== '') {
                console.log('New message received');
                var nb_new_msg = data.last_message_id - last_message_id;
                badger.value += nb_new_msg;
                // Ajouter les nouveaux messages au début
                messagesContainer.insertAdjacentHTML('beforeend', data.messages_html);

                // Met à jour l'offset
                var loadMoreBtn = document.getElementById('load-more');
                loadMoreBtn.setAttribute('data-next-page', 2);

                // Met à jour l'id du dernier message
                messagesContainer.setAttribute('last-message-id', data.last_message_id);
            }
            else {
                console.log('No new messages');
            }
        });
    };

   
    

    setInterval(reloadMessages, 60000);
    window.onfocus = function () {
        reloadMessages();
        badger.value = 0;
    };
});
