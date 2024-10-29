document.addEventListener('DOMContentLoaded', function () {

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const items = document.querySelectorAll('.item');
    const popup = document.getElementById("popup");
    const close = document.getElementById("close");
    const buy = document.getElementById("buy");

    // Global variables for buy and detail
    
    let id;

    // Loop throughout every selling items
    items.forEach(item =>  {

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

            id = item.getAttribute("id");

            
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
            body: `id=${id}`
        })
        .then(response => response.json())
        .then(data => {
            window.location.href="hdv";            
    });

    })


});