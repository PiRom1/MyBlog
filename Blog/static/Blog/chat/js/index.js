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

    var text_color = document.getElementById('items').getAttribute('text-color');
    var border_color = document.getElementById('items').getAttribute('border-color');
    var skinRadios = document.querySelectorAll('.skin-radio');
    var previousPerCategory = {};

    // document.getElementById('message-meta').style.font-size=45;

    

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

    setInterval(reloadMessages, 10000);
    window.onfocus = function () {
        reloadMessages();
        badger.value = 0;
    };

    const skinsButton = document.getElementById('skins-button');
    const skinsPopup = document.getElementById('skins-popup');
    const closeSkinsPopup = document.getElementById('close-skins-popup');
    const skinsList = document.getElementById('skins-list');
    // On récupère les skins équipés avec un fetch
    let favoriteItems = [];
    fetch('/inventory/favorite', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        favoriteItems = data.favorite_items;
        displaySkins();
    });

    // Fonction pour afficher les skins par 'data-skin-type'
    function displaySkins() {
        const skinGroups = {};
        skinsList.innerHTML = ''; // Vider la liste avant d'ajouter

        favoriteItems.forEach(item => {
            if (!skinGroups[item.skinType]) {
                skinGroups[item.skinType] = [];
            }
            skinGroups[item.skinType].push(item);
        });

        for (const skinType in skinGroups) {
            const groupDiv = document.createElement('div');
            groupDiv.classList.add('skin-category');
            groupDiv.innerHTML = `<h3>${skinType}</h3>`;

            skinGroups[skinType].forEach((item, index) => {
                if (previousPerCategory[skinType] == null) {
                    previousPerCategory[skinType] = item.id;
                }
                const itemDiv = document.createElement('div');
                itemDiv.classList.add('skin-item');
                // Vérifier si le pattern commence par '#', auquel cas on affiche un cercle de couleur
                const colorCircle = item.pattern.startsWith('#') ? `<span class="color-circle" style="background-color:${item.pattern};"></span>` : '';
                // Ajouter le rond de sélection (input radio personnalisé)
                itemDiv.innerHTML = `
                    <label class="skin-label">
                        <input type="radio" name="${skinType}" class="skin-radio" data-item-id="${item.id}"  ${item.equipped? 'checked' : ''}>
                        <span class="custom-radio"></span>
                        ${item.name} - ${item.pattern} ${colorCircle}
                    </label>
                `;
                groupDiv.appendChild(itemDiv);
            });

            skinsList.appendChild(groupDiv);
        }

        skinRadios = document.querySelectorAll('.skin-radio');
    }


    // Ouvrir la popup des skins
    skinsButton.addEventListener('click', function () {
        skinsPopup.style.display = 'flex';
        update_equipped(skinRadios);
    });

    // Fermer la popup des skins
    closeSkinsPopup.addEventListener('click', function () {
        skinsPopup.style.display = 'none';
    });

    // Fermer la popup en cliquant à l'extérieur
    window.addEventListener('click', function (event) {
        if (event.target === skinsPopup) {
            skinsPopup.style.display = 'none';
        }
    });

    function update_equipped(skinRadios) {
        skinRadios.forEach(radio => {
            radio.addEventListener('change', function () {
                const itemId = this.getAttribute('data-item-id'); // Récupérer l'ID du nouvel item sélectionné
                const skinType = this.getAttribute('name'); // Récupérer le nom de la catégorie (skinType)
                console.log('Item ID : ', itemId);
                // Trouver l'ancien élément sélectionné dans la même catégorie (skinType)
                const previousItemId = previousPerCategory[skinType];
    
                // Envoi d'une requête AJAX pour mettre à jour l'attribut 'favoris' en backend
                fetch('/inventory/update_equipped', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrftoken // Assurez-vous d'ajouter le token CSRF ici
                    },
                    body: JSON.stringify({ 'item_id': itemId,
                                            'previous_item_id': previousItemId
                    }) // Envoyer l'ID de l'item
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        console.log('Item favori mis à jour');
                        previousPerCategory[skinType] = itemId;
                    } else {
                        console.log('Erreur : ', data.message);
                    }
                });
            });
        });
    }
    
});
