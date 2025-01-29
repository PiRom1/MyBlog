document.addEventListener('DOMContentLoaded', async function () {

    const leaderboards = document.querySelectorAll('.leaderboard');
    const show_leaderboards = document.querySelectorAll('.show_leaderboard');


    show_leaderboards.forEach(item => {
        item.addEventListener('click', function() {
            leaderboards.forEach(leaderboard => {
                if (leaderboard.getAttribute('name') !== item.getAttribute('name')) {
                    leaderboard.style.display = 'none';
                }
                else {
                    leaderboard.style.display = 'block';
                }
            })
        })
    })

});