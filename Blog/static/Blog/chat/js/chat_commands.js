// message_verification.js

// const { act } = require("react");

document.addEventListener('DOMContentLoaded', function () {

    const csrftoken = document.querySelector('[name=csrf-token]').content;

    // ---------------------------------------------------------------
    // Attente de l'initialisation de CKEditor (window.editorInstance)
    // ---------------------------------------------------------------
    function attendreEditeur(callback) {
        if (window.editorInstance) {
            callback(window.editorInstance);
        } else {
            setTimeout(() => attendreEditeur(callback), 100);
        }

    }


    // ---------------------------------------------------------------
    // Remplit et positionne le menu au-dessus du curseur
    // ---------------------------------------------------------------
    function fill_commands(commands) {

        const view = window.editorInstance.editing.view;

        command_input.innerHTML = '';

        let i = 1;

        commands.forEach(command_name => {
            let command = document.createElement('div');
            command.classList.add('command-line');
            command.setAttribute('index', i);
            if (i === 1) {
                command.classList.add('selected-command-line');
            }

            // En mode emoji, affiche la vignette devant le nom
            if (mode === 'emoji') {
                let img = document.createElement('img');
                img.src = emojis[command_name];
                img.width = 30;
                img.height = 30;
                img.style.verticalAlign = 'middle';
                img.style.marginRight = '6px';
                command.appendChild(img);
            }
            // En mode tag, affiche l'avatar de l'utilisateur
            else if (mode === 'tag' || mode === 'bot') {
                let img = document.createElement('img');
                img.src = session_users[command_name]['url'];
                img.width = 30;
                img.height = 30;
                img.style.verticalAlign = 'middle';
                img.style.marginRight = '6px';
                command.appendChild(img);
            }

            let label = document.createElement('span');
            label.textContent = command_name;
            command.appendChild(label);

            // Badge (bot) en italique, purement indicatif
            if (mode === 'tag' && session_users[command_name]['is_bot']) {
                let bot_badge = document.createElement('span');
                bot_badge.textContent = ' (bot)';
                bot_badge.style.fontStyle = 'italic';
                bot_badge.style.opacity = '0.6';
                bot_badge.style.fontSize = '12px';
                command.appendChild(bot_badge);
            }
            command.addEventListener('mousedown', function (e) {
                e.preventDefault();   // empêche le clic de prendre le focus à l'éditeur
            });

            command.addEventListener('click', function (e) {
                e.stopPropagation();

                const current = command_input.querySelector('.selected-command-line');
                if (current) current.classList.remove('selected-command-line');
                command.classList.add('selected-command-line');
                document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }));
            });
            command.addEventListener('mouseenter', function () {
                const current = command_input.querySelector('.selected-command-line');
                if (current) current.classList.remove('selected-command-line');
                command.classList.add('selected-command-line');
            });

            command_input.appendChild(command);

            i += 1;
        });

        const domConverter = view.domConverter;
        const viewSelection = view.document.selection;
        const domRange = domConverter.viewRangeToDom(viewSelection.getFirstRange());

        let rect = domRange.getBoundingClientRect();

        // Cas du paragraphe vide : le range retourne un rect nul
        if (rect.width === 0 && rect.height === 0 && rect.top === 0 && rect.left === 0) {
            const node = domRange.startContainer;
            // startContainer peut être un noeud texte ou un élément
            const element = node.nodeType === Node.ELEMENT_NODE ? node : node.parentElement;
            rect = element.getBoundingClientRect();
        }

        command_input.classList.add('visible');
        command_input.style.left = (rect.left + window.scrollX) + 'px';
        command_input.style.top = (rect.top + window.scrollY - command_input.offsetHeight - 6) + 'px';

    }


    // ---------------------------------------------------------------
    // Ferme le menu et remet l'état à zéro
    // ---------------------------------------------------------------
    function fermer_menu() {
        command_input.classList.remove('visible');
        written_command = '';
        mode = 'command';
        tag_par_arobase = false;
        emoji_par_deux_points = false;
    }

    // ---------------------------------------------------------------
// /get_diplodocoins : la prison des fraudeurs fiscaux
// ---------------------------------------------------------------
    function afficher_prison() {

        // Overlay plein écran
        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: fixed;
            inset: 0;
            z-index: 99999;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: flash-fond 0.3s infinite;
        `;

        // Les barreaux de prison (répétition de bandes verticales)
        const barreaux = document.createElement('div');
        barreaux.style.cssText = `
            position: absolute;
            inset: 0;
            background: repeating-linear-gradient(
                90deg,
                rgba(20, 20, 20, 0.95) 0px,
                rgba(60, 60, 60, 0.95) 12px,
                rgba(20, 20, 20, 0.95) 24px,
                transparent 24px,
                transparent 90px
            );
            pointer-events: none;
        `;

        // Le message
        const message = document.createElement('div');
        message.textContent = '🚨 FRAUDEUR DIPLOFISCAL 🚨';
        message.style.cssText = `
            font-size: 8vw;
            font-weight: 900;
            color: white;
            text-shadow: 0 0 20px red, 0 0 40px red;
            text-align: center;
            animation: tremblement 0.1s infinite;
            z-index: 1;
        `;

        const sous_message = document.createElement('div');
        sous_message.textContent = "On ne peut pas gagner des Diplodocoins comme ça.";
        if (is_quest_done) {
            sous_message.textContent += " Si tu veux des thunes, t'as qu'à revenir demain pour faire ta quête. Le gars on lui donne ça il nous prend ça !"
        }
        else {
            sous_message.textContent += " Va plutôt faire tes quêtes au lieu de quémander, espèce d'assisté va !";
        }
        
        sous_message.style.cssText = `
            position: absolute;
            bottom: 15%;
            font-size: 2.5vw;
            color: yellow;
            text-shadow: 2px 2px 4px black;
            text-align: center;
            padding: 0 10%;
            z-index: 1;
        `;

        // Animations CSS injectées
        const style = document.createElement('style');
        style.textContent = `
            @keyframes flash-fond {
                0%   { background-color: #547687; }
                50%  { background-color: #00006a; }
                100% { background-color: #657687; }
            }
            @keyframes tremblement {
                0%   { transform: translate(2px, 1px) rotate(-0.5deg); }
                50%  { transform: translate(-2px, -1px) rotate(0.5deg); }
                100% { transform: translate(1px, 2px) rotate(0deg); }
            }
        `;

        overlay.appendChild(barreaux);
        overlay.appendChild(message);
        overlay.appendChild(sous_message);
        document.body.appendChild(style);
        document.body.appendChild(overlay);


        // Fetch endpoint de voleur fiscal

        fetch('/chat/fraude', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken  // Récupération du token CSRF
            },
            body: JSON.stringify({'user_id' : user_id, 'session_id' : session_id})
        }).then(response => response.json())
        .then(data => {
            console.log(data);
        })
    
        // Sirène sonore si tu as un son qui va bien dans la soundbox :
        // new Audio(user_sounds['sirene']).play();

        // Disparaît après 4 secondes, ou refresh au clic
        overlay.addEventListener('click', () => location.reload());
        setTimeout(() => { location.reload(); }, 4000);
    }


    // ---------------------------------------------------------------
    // Données
    // ---------------------------------------------------------------
    const data = document.getElementById('data');
    const commands = JSON.parse(data.getAttribute('commands'));

    // Construit {nom: url} à partir des images déjà présentes dans #emojis-list
    const emojis = {};
    document.querySelectorAll('#emojis-list img.emoji').forEach(img => {
        emojis[img.getAttribute('emoji_name')] = img.getAttribute('src');
    });
    const emoji_names = Object.keys(emojis);
    const session_users = JSON.parse(data.getAttribute('session_users'));
    const user_sounds = JSON.parse(data.getAttribute('user_sounds'));
    const pages = JSON.parse(data.getAttribute('pages'));
    const is_quest_done = {"True" : true, "False": false}[data.getAttribute("is_quest_done")];
    const user_id = data.getAttribute("user_id");
    const session_id = data.getAttribute("session_id");


    const command_input = document.getElementById('command-input');
    let written_command = '';
    let mode = 'command';          // 'command', 'emoji' ou 'tag'
    let tag_par_arobase = false;   // true si le menu tag a été ouvert en tapant '@'
    let emoji_par_deux_points = false;


    // Retourne la liste dans laquelle filtrer selon le mode courant
    function liste_courante() {
        if (mode === 'emoji') return emoji_names;
        if (mode === 'tag') return Object.keys(session_users);
        if (mode === 'bot') return Object.entries(session_users).filter(([name, infos]) => infos.is_bot).map(([name, infos]) => name);    
        if (mode === 'random') return ['0-1', '1-6', '1-10', '1-100'];
        if (mode === 'soundbox') return Object.keys(user_sounds);
        if (mode === 'kaomoji') return [
            '¯\\_(ツ)_/¯',
            '(╯°□°)╯︵ ┻━┻',
            '┬─┬ ノ( ゜-゜ノ)',
            '(づ｡◕‿‿◕｡)づ',
            '(ノ◕ヮ◕)ノ*:･ﾟ✧',
            '(◕‿◕✿)',
            '(｡♥‿♥｡)',
            'ಥ_ಥ',
            '(ง •̀_•́)ง',
            '( ͡° ͜ʖ ͡°)',
            '(=^･ω･^=)',
            '(⌐■_■)'
        ];
        if (mode == 'page') return Object.keys(pages);
        if (mode === 'help') return [
    'Échap : fermer le menu',
    '↑ ↓ : naviguer, Entrée : valider',
    '/tag : mentionner un membre (raccourci : @)',
    '/bot : mentionner un bot de la session',
    '/emoji : insérer un emoji (raccourci : :)',
    '/soundbox : jouer un son',
    '/random : tirer un nombre aléatoire',
    '/kaomoji : insérer un kaomoji (ツ)',
    '/get_diplodocoins : À toi la richesse !!! (Hmmm ?)',
    '/help : afficher cette aide',
];
        return commands;
    }


    // ---------------------------------------------------------------
    // Écouteurs
    // ---------------------------------------------------------------
    attendreEditeur(function (editor) {

        editor.editing.view.document.on('keydown', (evt, data) => {
            let key = data.domEvent.key;

            if (key === '/') {

                // Ouvrir le panel de commandes avec toutes les commandes
                mode = 'command';
                written_command = '';
                fill_commands(commands);

            }
            else if (key === '@') {

                // Ouvrir directement le panel des utilisateurs (le '@' reste dans le texte)
                mode = 'tag';
                written_command = '';
                tag_par_arobase = true;
                fill_commands(Object.keys(session_users));

            }
            else if (key === ':') {

                // Ouvrir directement le panel des emojis (le ':' reste dans le texte)
                mode = 'emoji';
                written_command = '';
                emoji_par_deux_points = true;
                fill_commands(emoji_names);
            }
            else if (key === 'Escape') {
                fermer_menu();
            }
            else if (key === 'Backspace') {
                if (!command_input.classList.contains('visible')) {
                    return;
                }
                if (data.domEvent.ctrlKey) {
                    // Ctrl+Backspace : ferme le menu (et reset tout via fermer_menu)
                    fermer_menu();
                }
                else if (written_command.length === 0) {
                    fermer_menu();
                }
                else {
                    written_command = written_command.slice(0, -1);
                    let remaining_commands = liste_courante().filter(c => c.toLowerCase().startsWith(written_command.toLowerCase()));
                    fill_commands(remaining_commands);
                }
            }
        });


        document.addEventListener('keydown', function (e) {

            if ((e.key == 'Enter' || e.key == 'Tab') && command_input.classList.contains('visible')) {
                let selected = document.querySelector('.selected-command-line');
                if (!selected) {
                    fermer_menu();
                    return;
                }
                let active_command = selected.querySelector('span').textContent;

                const editor = window.editorInstance;

                if (mode === 'command') {

                    // Supprime le '/' + ce qui a été tapé (ex: "/em" = 1 + 2 caractères)
                    editor.model.change(writer => {
                        const position = editor.model.document.selection.getFirstPosition();
                        const debut = position.getShiftedBy(-(written_command.length + 1));
                        const range = writer.createRange(debut, position);
                        writer.remove(range);
                    });

                    if (active_command === 'emoji') {
                        // Passe en mode emoji : le même menu, rempli avec les emojis
                        mode = 'emoji';
                        written_command = '';
                        fill_commands(emoji_names);
                    }
                    else if (active_command === 'tag') {
                        // Passe en mode tag : pas de '@' dans le texte (le /tag a été supprimé)
                        mode = 'tag';
                        written_command = '';
                        tag_par_arobase = false;
                        fill_commands(Object.keys(session_users));
                    }
                    else if (active_command === 'bot') {
                        // Passe en mode bot : pas de '@' dans le texte (le /tag a été supprimé)
                        mode = 'bot';
                        written_command = '';
                        tag_par_arobase = false;
                        fill_commands(
                            Object.entries(session_users)
                                .filter(([name, infos]) => infos.is_bot)
                                .map(([name, infos]) => name)
                        );
                    }
                    else if (active_command === 'random') {
                        mode = 'random';
                        written_command = '';
                        tag_par_arobase = false;
                        fill_commands(liste_courante());
                    }
                    else if (active_command === 'soundbox') {
                        // Passe en mode Soundbox
                        mode = 'soundbox';
                        written_command = '';
                        fill_commands(liste_courante());
                    }
                    else if (active_command === 'kaomoji') {
                        // Mode kaomoji
                        mode = 'kaomoji';
                        written_command = '';
                        fill_commands(liste_courante());
                    }
                    else if (active_command === 'help') {
                        // Mode help
                        mode = 'help';
                        written_command = '';
                        fill_commands(liste_courante());
                    }
                    else if (active_command === 'page') {
                        // Mode page
                        mode = 'page';
                        written_command = '';
                        fill_commands(liste_courante());
                    }
                    else if (active_command === 'get_diplodocoins') {
                        fermer_menu();
                        afficher_prison();
                    }
                    else {
                        // Les autres commandes : rien pour l'instant
                        console.log('Commande : ', active_command);
                        fermer_menu();
                    }

                }
                else if (mode === 'emoji') {

                    const url = emojis[active_command];

                    editor.model.change(writer => {
                        // Supprime le filtre tapé + le ':' s'il vient du clavier
                        const a_supprimer = written_command.length + (emoji_par_deux_points ? 1 : 0);
                        if (a_supprimer > 0) {
                            const position = editor.model.document.selection.getFirstPosition();
                            const debut = position.getShiftedBy(-a_supprimer);
                            writer.remove(writer.createRange(debut, position));
                        }

                        // Insère l'emoji comme dans insertAtCursor
                        const imageElement = writer.createElement('imageInline', {
                            src: url,
                            alt: 'emoji',
                        });
                        editor.model.insertContent(imageElement, editor.model.document.selection);
                    });

                    fermer_menu();
                }
                else if (mode === 'tag' || mode === 'bot') {

                    editor.model.change(writer => {
                        const position = editor.model.document.selection.getFirstPosition();

                        // Supprime le filtre tapé + le '@' s'il vient du clavier
                        const a_supprimer = written_command.length + (tag_par_arobase ? 1 : 0);
                        if (a_supprimer > 0) {
                            const debut = position.getShiftedBy(-a_supprimer);
                            writer.remove(writer.createRange(debut, position));
                        }

                        // Insère la mention : @pseudo
                        writer.insertText('@' + active_command + ' ', editor.model.document.selection.getFirstPosition());
                    });

                    fermer_menu();
                }
                else if (mode === 'random') {
                    const [min, max] = active_command.split('-').map(Number);
                    const random_number = Math.floor(Math.random() * (max - min + 1)) + min;

                    editor.model.change(writer => {
                    // Supprime le filtre tapé (ex: "1-1" si l'utilisateur a filtré)
                    if (written_command.length > 0) {
                        const position = editor.model.document.selection.getFirstPosition();
                        const debut = position.getShiftedBy(-written_command.length);
                        writer.remove(writer.createRange(debut, position));
                    }

                    // Insère le résultat
                    writer.insertText('🎲 [' + active_command + '] : ' + random_number + ' ',
                                    editor.model.document.selection.getFirstPosition());
                });
                fermer_menu(); 
                }
                else if (mode === 'soundbox') {
                    editor.model.change(writer => {
                    // Supprime le filtre tapé (ex: "1-1" si l'utilisateur a filtré)
                    if (written_command.length > 0) {
                        const position = editor.model.document.selection.getFirstPosition();
                        const debut = position.getShiftedBy(-written_command.length);
                        writer.remove(writer.createRange(debut, position));
                    }

                    // Jouer le son
                    if (active_command == 'Son aléatoire') {
                        const sound_names = Object.keys(user_sounds).filter(name => name !== 'Son aléatoire');
                        active_command = sound_names[Math.floor(Math.random() * sound_names.length)];
                        }
                    new Audio(user_sounds[active_command]).play();
                });
                fermer_menu(); 
                }
                else if (mode === 'kaomoji') {

                    editor.model.change(writer => {
                        const position = editor.model.document.selection.getFirstPosition();

                        // Supprime le filtre tapé + le '@' s'il vient du clavier
                        const a_supprimer = written_command.length + (tag_par_arobase ? 1 : 0);
                        if (a_supprimer > 0) {
                            const debut = position.getShiftedBy(-a_supprimer);
                            writer.remove(writer.createRange(debut, position));
                        }

                        // Insère la mention : @pseudo
                        writer.insertText(active_command, editor.model.document.selection.getFirstPosition());
                    });

                    fermer_menu();
                }
                else if (mode === 'help') {
                    fermer_menu();

                }
                else if (mode === 'page') {
                    fermer_menu();
                    window.location.href = pages[active_command];
                }
                e.preventDefault();
            }
            else if (e.key == 'ArrowDown' && command_input.classList.contains('visible')) {
                let active_command = document.querySelector('.selected-command-line');
                active_command.classList.remove('selected-command-line');

                let command_lines = document.getElementsByClassName('command-line');

                // index actuel (attribut 'index' commence à 1)
                let current_index = parseInt(active_command.getAttribute('index'));

                // index suivant, retour à 1 après la dernière commande
                let next_index = current_index + 1;
                if (next_index > command_lines.length) {
                    next_index = 1;
                }

                let new_active_command = document.querySelector('.command-line[index="' + next_index + '"]');
                new_active_command.classList.add('selected-command-line');
                new_active_command.scrollIntoView({ block: 'nearest' });

                e.preventDefault();
            }
            else if (e.key == 'ArrowUp' && command_input.classList.contains('visible')) {
                let active_command = document.querySelector('.selected-command-line');
                active_command.classList.remove('selected-command-line');

                let command_lines = document.getElementsByClassName('command-line');

                // index actuel (attribut 'index' commence à 1)
                let current_index = parseInt(active_command.getAttribute('index'));

                // index précédent, retour à la fin avant la première commande
                let next_index = current_index - 1;
                if (next_index <= 0) {
                    next_index = command_lines.length;
                }

                let new_active_command = document.querySelector('.command-line[index="' + next_index + '"]');
                new_active_command.classList.add('selected-command-line');
                new_active_command.scrollIntoView({ block: 'nearest' });

                e.preventDefault();
            }
            else if (command_input.classList.contains('visible') && e.key !== '/' && e.key !== '@' && e.key !== ':') {
                if (e.key.length === 1) {           // vrai caractère (a, b, 1, é...)
                    written_command += e.key;
                    let remaining_commands = liste_courante().filter(c => c.toLowerCase().startsWith(written_command.toLowerCase()));
                    if (remaining_commands.length >= 1) {
                        fill_commands(remaining_commands);
                    }
                    else {
                        written_command = '';
                        fermer_menu()
                    }
                }
            }
        })

        
        document.addEventListener('keydown', function (e) {
            if (e.key !== '/' || command_input.classList.contains('visible')) return;
            if (editor.editing.view.document.isFocused) return;
            if (e.target.closest('input, textarea, [contenteditable]')) return;

            e.preventDefault();
            editor.editing.view.focus();
            editor.model.change(writer => {
                editor.model.insertContent(writer.createText('/'));
            });

            mode = 'command';
            written_command = '';
            fill_commands(commands);
        });

        // Ferme le menu si on clique ailleurs
        document.addEventListener('click', function (e) {
            if (!command_input.contains(e.target)) {
                fermer_menu();
            }
        });

    });


    

});