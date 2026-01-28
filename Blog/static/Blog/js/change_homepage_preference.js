document.addEventListener('DOMContentLoaded', function () {
    console.log('ici')
    const csrftoken = document.querySelector('[name=csrf-token]').content;

    const change_homepage = document.getElementById("change_homepage_preference");

    change_homepage.addEventListener('click', function() {

        console.log('clic')

        
        fetch('/change_homepage_preference/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken  // Récupération du token CSRF
            },
            body: JSON.stringify({})
        }).then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.reload();
            }
        })
    })

    

})