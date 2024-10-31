document.addEventListener('DOMContentLoaded', function () {

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const items = document.querySelectorAll('.item');
    const popup = document.getElementById("popup");
    const close = document.getElementById("close");
    const buy = document.getElementById("buy");
    const remove = document.getElementById("remove");
    const user = document.getElementById("user").getAttribute("user");
    const fonts = [];
    

    

    // Global variables for buy and detail
    
    var item_id;
    var market_id;
    var font_tab = [];

    // Loop throughout every selling items
    items.forEach(item =>  {

        // Get attributes 
        const item_id = item.getAttribute("item_id");
        const skin = item.getAttribute("skin");
        const seller = item.getAttribute("seller");
        const pattern = item.getAttribute("pattern");
        const price = item.getAttribute("price");

        
        const circle = document.getElementById(`color-circle-${item_id}`);
        const patternText = document.getElementById(`pattern-${item_id}`); 
        // Si le pattern commence par un # 
        console.log("pattern : ", pattern);
        if (pattern.startsWith('#')) {
            circle.style.backgroundColor = pattern;
            patternText.style.display = "none";
        }
        else {
            circle.style.display = "none";
            if (skin === "Police") {
                font_tab.push(pattern);
            }
        }

        item.addEventListener('click', function() {

            // show detail popup
            popup.style.display = "block";

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
            else if (skin === "Police") {
                popup_pattern.innerHTML = `<a style="font-family: '${pattern}'; color: #feefeb;">${pattern}</a>`;
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
    })

    // Charger les fonts
    var font = document.createElement('link');
    font.rel = 'stylesheet';
    font.href = 'https://fonts.googleapis.com/css2?' 
    font_tab.forEach(f => {        
        console.log('font : ', f);
        font.href += 'family=' + f.replace(/ /g, '+') + '&';
    });
    font.href += 'display=swap';
    document.head.appendChild(font);

    // Close detail popup
    close.addEventListener('click', function() {
        popup.style.display = 'none';
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
            window.location.href="hdv";            
    });

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
            window.location.href="hdv";            
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


});