document.addEventListener('DOMContentLoaded', function () {

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const items = document.querySelectorAll('.item');
    const popup = document.getElementById("popup");

    const popup_content = document.getElementById("popup-content-id");
    const close = document.getElementById("close");
    const buy = document.getElementById("buy");
    const remove = document.getElementById("remove");
    const user = document.getElementById("user").getAttribute("user");
    const fonts = [];
    let user_coins = document.getElementById('user-coins');

    

    // Global variables for buy and detail
    let your_items = document.querySelectorAll('.item[is_yours="True"]');
    var item_id;
    var item_price;
    var current_item;
    var market_id;
    var font_tab = [];

    // Loop throughout every selling items
    items.forEach(item =>  {

        

        // Get attributes 
        item_id = item.getAttribute("item_id");
        const skin = item.getAttribute("skin-type");
        const seller = item.getAttribute("seller");
        const pattern = item.getAttribute("pattern");
        const price = item.getAttribute("price");
        const url = item.getAttribute("url");

        
        const circle = document.getElementById(`color-circle-${item_id}`);
        const patternText = document.getElementById(`pattern-${item_id}`); 
        // Si le pattern commence par un # 
        if (pattern.startsWith('#')) {
            circle.style.backgroundColor = pattern;
            patternText.style.display = "none";
        }
        else {
            circle.style.display = "none";
            if (skin === "font") {
                font_tab.push(pattern);
            }
        }


        // Show emoji image
        if ( (skin === 'emoji' || skin === 'background_image') ) {
            var img = document.getElementById(`img-${item_id}`);
            img.style.display = 'inline';
            patternText.style.display = 'none';

            if (pattern === '') {
                document.getElementById(`name-${item_id}`).innerHTML = " (unused)";
            }

        }

      



        item.addEventListener('click', function() {

            // show detail popup
            popup.style.display = "block";
            item_id = item.getAttribute("item_id");
            current_item = item;
            item_price = price;
            // assert attributes
            var popup_name = document.getElementById("seller-name");
            var popup_price = document.getElementById("item-price");
            var popup_pattern = document.getElementById("item-pattern");
            var popup_skin = document.getElementById("item-skin");

            popup_skin.innerHTML = skin;
            popup_name.innerHTML = seller;
            popup_price.innerHTML = price;
            if (pattern.startsWith('#')) {
                popup_pattern.innerHTML = pattern + `<span class="color-circle" style="background-color: ${pattern};"></span>`;
            }
            else if (skin === "font") {
                popup_pattern.innerHTML = `<a style="font-family: '${pattern}'; color: #feefeb;">${pattern}</a>`;
            }
            else if (skin === 'emoji') {
                popup_pattern.innerHTML = '';
                var url = document.getElementById(`img-${item_id}`).src;
                
                var emoji_popup_img = document.createElement('img');
                emoji_popup_img.src = url;
                emoji_popup_img.width='25';
                emoji_popup_img.height='25';
                emoji_popup_img.style.display = 'inline;'

                popup_pattern.appendChild(emoji_popup_img);
            }
            else if (skin === 'background_image') {
                popup_pattern.innerHTML = '';
                var url = document.getElementById(`img-${item_id}`).src;
                
                var emoji_popup_img = document.createElement('img');
                emoji_popup_img.src = url;
                emoji_popup_img.width='25';
                emoji_popup_img.height='25';
                emoji_popup_img.style.display = 'inline;'

                popup_pattern.appendChild(emoji_popup_img);
            }
            else if (skin === 'border_image') {
            var url = document.getElementById(`img-${item_id}`).src;
            popup_content.style.flex = '1';
            popup_content.style.borderImageSource = `url(${url})`;
            popup_content.style.borderImageSlice = '31 16 30 15 fill';
            popup_content.style.borderImageOutset = '0px';
            popup_content.style.borderImageRepeat = 'round';
            popup_content.style.borderStyle = 'solid';
            popup_content.style.borderWidth = '30px 15px';
            popup_content.style.setProperty('border-image-source', `url(${url})`, 'important'); // Avec priorité 'important'
            popup_pattern.innerHTML = pattern;
            }
            else {
                popup_pattern.innerHTML = pattern;
            }

            market_id = item.getAttribute("market_id");

            
            if (seller === user) {
                remove.style.display = 'block';
                buy.style.display = 'none';
            }

            else {
                buy.style.display = 'block';
                remove.style.display = 'none';
            }
        })

        if (item.getAttribute("is_yours") === "True") {
            
            let item_id = item.getAttribute("item_id");
            const remove_item_icon = document.getElementById(`remove-item-icon-${item_id}`);

            remove_item_icon.addEventListener('click', function(event) {
                event.stopPropagation(); // <-- empêche l'ouverture de la popup
                current_item = document.querySelector(`.item[item_id="${item_id}"]`);
                console.log(current_item);

                const url = "hdv/remove"
            
                fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrftoken // Inclure le token CSRF pour la sécurité
                    },
                    body: `id=${item_id}`
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        current_item.remove();
                        popup.style.display = 'none';
                        remove_item_icon.remove();
                    }
                });

            })
        }


    })

    // Charger les fonts
    var font = document.createElement('link');
    font.rel = 'stylesheet';
    font.href = 'https://fonts.googleapis.com/css2?' 
    font_tab.forEach(f => {        
        font.href += 'family=' + f.replace(/ /g, '+') + '&';
    });
    font.href += 'display=swap';
    document.head.appendChild(font);

    // Close detail popup
    close.addEventListener('click', function() {
        popup.style.display = 'none';
        popup_content.style.flex = '1';
        popup_content.style.borderImageSource = ''
        popup_content.style.borderImageSlice = ''
        popup_content.style.borderImageOutset = '';
        popup_content.style.borderImageRepeat = '';
        popup_content.style.borderStyle = '';
        popup_content.style.borderWidth = '';
        popup_content.style.setProperty('');
    })

    // Buy item
    buy.addEventListener('click', function() {
        // Buy item with fetch and redirect toward hdv

        const url = "hdv/buy"

        fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken // Inclure le token CSRF pour la sécurité
            },
            body: `id=${market_id}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                current_item.remove();
                user_coins.innerHTML = `${parseInt(user_coins.innerHTML) - item_price}`;
                popup.style.display = 'none';
            }
        })

    })



    // Retirer de la vente
    remove.addEventListener('click', function() {
        
        const url = "hdv/remove"
        
        fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken // Inclure le token CSRF pour la sécurité
            },
            body: `id=${item_id}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                current_item.remove();
                popup.style.display = 'none';
            }
        });

    })

    // Remove all
    const remove_all_button = document.getElementById("remove-all-button");

    remove_all_button.addEventListener('click', function() {
        let your_items = document.querySelectorAll('.item[is_yours="True"]');
        if (your_items.length === 0) {
            alert("T'as aucun item en vente. T'es con ou quoi ?");
        }
        
        const url = "hdv/remove_all"
        
        fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken // Inclure le token CSRF pour la sécurité
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                your_items.forEach(item => {
                    item.remove();
                })     
                your_items = [];       
            }
        });

    })


    var font_url = document.createElement('link');
    font_url.rel = 'stylesheet';
    font_url.href = 'https://fonts.googleapis.com/css2?' 
    for (var f in fonts) {
        font_url.href += 'family=' + fonts[f].replace(/ /g, '+') + '&';
    }
    font_url.href += 'display=swap';
    document.head.appendChild(font_url);




    // Color patterns in history

    const history_skins = document.querySelectorAll('.skin');

    history_skins.forEach(skin => {
        let skin_pattern = skin.getAttribute('pattern');
        
        if (skin_pattern) {
            skin.style.color = skin_pattern;
        }
    })



    const selector_name = document.getElementById('selector-name');
    selector_name.addEventListener('input', function() {
        

        items.forEach(item => {

            if (item.getAttribute("is_yours") === "True") {
                return;
            }

            if (selector_name.value === '') {
                item.style.display = 'block';
            }
            else {
                let skin_type = item.getAttribute('skin-type');
                if (skin_type.toLowerCase().includes(selector_name.value.toLowerCase())) {
                    item.style.display = 'block';
                }
                else  {
                    item.style.display = 'none';
                }
            }
        })

    })



});