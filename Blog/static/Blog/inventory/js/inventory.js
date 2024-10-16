// JavaScript pour gérer les événements de clic
document.addEventListener('DOMContentLoaded', function () {
    const items = document.querySelectorAll('.inventory-item');
    const contextMenu = document.getElementById('context-menu');
    const infoModal = document.getElementById('info-modal');
    const itemInfo = document.getElementById('item-info');
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    let selectedItem = null;

    // Récupérer l'élément "Ouvrir" du menu contextuel
    const openOption = document.getElementById('open-option');
    // Récupérer l'élément pour l'option "Équiper/Déséquiper"
    const equipOption = document.getElementById('equip-option');

    // Mettre à jour l'événement de clic sur les items pour afficher l'option "Ouvrir" si c'est une boîte
    items.forEach(item => {
        item.addEventListener('click', function (e) {
            e.preventDefault();
            selectedItem = item;
            
            // Vérifier le type de l'item (boîte ou skin)
            const itemType = item.getAttribute('data-type');
            if (itemType === 'box') {
                openOption.style.display = 'block'; 
                equipOption.style.display = 'none'; 
            } else if (itemType === 'skin') {
                openOption.style.display = 'none';
                equipOption.style.display = 'block';
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
            const status = selectedItem.getAttribute('data-status');
            const date = selectedItem.getAttribute('data-date');
            const type = selectedItem.getAttribute('data-type');
            let additionalInfo = '';

            if (type === 'skin') {
                const pattern = selectedItem.getAttribute('data-pattern');
                additionalInfo = `<strong>Pattern:</strong> ${pattern}<br>
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
                    alert(`${selectedItem.getAttribute('data-name')} a été ${newStatus === 'equipped' ? 'équipé' : 'déséquipé'}.`);
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
});