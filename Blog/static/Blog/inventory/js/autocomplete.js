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
        } else if (e.keyCode === 38) {  // Flèche haut
            currentFocus--;
            addActive(items);
        } else if (e.keyCode === 13) {  // Entrée
            e.preventDefault();
            if (currentFocus > -1 && items[currentFocus]) {
                items[currentFocus].click();
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
}

// Fonction pour filtrer les items de l'inventaire
function filterItems(value) {
    const items = document.querySelectorAll('.inventory-item');

    items.forEach(item => {
        const dataType = item.getAttribute('data-type');
        const dataSkinType = item.getAttribute('data-skin-type');
        const dataName = item.getAttribute('data-name');
        const dataStatus = item.getAttribute('data-status');
        const attribute_list = [dataType, dataSkinType, dataName, dataStatus];

        // Vérifier si l'une des valeurs correspond à la valeur recherchée
        if (attribute_list.includes(value)) {
            item.style.display = 'block';  // Afficher l'item
        } else {
            item.style.display = 'none';   // Masquer l'item
        }
    });
}

export default autocomplete;