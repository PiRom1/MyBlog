document.addEventListener('DOMContentLoaded', function () {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    const objectives = document.querySelectorAll('.objective');
    let all_achieved = true;

    objectives.forEach(objective => {
        const objective_value = objective.getAttribute("objective_value");
        const current_value = objective.getAttribute("current_value");
        
        if (objective_value === current_value) {
            objective.style.textDecoration = 'line-through';
        }

        if (objective.getAttribute("achieved") === 'False') {
            all_achieved = false;
        }
        
    })

    if (all_achieved) {  // Si tous les objectifs ont été atteints.
        console.log('fini');
    }
    else {
        console.log("pas fini");
    }

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
      }

    async function displayWithDelay(quest_text, quest_text_span) {
    for (const text of quest_text) {
        quest_text_span.innerHTML += `${text} `;
        await sleep(50);  // Pause de 100 ms
    }
    }
    // Manage quest_text
    const quest_text_span = document.getElementById("quest-text");
    let quest_text = quest_text_span.innerHTML.split(" ");
    quest_text = quest_text.filter(item => item !== "");
    quest_text_span.innerHTML = '';

    displayWithDelay(quest_text, quest_text_span);




    // Achieved button
    const achieved_button = document.getElementById("achieved-button");

    if (achieved_button) {
        achieved_button.addEventListener('click', function() {
            
            fetch('/quêtes/achieved', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,  // Récupération du token CSRF
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({})
            }).then(response => response.json())
            .then(data => {
                console.log(data.success);
                if (data.success) {
                window.location.href = "/quêtes";
                }
            })
        })
    }



    // Pending quests

    const pending_quests = document.querySelectorAll(".pending-quest");
    console.log(pending_quests);

    pending_quests.forEach(quest => {

        quest.addEventListener('click', function() {

            const id = quest.getAttribute("id");

            fetch('/quêtes/accept', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,  // Récupération du token CSRF
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({id})
            }).then(response => response.json())
            .then(data => {
                console.log(data.success);
                if (data.success) {
                window.location.href = "/quêtes";
                }
            })
        


        })


    })
    

})