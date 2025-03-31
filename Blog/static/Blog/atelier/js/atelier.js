
// JavaScript pour gérer les événements de clic
document.addEventListener('DOMContentLoaded', function () {
    const csrftoken = document.querySelector('[name=csrf-token]').content;

    const context_popup = document.getElementById('context-popup');
    const font_tab = Array();

    function manage_click_on_item(item) {

        
        item.addEventListener('click', function() {
            
                
            console.log(nb_items_recycles);
            if (item.parentElement.id === 'inventory-grid') {
                if (nb_items_recycles < 10) {
                    recycled_items.prepend(item);
                    nb_items_recycles += 1
                    examples[nb_items_recycles-1].style.display = 'none';

                    items_a_recycler.push(item.getAttribute('data-id'));

                    let rarity_name = item.getAttribute('data-rarity-name');

                    items.forEach(item => {
                        if (item.getAttribute('data-rarity-name') !== rarity_name) {
                            if (item.getAttribute('is-movable') === "true") {
                                item.style.display = 'none';
                            }
                        }
                    })


                }
            }
            else {
                inventory_grid.append(item);
                nb_items_recycles -= 1
                examples[nb_items_recycles].style.display = 'block';

                items_a_recycler = items_a_recycler.filter(id => id !== item.getAttribute('data-id'));

                if (nb_items_recycles === 0) {
                    items.forEach(item => {
                        item.style.display = 'block';
                    })
                }


            }

            if (nb_items_recycles >= 10) {
                recycler.classList = "recycler-ok";
            }
            else {
                recycler.classList = "recycler-broken";
            }                


        })


    const skin_type = item.getAttribute('data-skin-type');

    let popupTimeout;
    let mouseX, mouseY;

    if (skin_type === 'font' | skin_type == 'border_image') {
        item.addEventListener('mousemove', function(e) {
            mouseX = e.pageX;
            mouseY = e.pageY;
        });

    

    item.addEventListener('mouseenter', function() {
        popupTimeout = setTimeout(() => {
            console.log(skin_type);
            context_popup.style.left = `${mouseX}px`;
            context_popup.style.top = `${mouseY}px`;
            context_popup.style.display = 'block';

            if (skin_type === 'font') {
                context_popup.style.fontFamily = item.getAttribute('data-pattern');
                context_popup.style.fontSize = '1.2em';
                context_popup.style.border = '';
            }
            else {
                console.log('here');
                context_popup.style.fontFamily = "";
                context_popup.style.fontSize = '1.2em';
                
                context_popup.style.flex = '1';
                context_popup.style.borderImageSlice = '31 16 30 15 fill';
                context_popup.style.borderImageOutset = '0px';
                context_popup.style.borderImageRepeat = 'round';
                context_popup.style.borderStyle = 'solid';
                context_popup.style.borderWidth = '30px 15px';
                context_popup.style.setProperty('border-image-source', `url(${item.getAttribute('data-url')})`, 'important'); // Avec priorité 'important'

            }

            

        }, 400); // Délai de 1 seconde (1000 ms)
    });

    item.addEventListener('mouseleave', function() {
        clearTimeout(popupTimeout); // Annule l'affichage si la souris quitte avant 1s
        context_popup.style.display = 'none'; // Cache le popup si la souris part
    });
}
        else {
            console.log(skin_type);
        }
    }


    let fadeTimeout, hideTimeout;


    let items_a_recycler = Array();
    const examples = Array();
    for (let i=1; i <= 10; i++) {
        examples.push(document.getElementById(`example_${i}`));
    }

    let nb_items_recycles = 0;
    const inventory_grid = document.getElementById('inventory-grid');
    const recycled_items = document.getElementById('recycled-items');
    const recycler = document.getElementById("recycler");
    const new_item = document.getElementById("new-item");

    const items = document.querySelectorAll('.inventory-item');


    items.forEach(item => {

        // Manage color circle
        const pattern = item.getAttribute('data-pattern');
        
        if (pattern && pattern.startsWith('#')) {
            // Créer un élément div pour le cercle
            const colorCircle = document.createElement('div');
            colorCircle.classList.add('color-circle');
            
            // Appliquer la couleur de fond correspondant à l'hexadécimal du pattern
            colorCircle.style.backgroundColor = pattern;
            
            // Ajouter le cercle à l'item
            item.appendChild(colorCircle);
        }

        // Manage rarity
        if (item.getAttribute("is-movable") === "true") {
            const rarity = item.getAttribute('data-rarity-name');
            const rarity_color = item.getAttribute('data-rarity-color');

            item.style.setProperty('--RarityBorder', `6px solid ${rarity_color}`);
            
            manage_click_on_item(item);
        }

        // Manage font
        console.log()
        if (item.getAttribute('data-skin-type') === 'font') {
            let font_family = item.getAttribute('data-pattern');
            font_tab.push(font_family);
            console.log(font_family);
    
        }

    

    })

    
    var font = document.createElement('link');
    font.rel = 'stylesheet';
    font.href = 'https://fonts.googleapis.com/css2?' 

    font_tab.forEach(font_name => {
        font.href += 'family=' + font_name.replace(/ /g, '+') + '&';
    })

    font.href += 'display=swap';
    document.head.appendChild(font);


    const popup = document.getElementById('popup');

    recycler.addEventListener('click', function() {
        // Il faudra aussi ajouter la prévisu des fonts / border image et les couleurs d'items
        console.log(`fetch : ${items_a_recycler}`);   

        
        fetch('/atelier/recycler', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken  // Récupération du token CSRF
            },
            body: JSON.stringify({items_a_recycler})
        }).then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.success === false) {
                console.log(data.error);
                popup.style.display = 'block';
                popup.innerHTML = data.error;

                clearTimeout(fadeTimeout);
                clearTimeout(hideTimeout);
            
                // Réinitialiser immédiatement la popup
                popup.style.display = "block";
                popup.style.opacity = "1";
                popup.style.transition = "none"; // Supprime temporairement l'animation pour éviter un bug
            
                // Attendre un petit instant avant de remettre la transition pour éviter les glitches
                setTimeout(() => {
                    popup.style.transition = "opacity 2s";
                }, 50);
            
                // Démarrer le fade-out après 1 seconde
                fadeTimeout = setTimeout(() => {
                    popup.style.opacity = "0";
                }, 1000);
            
                // Cacher complètement après le fade-out
                hideTimeout = setTimeout(() => {
                    popup.style.display = "none";
                }, 3000); // 1s (pause) + 2s (fade-out)


            }
            else {
                // Create new_item skin
                console.log(data);
                const img = document.createElement("img");
                img.src = data.skin_url;
                img.alt = "New_item";
                new_item.innerHTML = '';
                new_item.appendChild(img);
                new_item.style.setProperty('--RarityBorder', `6px solid ${data.rarity_color}`);

                // Delete items à recycler
                items_a_recycler.forEach(item => {
                    const removedItem = document.querySelectorAll(`div[data-id='${item}']`);
                    removedItem[0].remove();
                })
                examples.forEach(example => {
                    example.style.display = 'block';
                })

                nb_items_recycles = 0;
                items_a_recycler = Array();

                const new_item_inventory = document.createElement("div");
                new_item_inventory.classList = "inventory-item";
                new_item_inventory.setAttribute("data-id", data.item_id);
                new_item_inventory.setAttribute("data-rarity-name", data.rarity_name);
                new_item_inventory.appendChild(img.cloneNode());
                new_item_inventory.style.setProperty('--RarityBorder', `6px solid ${data.rarity_color}`);
                inventory_grid.append(new_item_inventory);
                

                items.forEach(item => {
                    item.style.display = 'block';
                })


                window.location.href = "/inventory";

            }
        });

    })





})