document.addEventListener('DOMContentLoaded', function () {

    bg = document.getElementById('bg').getAttribute('bg');
    console.log('bg : ', bg);
    if (bg != 'None') {
        document.body.style.backgroundImage = `url(${bg})`;
    }

})