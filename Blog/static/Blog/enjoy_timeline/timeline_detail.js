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


})