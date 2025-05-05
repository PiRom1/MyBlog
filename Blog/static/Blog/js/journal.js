document.addEventListener('DOMContentLoaded', function () {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    
    let overlay;
    function assombrirPage(saufElement) {
        // Créer un overlay sombre couvrant toute la page
        overlay = document.createElement("div");
        overlay.style.position = "fixed";
        overlay.style.top = "0";
        overlay.style.left = "0";
        overlay.style.width = "100vw";
        overlay.style.height = "100vh";
        overlay.style.backgroundColor = "rgba(0, 0, 0, 0.7)"; // Assombrissement
        overlay.style.zIndex = "100";
    
        // Placer l'élément au-dessus de l'overlay
        saufElement.style.zIndex = "1001";
    
        // Ajouter l'overlay au body
        document.body.appendChild(overlay);
    
        // Supprimer l'overlay au clic dessus (optionnel)
        overlay.addEventListener("click", () => {
            overlay.remove();
            saufElement.style.zIndex = "";
            saufElement.style.opacity = '0%';
            saufElement.style.display = 'none';
        });
    }


    const icons = {'Soundbox' : 'fi fi-rs-ear-sound',
                   'Sondage' : 'fi fi-rs-poll-h',
                   'Ticket' : 'fi fi-rs-ticket-alt',
                   'Récit' : 'fi fi-rs-book-alt',
                   'Quête' : 'fi fi-rs-scroll-old',
                   'Pari' : 'fi fi-rs-dice-alt',
                   'Arène' : 'fi fi-rs-t-rex',
                   'HDV' : 'fi fi-rs-shop',

                }

    function add_entry(entry) {

        const li = document.createElement('li');
        const i = document.createElement('i');
        i.className = icons[entry.entry_type]
        li.appendChild(i);

        li.innerHTML += ` - (${entry.date}) ${entry.entry}`;
        

        if (entry.is_viewed === false) {
            li.style.fontWeight = 'bolder';
        }

        journal_content.appendChild(li);
    }


    function get_journal(page) {
        let url = `/get_journal_entries?page=${page}`;
        if (nb_per_page) {
            url += `&nb_per_page=${nb_per_page}`
        }

        fetch(url, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'  // Ajoute cet en-tête pour indiquer qu'il s'agit d'une requête AJAX
            }
        })
        .then(response => response.json())
        .then(data => {
            journal_content.innerHTML = '';
            journal_container.style.display = 'flex';
            journal_container.style.opacity = '100%';

            journal_page_number.innerHTML = `${page_number}/${data.data.n_pages}`;


            data.data.all_journal_entries.forEach(entry => {
                add_entry(entry);
            })

            if (data.data.can_decrease_page === false) {
                decrease_page.style.cursor = 'default';
                decrease_page.style.color = 'gray';
                can_decrease_page = false
            }
            else {
                decrease_page.style.cursor = 'pointer';
                decrease_page.style.color = 'black';
                can_decrease_page = true;
            }

            if (data.data.can_increase_page === false) {
                increase_page.style.cursor = 'default';
                increase_page.style.color = 'gray';
                can_increase_page = false;
            }
            else {
                increase_page.style.cursor = 'pointer';
                increase_page.style.color = 'black';
                can_increase_page = true;
            }


            // Manage icons
            let notifying_journal_entrytypes = (data.data.notifying_journal_entrytypes)
            console.log("notifs : ", notifying_journal_entrytypes)
            list_icons.forEach(icon => {
                
                if (notifying_journal_entrytypes.includes(icon.getAttribute('label'))) {
                    icon.style.opacity = '100%';
                } 
                else {
                    icon.style.opacity = '30%';
                }
            })

        })

    }

    const tooltip = document.getElementById('tooltip');
    let tooltipTimeout;

    function show_tooltip(label, e) {

        tooltipTimeout = setTimeout(() => {
            console.log(e, e.x, e.y);
            tooltip.innerHTML = label;
            tooltip.style.left = `${e.clientX + 10}px`;
            tooltip.style.top = `${e.clientY + 10}px`;
            tooltip.style.opacity = "100%";
        }, 400); // Affiche après 1 seconde
        

    }

    



    // Get number of notifications
    let badge = document.getElementById('badge');
    let nb_notifications;
    
    fetch(`/get_notifications_number/`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',  // Ajoute cet en-tête pour indiquer qu'il s'agit d'une requête AJAX
        }
    })
    .then(response => response.json())
    .then(data => {
        nb_notifications = data.data.nb_notifications;
        console.log(data);
        if (nb_notifications > 0) {
            badge.innerHTML = nb_notifications;
            badge.style.display = 'block';
        }
        else {
            badge.style.display = 'none';
        }

    })






    const list_icons = document.getElementById('icons').querySelectorAll('i');

    list_icons.forEach(icon => {
        
        // Event click
        icon.addEventListener('click', function() {

            fetch(`/manage_notification_entry/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken,
    
                },
                body: JSON.stringify({'label' : icon.getAttribute('label')}),
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                get_journal(page_number);
            })

        })


        // Tooltip
        icon.addEventListener('mouseenter', function(e) {
            
            show_tooltip(icon.getAttribute('label'), e);

        })

        icon.addEventListener('mouseleave', function() {
            clearTimeout(tooltipTimeout);
            console.log("out");
            tooltip.style.opacity = "0%";
        })

    })



    

    const input_number = document.getElementById('input-number');
    let page_number = 1;
    let n_pages;
    let can_increase_page = false;
    let can_decrease_page = false;
    const open_journal = document.getElementById('open-journal');
    const journal_container = document.getElementById('journal-container');
    const journal_content = document.getElementById('journal-content');
    const increase_page = document.getElementById('journal-increase-page');
    const decrease_page = document.getElementById('journal-decrease-page');
    const journal_page_number = document.getElementById('journal-page-number');


    open_journal.addEventListener('click', function() {
        badge.style.display = 'none';
        assombrirPage(journal_container);
        get_journal(page_number);
                
    })

    
    increase_page.addEventListener('click', function() {

        if (can_increase_page) {
            page_number += 1;
            get_journal(page_number)
        }
        
    })


    decrease_page.addEventListener('click', function() {

        if (can_decrease_page) {
            page_number -= 1;
            get_journal(page_number)
        }
        
    })

    let nb_per_page;
    input_number.addEventListener('change', function() {
        nb_per_page = input_number.value;
        page_number = 1;
        get_journal(page_number);
    })

})