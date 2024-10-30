document.addEventListener('DOMContentLoaded', function () {

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const items = document.querySelectorAll('.item');
    const popup = document.getElementById("popup");
    const close = document.getElementById("close");
    const buy = document.getElementById("buy");
    const remove = document.getElementById("remove");
    const user = document.getElementById("user").getAttribute("user");

    

    

    // Global variables for buy and detail
    
    var item_id;
    var market_id;

    // Loop throughout every selling items
    items.forEach(item =>  {

        item_id = item.getAttribute("item_id");
        
        var circle = document.getElementById(`color-circle-${item_id}`);
        circle.style.backgroundColor = item.getAttribute("pattern");

        
        
        item.addEventListener('click', function() {

            // show detail popup
            popup.style.display = "block";

            // Get attributes 
            const skin = item.getAttribute("skin");
            const seller = item.getAttribute("seller");
            const pattern = item.getAttribute("pattern");
            const price = item.getAttribute("price");

            // assert attributes
            var popup_name = document.getElementById("seller-name");
            var popup_price = document.getElementById("item-price");
            var popup_pattern = document.getElementById("item-pattern");
            var popup_skin = document.getElementById("item-skin");

            popup_name.innerHTML = seller;
            popup_price.innerHTML = price;
            popup_pattern.innerHTML = pattern;
            popup_pattern.style.color = pattern;
            popup_skin.innerHTML = skin;

            item_id = item.getAttribute("item_id");
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


});