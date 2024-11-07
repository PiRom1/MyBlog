document.addEventListener('DOMContentLoaded', function () {

    bg = document.getElementById('bg').getAttribute('bg');

    if (bg) {
        document.body.style.backgroundImage = `url(${bg})`;
    }

})