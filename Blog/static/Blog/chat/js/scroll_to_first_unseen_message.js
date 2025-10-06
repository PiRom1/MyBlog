document.addEventListener('DOMContentLoaded', () => {
    const data = document.getElementById('data');
    const id = data?.getAttribute('first_unseen_message_id');
    if (!id) return;

    setTimeout(() => {
        const first_unseen_message = document.querySelector(`div.message[id_message="${id}"]`);
        const offset = 200;
        const topPos = first_unseen_message.getBoundingClientRect().top + window.pageYOffset;
        // scroll avec marge
        if (first_unseen_message) {
            first_unseen_message.insertAdjacentHTML('beforebegin', '<div style="text-align: center; font-weight:bold; margin:7px;">MESSAGES NON LUS</div>');
            window.scrollTo({ top: topPos - offset, behavior: 'smooth' });
        }
    }, 50);
});
