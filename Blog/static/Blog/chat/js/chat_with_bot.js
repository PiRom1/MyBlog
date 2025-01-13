document.addEventListener('DOMContentLoaded', async function () {

    let answer = document.getElementById('answer');
    let message = document.getElementById('message');
    const form = document.getElementById('messageForm');


    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));



    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            form.submit();
        }
    })



    
    if (message.innerHTML === '') {
        message.style.display = 'none';    
    }

    if (answer.innerHTML === '') {
        answer.style.display = 'none';
    }

    else {
        const answer_text = answer.innerHTML;
        answer.innerHTML = '';
        for (let i = 0; i < answer_text.length; i++) {
            answer.innerHTML += answer_text[i];
            await sleep(5);
        }
    }

})
    