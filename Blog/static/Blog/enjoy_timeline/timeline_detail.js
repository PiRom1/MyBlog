document.addEventListener('DOMContentLoaded', function () {

    const comment_text = document.querySelector('label[for="id_comment"]');
    comment_text.innerHTML = '';


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
        h1.innerHTML = `${hour}h ${minute}mn`;
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



})