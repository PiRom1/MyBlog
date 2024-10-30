

document.addEventListener('DOMContentLoaded', function () {

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const sell_button = document.getElementById('sell-option');
    const sell_popup = document.getElementById('sell-popup');
    const close = document.getElementById('close');
    const sell = document.getElementById('sell');
    const price = document.getElementById('price');

    var item_name = document.getElementById('item-name');
    var item_pattern = document.getElementById('item-pattern');

    const items = this.querySelectorAll('.inventory-item');

    var name;
    var pattern;
    var item_id;

    items.forEach( item => {
        item.addEventListener('click', function() {

            name = item.getAttribute('data-name');
            pattern = item.getAttribute('data-pattern');
            item_id = item.getAttribute('data-id')

        })


    })



    sell_button.addEventListener('click', function() {
        sell_popup.style.display = 'block';
        item_name.innerHTML = name;
        item_pattern.innerHTML = pattern;
    })

    close.addEventListener('click', function() {

        sell_popup.style.display = 'none';
        
    })


    sell.addEventListener('click', function() {
        
        var price_value = price.value;
        console.log(price_value, item_id);


        const url = "/hdv/sell"

        fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken // Inclure le token CSRF pour la sécurité
            },
            body: `item_id=${item_id}&price=${price_value}`
        })
        .then(response => response.json())
        .then(data => {
            window.location.href="/inventory";            
    });

    })





});