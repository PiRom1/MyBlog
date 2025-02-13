document.addEventListener('DOMContentLoaded', function () {

    const id_pari = document.getElementById('id-pari').getAttribute('id-pari');
    const is_open = document.getElementById('is-open').getAttribute('is-open');
    const error_message = document.getElementById('error-message');

    const duree_atteinte = document.getElementById('duree-atteinte').getAttribute('duree-atteinte');

    const issues = document.querySelectorAll('.issue_text');
    const details = document.querySelectorAll('.issue_detail');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const mise_possible = document.getElementById('mise-possible').getAttribute('mise-possible');
    console.log(mise_possible);

    details[0].style.display = 'block';
    
    issues.forEach(issue => {
        console.log(issue);
        issue.addEventListener('click', function() {

            details.forEach(detail => {
                detail.style.display = 'none';
            })

            let detail = document.getElementById(`issue_detail_${issue.getAttribute('issue-id')}`);
            detail.style.display = 'block';

        })
    })



    // Gérer le pari (formulaire)

    const plus = document.querySelectorAll('.issue_add');
    const form = document.getElementById('pari_form');
    const form_name = document.getElementById('pari_form_name');
    const form_mise = document.getElementById('input_mise');
    const form_commentaire = document.getElementById('input_commentaire');

    let id_issue;
    const blur_background = document.getElementById('blur-background')
    console.log("blur : ", blur_background);
    plus.forEach(plus_=>{
        
        if (mise_possible === 'True' && is_open === 'True' && duree_atteinte === 'False') {
            plus_.addEventListener('click', function() {

                // blur_background.style.backdropFilter = 'blur(2px)';
                

                id_issue = plus_.getAttribute('issue-id');
                const issue_text = document.getElementById(`issue_${id_issue}`);
                document.getElementById('pari_form_name').innerHTML = issue_text.innerHTML;
                form.style.display = 'block';


            })
        }
        else {
            plus_.style.display = 'none';
            // plus_.style.background ='rgba(104, 40, 40, 0.663)';
        }
        
    })


    const close = document.getElementById('close');

    close.addEventListener('click', function() {
        form.style.display = 'none';
    })


    const submit = document.getElementById('submit');

    submit.addEventListener('click', function() {
        

            
        fetch('/parier/', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken // Inclure le token CSRF pour la sécurité
            },
            body: JSON.stringify({
                id_issue: id_issue,
                mise: form_mise.value,
                commentaire: form_commentaire.value
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.success === false) {
                const error = data.error;
                error_message.innerHTML = error;
            }
            else {
                window.location.reload();
            }

        })
        .catch(error => {
            console.error('Erreur lors de la requête:', error);
        });

    })


    // Admin validation
    console.log('open : ', is_open);
    if (is_open === 'True') {
        const is_admin = document.getElementById('is-admin').getAttribute('is-admin');
        const validate_issue = document.getElementById('validate-issue');
        let winning_issue;

        if (is_admin === 'True') {

            issues.forEach(issue => {
                console.log(issue);
                issue.addEventListener('contextmenu', function(e) {
                    winning_issue = issue.getAttribute('issue-id');
                    e.preventDefault();
                    
                    validate_issue.style.position = 'absolute';
                    validate_issue.style.left = `${e.clientX}px`;
                    validate_issue.style.top = `${e.clientY}px`;
                    validate_issue.style.display = 'block';

                    setTimeout(() => {
                        validate_issue.style.display = 'none';
                    }, 1000);

                    
                })
            })



            validate_issue.addEventListener('click', function() {

                
                
            fetch('/conclure_pari/', {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken // Inclure le token CSRF pour la sécurité
                },
                body: JSON.stringify({'id_pari' : id_pari,
                                    'winning_issue' : winning_issue
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                if (data.success === false) {
                    console.log(error);
                }
                else {
                    window.location.reload();
                }

            })
            .catch(error => {
                console.error('Erreur lors de la requête:', error);
            });




            })
        }
    }

    console.log('ici');
    const ctx = document.getElementById('pie-chart').getContext('2d');
    const data = document.getElementById('data');
    let labels = data.getAttribute('labels');
    console.log("labels : ", labels);
    // labels = labels.replace(/'/g, '"');
    let cotes = data.getAttribute('cotes').replace(/'/g, '"');
    console.log(labels);
    labels = JSON.parse(labels);
    cotes = JSON.parse(cotes);
    console.log("labels, cotes : ", labels, cotes);


    const chart_data = {
        labels: labels,
        datasets: [{
            data: cotes, // Proportions
        }]
    };

    new Chart(ctx, {
        type: 'pie',
        data: chart_data,
        options: {
            plugins: {
                legend: {
                    labels: {
                        color: 'white' // Texte des labels en blanc
                            }
                        }
                    }
                }

    });






});
