document.addEventListener('DOMContentLoaded', function () {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    const comment_text = document.querySelector('label[for="id_comment"]');
    comment_text.innerHTML = '';
    let check_666 = [false, false, false];
    
    let form = document.getElementById('form');

    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            form.submit();
        }
    })


    // Manage datetimes
    const moisFrancais = [
        "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
        "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
      ];

    var datetimes = document.querySelectorAll('.date');
    datetimes.forEach(item => {
        
        const formatted_datetime = item.innerHTML.split(',')[0] + item.innerHTML.split(',')[1];
        const dateObj = new Date(formatted_datetime);

        const jour = dateObj.getDate(); 
        const mois = moisFrancais[dateObj.getMonth()]; 
        const annee = dateObj.getFullYear(); 
        item.innerHTML = `${jour} ${mois} ${annee}`

    })

    // Modify input form
    const note_label = document.querySelector('label[for="id_note"]');
    note_label.innerHTML = "Note (sur 5) : ";

    const note_form = document.getElementById('id_note');
    note_form.style.width = '3%';
    note_form.value = 1;

    note_form.addEventListener('change', function() {
        console.log(note_form.value);
        if (note_form.value < 1) {
            note_form.value = 1;
        }
        if (note_form.value > 5) {
            note_form.value = 5;
        }
    })


    document.addEventListener('wheel', function(e) {
        let note = parseInt(note_form.value);
        if (e.deltaY > 0 && note > 1) {
            note -= 1;
        }
        if (e.deltaY < 0 && note < 5) {
            note += 1;
        }

        note_form.value = note;

    })
    




    // Manage non existent hour minutes
    const url = window.location.href;
    const splitted_url = url.split('/');
    const minute = splitted_url[splitted_url.length - 2];
    const hour = splitted_url[splitted_url.length - 3];

    console.log('hour : ', hour, "mionute : ", minute);

    if (minute < 0 || minute > 59 || hour < 0 || hour > 23) {
        console.log("nope");
        document.body.innerHTML = '';
        const date = new Date();

        const h1 = document.createElement("h1");

        if (hour == 6 && minute == 66) {
            
            const hour = document.createElement("span");
            hour.id = "hour";
            hour.textContent = "6";
            
            const minute1 = document.createElement("span");
            minute1.id = "minute1";
            minute1.textContent = "6";
            
            const minute2 = document.createElement("span");
            minute2.id = "minute2";
            minute2.textContent = "6";
            h1.append(hour, "h ", minute1, minute2, "mn");

            hour.addEventListener('click', function() {
                hour.innerHTML = '𝟔̸';
                check_666[0] = true;
            })

            minute1.addEventListener('click', function() {
                minute1.innerHTML = '𝟔̸';
                check_666[1] = true;

            })

            minute2.addEventListener('click', function() {
                minute2.innerHTML = '𝟔̸';
                check_666[2] = true;

            })

        }
        else if (hour == 66 && minute == 6) {
            console.log('làà');
            const hour1 = document.createElement("span");
            hour1.id = "hour1";
            hour1.textContent = "6";
            

            const hour2 = document.createElement("span");
            hour2.id = "hour2";
            hour2.textContent = "6";
            
            const minute = document.createElement("span");
            minute.id = "minute";
            minute.textContent = "6";

            h1.append(hour1, hour2, "h ", minute, "mn");

            
            hour1.addEventListener('click', function() {
                hour1.innerHTML = '𝟔̸';
                check_666[0] = true;

            })

            hour2.addEventListener('click', function() {
                hour2.innerHTML = '𝟔̸';
                check_666[1] = true;

            })

            minute.addEventListener('click', function() {
                minute.innerHTML = '𝟔̸';
                check_666[2] = true;

            })

        }
        else {
        h1.innerHTML = `${hour}h ${minute}mn`;
        }
        document.body.appendChild(h1);

        const h3 = document.createElement("h3");
        h3.innerHTML = `Petit malin va ... Cette heure n'existe pas et tu le sais très bien !`;
        document.body.appendChild(h3);

        const h4 = document.createElement("h4");
        h4.innerHTML = `Alors arrête les clowneries et va vraiment remplir la timeline, il y a encore du pain sur la planche !`;
        document.body.appendChild(h4);

        const link = document.createElement("a");
        link.href= `/enjoy_timeline/${date.getHours()}/${date.getMinutes()}/`;
        link.text = `${date.getHours()}h${date.getMinutes()} n'est pas encore rempli par exemple !`;
        document.body.appendChild(link);

    }


    document.addEventListener('click', function() {
        const allTrue = check_666.every(item => item === true);
        if (allTrue) {
            console.log('TRUE !');
            document.body.innerHTML = '';
            check_666 = [false, false, false];

            // Show gain + bouton
            let titre = document.createElement("h1");
            titre.innerHTML = `Durant de longues années, le Modéraptor Dissident t'as observé.`;
            let paragraph = document.createElement("p");
            paragraph.innerHTML = `Il a été témoin de tes actions, a reconnu ta bravoure et ta vertue.<br>Démiurge des temps anciens, il te reconnait aujourd'hui comme son maître.<br>Sois digne de sa confiance et propage à ton tour la sainte parole comme il l'a fait pendant l'éternité passée.`;
            paragraph.style.textAlign = 'center';

            let bouton = document.createElement('button');
            bouton.textContent = 'Accepter le Modéraptor Dissident en votre sein';
            bouton.style.textAlign = 'center';
            bouton.style.position = 'absolute';
            bouton.style.left = '40%';
            bouton.style.paddingTop = '5px';

            document.body.appendChild(titre);
            document.body.appendChild(paragraph);
            document.body.appendChild(bouton);

            document.body.style.backgroundImage = "url('/static/img/raptor.gif')";
            
            bouton.addEventListener('click', function() {
                
                fetch("/get_moderaptor/", {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,  // Obtenez le token CSRF
                    },
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Mise à jour réussie:', data);
                        window.location.href = '/';
                    })
                    .catch(error => {
                        console.error('Erreur:', error);
                    });

                    })

        }

    })

    


})