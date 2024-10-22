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
    const equipOption = document.getElementById('equip-option');
    const openOption = document.getElementById('open-option');
    
    // Récupérer les noms des items
    const searchList = ['equipped', 'unequipped', 'locked', 'box', 'skin'];

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
        const itemStatus = item.getAttribute('data-status');
        const itemSkinType = item.getAttribute('data-skin-type');

        if (itemName && !searchList.includes(itemName)) {searchList.push(itemName);}
        if (itemSkinType && !searchList.includes(itemSkinType)) {searchList.push(itemSkinType);}
        
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

        // Vérifier si l'item est équipé
        if (itemStatus === 'equipped') {
            addHeartCircle(item)
        }

        item.addEventListener('click', function (e) {
            e.preventDefault();
            selectedItem = item;
            
            // Toujours afficher l'option "Infos"
            infoOption.style.display = 'block';
            
            // Gérer l'affichage des options Vendre et Échanger, sauf si l'item est "locked"
            if (itemStatus !== 'locked') {
                sellOption.style.display = 'block';
                tradeOption.style.display = 'block';
            } else {
                sellOption.style.display = 'none';
                tradeOption.style.display = 'none';
            }
    
            // Gérer les options spécifiques aux skins
            if (itemType === 'skin') {
                equipOption.style.display = 'block';
                equipOption.textContent = itemStatus === 'equipped' ? 'Déséquiper' : 'Équiper';
            } else {
                equipOption.style.display = 'none';
            }
    
            // Gérer l'option "Ouvrir" pour les boîtes
            if (itemType === 'box' && itemStatus !== 'locked') {
                openOption.style.display = 'block';
            } else {
                openOption.style.display = 'none';
            }

            // Positionner le menu contextuel à l'endroit du clic
            contextMenu.style.top = `${e.clientY}px`;
            contextMenu.style.left = `${e.clientX}px`;
            contextMenu.classList.add('active');
        });
    });

    // Cacher le menu contextuel lorsqu'on clique ailleurs
    document.addEventListener('click', function (e) {
        if (!e.target.closest('.inventory-item')) {
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
                const status = selectedItem.getAttribute('data-status');
                const skin_type = selectedItem.getAttribute('data-skin-type');
                additionalInfo = `<strong>Pattern:</strong> ${pattern}<br>
                                  <strong>Type:</strong> ${skin_type}<br>
                                  <strong>Statut:</strong> ${status}`;
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

    // Fonction pour équiper ou déséquiper l'item
    function toggleEquipStatus() {
        if (selectedItem) {
            // Récupérer l'ID de l'item et le statut actuel
            const itemId = selectedItem.getAttribute('data-id');
            let status = selectedItem.getAttribute('data-status');
            
            // Bascule entre "equipped" et "unequipped"
            const newStatus = (status === 'equipped') ? 'unequipped' : 'equipped';

            var url = `/inventory/toggle_item_status`;

            // Envoyer la requête pour mettre à jour le statut en base de données
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrftoken // Inclure le token CSRF pour la sécurité
                },
                body: `item_id=${itemId}&status=${newStatus}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Mettre à jour le statut dans l'attribut de l'élément
                    selectedItem.setAttribute('data-status', newStatus);
                    // Ajouter ou supprimer le cercle avec le coeur
                    if (newStatus === 'equipped') {
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
    equipOption.addEventListener('click', function () {
        toggleEquipStatus();
    });

    // Récupérer l'élément de filtre
    const filterButton = document.getElementById('filter-equipped');
    // Ajouter un événement de clic pour activer ou désactiver le filtre
    filterButton.addEventListener('click', function() {
        // Basculer la classe "active" pour changer la couleur du bouton
        filterButton.classList.toggle('active');
        const showEquippedOnly = filterButton.classList.contains('active');
        // Parcourir tous les items
        items.forEach(item => {
            const itemStatus = item.getAttribute('data-status');
            // Si le filtre est activé et l'item n'est pas équipé, on le cache
            if (showEquippedOnly && itemStatus !== 'equipped') {
                item.style.display = 'none';
            } else {
                // Sinon, on affiche l'item
                item.style.display = 'block';
            }
        });
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