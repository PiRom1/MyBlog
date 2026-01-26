document.addEventListener('DOMContentLoaded', function () {

    let bg = document.getElementById('bg').getAttribute('bg');
    if (bg != 'None') {
        document.body.style.backgroundImage = `url(${bg})`;
    }

})