import autocomplete from './autocomplete.js';

// JavaScript pour gérer les événements de clic
document.addEventListener('DOMContentLoaded', function () {
    const items = document.querySelectorAll('.inventory-item');
    const contextMenu = document.getElementById('context-menu');
    const infoModal = document.getElementById('info-modal');
    const itemInfo = document.getElementById('item-info');
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    let selectedItem = null;

    // Récupérer les éléments du menu contextuel
    const infoOption = document.getElementById('info-option');
    const sellOption = document.getElementById('sell-option');
    const tradeOption = document.getElementById('trade-option');
    const favoriteOption = document.getElementById('favorite-option');
    const openOption = document.getElementById('open-option');
    const useOption = document.getElementById('use-option');
    const unequipOption = document.getElementById('unequip-option');
    const equipOption = document.getElementById('equip-option');

    // Price management
    const price_input = document.getElementById('price');
    console.log(price_input);

    price_input.addEventListener('keydown', function(e) {
        if (e.key === '-' || e.key === 'e' || e.key === 'E') {
            e.preventDefault();
        }

    })

   
    
    // Récupérer les noms des items
    const searchList = ['Tous', 'Equipé', 'Favori', 'box', 'skin'];

    // Charger les fonts
    var font_tab = [];

    function addHeartCircle(item) {
        // Créer un élément div pour le cercle avec le coeur
        const heartCircle = document.createElement('div');
        heartCircle.classList.add('heart-circle');

        // Ajouter l'icône de coeur de FontAwesome à l'intérieur du cercle
        heartCircle.innerHTML = '<i class="fas fa-heart"></i>';

        // Ajouter le cercle avec l'icône de coeur à l'item
        item.appendChild(heartCircle);
    }

    // Mettre à jour l'événement de clic sur les items pour afficher les options du menu contextuel
    items.forEach(item => {

        const itemName = item.getAttribute('data-name');
        const itemType = item.getAttribute('data-type');
        const itemFavorite = item.getAttribute('data-favorite');
        const itemEquipped = item.getAttribute('data-equipped');
        const itemSkinType = item.getAttribute('data-skin-type');
        const itemRarityName = item.getAttribute('data-rarity-name');
        const itemRarityColor = item.getAttribute('data-rarity-color');
        const itemPattern = item.getAttribute('data-pattern');
        const itemId = item.getAttribute('data-id');
        const Id = item.getAttribute('id');
        const itemUrl = item.getAttribute('data-url');
        
        

        if (itemName && !searchList.includes(itemName)) {searchList.push(itemName);}
        if (itemSkinType && !searchList.includes(itemSkinType)) {searchList.push(itemSkinType);}

        // Fonts
        if (itemSkinType === 'font' && font_tab.includes(itemPattern) === false) {
            font_tab.push(itemPattern);
        }

        // Set rarity color
        // Get the after pseudo of the item in jquery
        item.style.setProperty('--RarityBorder', `6px solid ${itemRarityColor}`);
                
        const pattern = item.getAttribute('data-pattern');
        // Vérifier si le pattern commence par un '#' (hexadécimal)
        if (pattern && pattern.startsWith('#')) {
            // Créer un élément div pour le cercle
            const colorCircle = document.createElement('div');
            colorCircle.classList.add('color-circle');
            
            // Appliquer la couleur de fond correspondant à l'hexadécimal du pattern
            colorCircle.style.backgroundColor = pattern;
            
            // Ajouter le cercle à l'item
            item.appendChild(colorCircle);
        }

        // Vérifier si l'item est favori
        if (itemFavorite === 'True') {
            addHeartCircle(item)
        }

       


        item.addEventListener('click', function (e) {
            e.preventDefault();
            selectedItem = item;
            const itemFavorite = item.getAttribute('data-favorite');
            const itemType = item.getAttribute('data-type');
            const isEquippedOnArenaDino = item.getAttribute('data-equipped-on-arena-dino') === 'True';
            const isEquippedOnDino = item.getAttribute('data-equipped-on-dino') === 'True';
            
            
            if (isEquippedOnDino) {
                // Hide all standard options
                sellOption.style.display = 'none';
                tradeOption.style.display = 'none';
                favoriteOption.style.display = 'none';
                openOption.style.display = 'none';
                useOption.style.display = 'none';
                unequipOption.style.display = 'none';
                equipOption.style.display = 'none';
                
                // Show arena warning message
                if (isEquippedOnArenaDino) {
                    if (contextMenu.querySelector('ul').querySelector('.dino-warning')) {
                        contextMenu.querySelector('ul').querySelector('.dino-warning').remove();
                    }
                    if (!contextMenu.querySelector('ul').querySelector('.arena-warning')) {
                        const arenaWarning = document.createElement('li');
                        arenaWarning.textContent = "Item utilisé sur un Dino en arène";
                        arenaWarning.className = 'arena-warning';
                        contextMenu.querySelector('ul').appendChild(arenaWarning);
                    }
                        
                } else if (!contextMenu.querySelector('ul').querySelector('.dino-warning')) {
                    if (contextMenu.querySelector('ul').querySelector('.arena-warning')) {
                        contextMenu.querySelector('ul').querySelector('.arena-warning').remove();
                    }
                    const dinoWarning = document.createElement('li');
                    dinoWarning.textContent = "Item utilisé sur un Dino. Déséquiper ?";
                    dinoWarning.className = 'dino-warning';
                    contextMenu.querySelector('ul').appendChild(dinoWarning);
                    dinoWarning.addEventListener('click', function() {
                        const itemId = selectedItem.getAttribute('data-id');
                        fetch('/unequip_dino_item', {
                            method: 'POST',
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest',
                                'Content-Type': 'application/x-www-form-urlencoded',
                                'X-CSRFToken': csrftoken
                            },
                            body: `item_id=${itemId}`
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                contextMenu.querySelector('ul').querySelector('.dino-warning').remove();
                                selectedItem.setAttribute('data-equipped-on-dino', 'False');
                            }
                        });
                    });
                }
            } else {
                // Regular context menu logic
                // Toujours afficher l'option "Infos", "Vendre" et "Échanger"
                if (contextMenu.querySelector('ul').querySelector('.arena-warning')) {
                    contextMenu.querySelector('ul').querySelector('.arena-warning').remove();
                } else if (contextMenu.querySelector('ul').querySelector('.dino-warning')) {
                    contextMenu.querySelector('ul').querySelector('.dino-warning').remove();
                }
                infoOption.style.display = 'block';
                sellOption.style.display = 'block';
                tradeOption.style.display = 'block';
                useOption.style.display = 'none';
                unequipOption.style.display = 'none';
                equipOption.style.display = 'none';
        
                // Gérer les options spécifiques aux skins
                if (itemType === 'skin') {
                    favoriteOption.style.display = 'block';
                    favoriteOption.textContent = itemFavorite === 'True' ? 'Retirer des favoris' : 'Ajouter en favori';
                } else {
                    favoriteOption.style.display = 'none';
                }
        
                // Gérer l'option "Ouvrir" pour les boîtes
                if (itemType === 'box') {
                    openOption.style.display = 'block';
                } else {
                    openOption.style.display = 'none';
                }
                
                console.log(itemSkinType);
    
                // Gérer l'option "Utiliser" des émojis 
                if (itemSkinType === 'emoji') {
                    favoriteOption.style.display = 'none';
                    if (itemPattern == '') {
                        useOption.style.display = 'block';
                    } else {
                        useOption.style.display = 'none';
                    }
                }
    
                // Gérer l'option "Utiliser" et "Déséquiper" des Backgrounds 
                if (itemSkinType === 'background_image') {
                    favoriteOption.style.display = 'none';
    
                    if (itemPattern === "") {
                        useOption.style.display = 'block';
                    }
    
                    else {
    
                        if (itemEquipped === "True") {
                            unequipOption.style.display = 'block';
                        }
                        else {
                            equipOption.style.display = 'block';
                        }
                    }
                }
    
                if (itemSkinType === 'border_image') {
                    infoModal.style.flex = '1';
                    infoModal.style.borderImageSlice = '31 16 30 15 fill';
                    infoModal.style.borderImageOutset = '0px';
                    infoModal.style.borderImageRepeat = 'round';
                    infoModal.style.borderStyle = 'solid';
                    infoModal.style.borderWidth = '30px 15px';
                    infoModal.style.setProperty('border-image-source', `url(${itemUrl})`, 'important'); // Avec priorité 'important'
                }
    
                else {
                    infoModal.style.borderImageSource = ''
                    infoModal.style.borderImageSlice = ''
                    infoModal.style.borderImageOutset = '';
                    infoModal.style.borderImageRepeat = '';
                    infoModal.style.borderStyle = '';
                    infoModal.style.borderWidth = '';
                }
            }
                

           


            // Positionner le menu contextuel à l'endroit du clic
            contextMenu.style.top = `${e.clientY}px`;
            contextMenu.style.left = `${e.clientX}px`;
            contextMenu.classList.add('active');
        });
    });

    // Charger les fonts
    var font = document.createElement('link');
    font.rel = 'stylesheet';
    font.href = 'https://fonts.googleapis.com/css2?' 
    for (var f in font_tab) {
        font.href += 'family=' + font_tab[f].replace(/ /g, '+') + '&';
    }
    font.href += 'display=swap';
    document.head.appendChild(font);

    // Cacher le menu contextuel lorsqu'on clique ailleurs
    document.addEventListener('click', function (e) {
        if (!e.target.closest('.inventory-item')) {
            
            // infoModal.style.borderImageSource = ''
            // infoModal.style.borderImageSlice = ''
            // infoModal.style.borderImageOutset = '';
            // infoModal.style.borderImageRepeat = '';
            // infoModal.style.borderStyle = '';
            // infoModal.style.borderWidth = '';
            contextMenu.classList.remove('active');
        }
    });

    // Récupérer l'élément pour le fond flou
    const blurBackground = document.getElementById('blur-background');

    // Fonction pour ouvrir la modale
    function openModal() {
        infoModal.classList.add('active');
        blurBackground.classList.add('active');
    }

    // Fonction pour fermer la modale
    function closeModal() {
        infoModal.classList.remove('active');
        blurBackground.classList.remove('active');
    }


    // Afficher les informations de l'item lorsqu'on clique sur "Infos"
    document.getElementById('info-option').addEventListener('click', function () {
        if (selectedItem) {
            const name = selectedItem.getAttribute('data-name');
            const date = selectedItem.getAttribute('data-date');
            const type = selectedItem.getAttribute('data-type');
            let additionalInfo = '';

            if (type === 'skin') {
                const pattern = selectedItem.getAttribute('data-pattern');
                const favorite = selectedItem.getAttribute('data-favorite');
                const skin_type = selectedItem.getAttribute('data-skin-type');
                const skin_rarity_name = selectedItem.getAttribute('data-rarity-name');

                additionalInfo = `<strong>Pattern:</strong> <a style="font-family: ${pattern}; color: #000;">${pattern}</a><br>
                                  <strong>Type:</strong> ${skin_type}<br>
                                  <strong>Statut:</strong> ${favorite === 'True' ? 'Favori' : 'Non favori'}<br>
                                  <strong>Rareté:</strong> ${skin_rarity_name}`;
            } else if (type === 'box') {
                const openPrice = selectedItem.getAttribute('data-open-price');
                additionalInfo = `<strong>Prix d'ouverture:</strong> ${openPrice} crédits`;
            }

            // Mettre à jour le contenu du modal
            itemInfo.innerHTML = `<strong>Nom:</strong> ${name}<br>
                                  <strong>Date d'obtention:</strong> ${date}<br>
                                  ${additionalInfo}`;
            // Ouvrir la modale
            openModal();
            contextMenu.classList.remove('active');
        }
    });

    // Fermer la modale lorsqu'on appuie sur "Echap" ou qu'on clique en dehors de la modale
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && infoModal.classList.contains('active')) {
            closeModal();
        }
    });
    document.addEventListener('click', function (e) {
        if (e.target === blurBackground) {
            closeModal();
        }
    });

    // Ajouter un événement de clic pour l'option "Ouvrir"
    openOption.addEventListener('click', function () {
        if (selectedItem) {
            const boxId = selectedItem.getAttribute('data-id'); // Récupérer l'ID de la boîte
            if (boxId) {
                // Rediriger vers l'URL '/lootbox/(box_id)'
                window.location.href = `/lootbox/${boxId}`;
            }
            contextMenu.classList.remove('active');
        }
    });


    unequipOption.addEventListener('click', function() {
        var itemId = selectedItem.getAttribute('data-id');

        fetch('/unequip_bg', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken // Inclure le token CSRF pour la sécurité
            },
            body: `item_id=${itemId}`
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            window.location.href='/inventory';
        })

    })

    equipOption.addEventListener('click', function() {
        var itemId = selectedItem.getAttribute('data-id');

        fetch('/equip_bg', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken // Inclure le token CSRF pour la sécurité
            },
            body: `item_id=${itemId}`
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            window.location.href='/inventory';
        })

    })




    useOption.addEventListener('click', function() {

        var itemId = selectedItem.getAttribute('data-id');
        var itemType = selectedItem.getAttribute('data-skin-type');
        var pattern = selectedItem.getAttribute('data-pattern');

        if (itemType === 'emoji') {
            window.location.href = `/emoji/${itemId}`;
        }

        if (itemType === 'background_image') {
            if (pattern === '') {
            window.location.href = `/background/${itemId}`;
            }            
        }
    });

    // Fonction pour équiper ou déséquiper l'item
    function toggleFavStatus() {
        if (selectedItem) {
            // Récupérer l'ID de l'item et le statut actuel
            const itemId = selectedItem.getAttribute('data-id');
            let favorite = selectedItem.getAttribute('data-favorite');
            
            // Bascule entre "equipped" et "unequipped"
            const newFavorite = (favorite === 'True') ? 'False' : 'True';

            var url = `/inventory/toggle_item_favorite`;

            // Envoyer la requête pour mettre à jour le statut en base de données
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrftoken // Inclure le token CSRF pour la sécurité
                },
                body: `item_id=${itemId}&favorite=${newFavorite}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Mettre à jour le statut dans l'attribut de l'élément
                    selectedItem.setAttribute('data-favorite', newFavorite);
                    // Ajouter ou supprimer le cercle avec le coeur
                    if (newFavorite === 'True') {
                        addHeartCircle(selectedItem);
                    } else {
                        const heartCircle = selectedItem.querySelector('.heart-circle');
                        if (heartCircle) {
                            heartCircle.remove();
                        }
                    }
                    // alert(`${selectedItem.getAttribute('data-name')} a été ${newStatus === 'equipped' ? 'équipé' : 'déséquipé'}.`);
                } else {
                    alert('Erreur lors de la mise à jour du statut : ' + data.message);
                }

                // Fermer le menu contextuel
                contextMenu.classList.remove('active');
            })
            .catch(error => {
                console.error('Erreur lors de la requête :', error);
                alert('Une erreur est survenue lors de la mise à jour du statut.');
            });
        }
    }

    // Ajouter un événement de clic pour l'option "Équiper/Déséquiper"
    favoriteOption.addEventListener('click', function () {
        toggleFavStatus();
    });

    // Récupérer l'élément de recherche
    const searchInput = document.getElementById("search-bar");
    // Ajouter un événement de saisie pour l'auto-complétion
    autocomplete(searchInput, searchList);
    // Récupérer l'icône de croix pour annuler le filtre
    const clearFilterButton = document.getElementById('clear-filter');
    // Réinitialiser la recherche et afficher tous les items lorsque la croix est cliquée
    clearFilterButton.addEventListener("click", function() {
        document.getElementById('search-bar').value = ""; // Vider la barre de recherche
        items.forEach(item => item.style.display = 'block');
        clearFilterButton.style.display = 'none'; // Masquer la croix
    });

});