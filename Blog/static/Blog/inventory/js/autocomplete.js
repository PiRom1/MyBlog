// Fonction d'auto-complétion
function autocomplete(input, items) {
    let currentFocus;
    
    // Récupérer l'icône de croix pour annuler le filtre
    const clearFilterButton = document.getElementById('clear-filter');

    // Lorsque l'utilisateur tape dans le champ
    input.addEventListener("input", function() {
        let val = this.value;
        closeAllLists();
        if (!val) return false;
        currentFocus = -1;

        // Créer un conteneur pour les suggestions
        const autocompleteList = document.createElement("div");
        autocompleteList.setAttribute("id", this.id + "autocomplete-list");
        autocompleteList.setAttribute("class", "autocomplete-items");
        this.parentNode.appendChild(autocompleteList);

        // Filtrer la liste et créer des suggestions
        items.forEach(item => {
            if (item.toLowerCase().includes(val.toLowerCase())) {
                const suggestion = document.createElement("div");
                suggestion.innerHTML = item;
                suggestion.addEventListener("click", function() {
                    // Remplir le champ avec la suggestion cliquée
                    input.value = this.innerText;
                    // Filtrer les items en fonction de la sélection
                    filterItems(input.value);
                    closeAllLists();
                    clearFilterButton.style.display = 'block'; 
                });
                autocompleteList.appendChild(suggestion);
            }
        });
    });

    // Gérer la navigation au clavier dans les suggestions
    input.addEventListener("keydown", function(e) {
        const list = document.getElementById(this.id + "autocomplete-list");
        let items = list ? list.getElementsByTagName("div") : [];
        if (e.keyCode === 40) {  // Flèche bas
            currentFocus++;
            addActive(items);
            ensureVisible(items[currentFocus], list);
        } else if (e.keyCode === 38) {  // Flèche haut
            currentFocus--;
            addActive(items);
            ensureVisible(items[currentFocus], list);
        } else if (e.keyCode === 13) {  // Entrée
            e.preventDefault();
            if (currentFocus > -1 && items[currentFocus]) {
                items[currentFocus].click();
            }
            else if (items.length === 0) {
                filterItems('');
                closeAllLists();
                clearFilterButton.style.display = 'None';
            }
        }
    });

    function addActive(items) {
        if (!items) return false;
        removeActive(items);
        if (currentFocus >= items.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = items.length - 1;
        items[currentFocus].classList.add("autocomplete-active");
    }

    function removeActive(items) {
        Array.from(items).forEach(item => item.classList.remove("autocomplete-active"));
    }

    function closeAllLists() {
        const items = document.getElementsByClassName("autocomplete-items");
        Array.from(items).forEach(item => item.parentNode.removeChild(item));
    }

    document.addEventListener("click", function (e) {
        closeAllLists(e.target);
    });

    // Fonction pour s'assurer que l'élément actif est visible dans la liste des suggestions
    function ensureVisible(activeItem, list) {
        const rect = activeItem.getBoundingClientRect();
        const listRect = list.getBoundingClientRect();

        if (rect.bottom > listRect.bottom) {
            // Si l'élément dépasse en bas, faire défiler vers le bas
            list.scrollTop = activeItem.offsetTop - listRect.height + activeItem.offsetHeight;
        } else if (rect.top < listRect.top) {
            // Si l'élément dépasse en haut, faire défiler vers le haut
            list.scrollTop = activeItem.offsetTop;
        }
    }
}

// Fonction pour filtrer les items de l'inventaire
function filterItems(value) {
    const items = document.querySelectorAll('.inventory-item');

    items.forEach(item => {
        const dataType = item.getAttribute('data-type');
        const dataSkinType = item.getAttribute('data-skin-type');
        const dataName = item.getAttribute('data-name');
        const dataFavorite = item.getAttribute('data-favorite');
        const dataEquipped = item.getAttribute('data-equipped');
        const attribute_list = [dataType, dataSkinType, dataName];

        // Vérifier si l'une des valeurs correspond à la valeur recherchée
        if (attribute_list.includes(value) || 
        (dataFavorite === 'True' && value === 'Favori') || 
        (dataEquipped === 'True' && value === 'Equipé') || 
        (value === 'Tous') || (value === '')) {
            item.style.display = 'block';  // Afficher l'item
        } else {
            item.style.display = 'none';   // Masquer l'item
        }
    });
}

export default autocomplete;