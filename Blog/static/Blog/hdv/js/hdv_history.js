document.addEventListener('DOMContentLoaded', async function () {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const data = document.getElementById("data");
    const max_pages = parseInt(data.getAttribute("max-pages"));
    const history_items = document.getElementById("history-items");

    console.log(data, max_pages);
    const previous_page = document.getElementById('previous-page');
    const next_page = document.getElementById('next-page');
    const page_number = document.getElementById('page-number');
    let page = 0;

    function capitalize(word) {
        if (!word) return ""; // gère le cas vide ou null
        return word[0].toUpperCase() + word.slice(1);
}

    async function get_market(page) {
        const url = "hdv/get_market";
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken
            },
            body: `page=${page}`
        });
        const data = await response.json();
        if (data.success) {
            return data.market;
        }
        return null;
}



    async function show_market(page) {
        const market = await get_market(page);

        if (page === 0) {
            previous_page.style.visibility = 'hidden';
            next_page.style.visibility = "visible";
        }
        else if (page < max_pages) {
            next_page.style.visibility = "visible";
            previous_page.style.visibility = "visible";
        }
        else {
            next_page.style.visibility = 'hidden';
            previous_page.style.visibility = "visible";
        }

        history_items.innerHTML = "";

        market.forEach(item => {
            
            const date = new Date(item.date);
            const date_str = `${date.getUTCDate()}/${date.getUTCMonth() + 1}/${date.getUTCFullYear()} ${date.getHours()}:${date.getMinutes()}`;
            const price_text = `${item.price} <img class="coin" src="/static/img/coin.png"" width="30"/>`;
            const skin_text = `<span class='skin' style='color: ${item.pattern};'>${item.skin}</span>`;
            let classname, action
            if (item.action === "buy") {
                classname = "buy";
                action = "a acheté";
            }
            else {
                classname = "sell";
                action = "a mis en vente";
            }
            let li = document.createElement('li');
            li.innerHTML = `${capitalize(item.user)} ${action} ${skin_text} pour ${price_text} (${date_str})`;
            li.classList.add(classname);
            
            history_items.appendChild(li);
        })

        page_number.innerHTML = `${page + 1}`;
}



    next_page.addEventListener('click', async function() {
        if (page < max_pages) {
            page += 1;
            await show_market(page);
        }
    })

    previous_page.addEventListener('click', async function() {
        if (page > 0) {
            page -= 1;
            await show_market(page);
        }
    })

    await show_market(page);

})