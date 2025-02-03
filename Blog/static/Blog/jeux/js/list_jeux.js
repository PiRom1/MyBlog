document.addEventListener('DOMContentLoaded', async function () {

    const leaderboards = document.querySelectorAll('.leaderboard');
    const show_leaderboards = document.querySelectorAll('.show_leaderboard');
    const game_selector = document.getElementById('game-selector');
    const timedelta_selector = document.getElementById('timedelta-selector');

    function filter_leaderboards() {
        leaderboards.forEach(leaderboard => {
            if ( (leaderboard.getAttribute('name') === game_selector.value) && (leaderboard.getAttribute('timedelta') === timedelta_selector.value) ) {
                leaderboard.style.display = 'block';
            }
            else {
                leaderboard.style.display = 'none';
            }
        });
    };

    filter_leaderboards();


    show_leaderboards.forEach(item => {
        item.addEventListener('click', function() {
            game_selector.value = item.getAttribute('name');
            filter_leaderboards();
        })
    })


    game_selector.addEventListener('change', function() {
        filter_leaderboards();
    })


    timedelta_selector.addEventListener('change', function() {
        filter_leaderboards();
    })

});