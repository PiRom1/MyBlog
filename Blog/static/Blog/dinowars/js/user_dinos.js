document.addEventListener('DOMContentLoaded', function() {
    const dinosGrid = document.getElementById('dinosGrid');
    const dinoCards = Array.from(dinosGrid.getElementsByClassName('dino-card'));

    // Check if there's a dino to show
    const dinoToShow = localStorage.getItem('showDinoAfterLoad');
    if (dinoToShow) {
        showDinoDetails(dinoToShow);
        localStorage.removeItem('showDinoAfterLoad');
    }

    // Sort dinos by level (descending) and then by name
    dinoCards.sort((a, b) => {
        const levelA = parseInt(a.dataset.level);
        const levelB = parseInt(b.dataset.level);
        
        if (levelA !== levelB) {
            return levelB - levelA; // Sort by level descending
        }
        
        // If levels are equal, sort by name
        const nameA = a.dataset.name.toLowerCase();
        const nameB = b.dataset.name.toLowerCase();
        return nameA.localeCompare(nameB);
    });

    // Reorder the elements in the DOM
    dinoCards.forEach(card => dinosGrid.appendChild(card));

    initializeDinoCards();
});

function openEditTeamPopup(teamId = null) {
    const popup = document.getElementById('editTeamPopup');
    const content = document.getElementById('editTeamContent');
    
    const url = teamId ? `/dinowars/edit_team/${teamId}/` : '/dinowars/edit_team/';
    
    fetch(url, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.text())
    .then(html => {
        content.innerHTML = html;
        popup.style.display = 'block';

        // Close popup handlers setup
        document.addEventListener('mousedown', handleClickOutside);
        document.addEventListener('keydown', handleEscKey);
        
        // Set up form submission and validation
        const form = content.querySelector('form');
        form.addEventListener('submit', handleTeamSubmit);
        
        // Setup form validation
        const submitButton = form.querySelector('button[type="submit"]');
        const teamNameInput = form.querySelector('#team_name');
        const dinoSelects = form.querySelectorAll('select');
        
        // Reset original options state
        window.originalOptions = null;
        
        // Initialize select options and constraints
        updateSelectOptions(dinoSelects);
        
        function validateForm() {
            const isTeamNameValid = teamNameInput.value.trim() !== '';
            const areAllDinosSelected = Array.from(dinoSelects).every(select => select.value !== '');
            submitButton.style.display = isTeamNameValid && areAllDinosSelected ? 'block' : 'none';
        }
        
        teamNameInput.addEventListener('input', validateForm);
        dinoSelects.forEach(select => {
            select.addEventListener('change', function() {
                updateSelectOptions(dinoSelects);
                validateForm();
            });
        });
        
        // Initial validation
        validateForm();
    });
}

function handleClickOutside(event) {
    const popup = document.getElementById('editTeamPopup');
    const content = document.getElementById('editTeamContent');
    
    if (popup && !content.contains(event.target)) {
        closeEditTeamPopup();
        document.removeEventListener('mousedown', handleClickOutside);
    }
}

function handleEscKey(event) {
    if (event.key === 'Escape') {
        closeEditTeamPopup();
        document.removeEventListener('keydown', handleEscKey);
    }
}

function updateSelectOptions(selects) {
    if (!window.originalOptions) {
        window.originalOptions = Array.from(selects).map(select => 
            Array.from(select.options).map(opt => opt.cloneNode(true))
        );
    }

    const selectedDinoInfo = Array.from(selects)
        .filter(s => s.value)
        .map(s => ({
            name: s.selectedOptions[0].text.split(' (')[0],
            select: s
        }));
    
    selects.forEach((select, index) => {
        const currentValue = select.value;
        const currentName = currentValue ? select.selectedOptions[0].text.split(' (')[0] : null;
        select.innerHTML = '';
        
        // Add back the empty option
        const emptyOption = window.originalOptions[index][0];
        select.appendChild(emptyOption.cloneNode(true));
        
        // Convert options to array for sorting
        const optionsToAdd = window.originalOptions[index]
            .filter(option => option.value)
            .map(option => {
                const match = option.text.match(/^(.+) \(Nv. (\d+)\)/);
                return {
                    option: option,
                    name: match[1],
                    level: parseInt(match[2])
                };
            })
            .sort((a, b) => {
                if (a.level !== b.level) {
                    return b.level - a.level; // Sort by level descending
                }
                return a.name.localeCompare(b.name); // Then by name
            });
        
        // Add sorted options back
        optionsToAdd.forEach(({ option, name }) => {
            // Check if this name is selected in other dropdowns
            const isNameSelectedInOthers = selectedDinoInfo.some(info => 
                info.name === name && info.select !== select
            );
            
            // Add option if not selected elsewhere or if it's the current selection
            if (!isNameSelectedInOthers || (currentName === name)) {
                select.appendChild(option.cloneNode(true));
            }
        });
        
        // Restore the current selection
        select.value = currentValue;
    });
}

function closeEditTeamPopup() {
    const popup = document.getElementById('editTeamPopup');
    popup.style.display = 'none';
    document.removeEventListener('mousedown', handleClickOutside);
    document.removeEventListener('keydown', handleEscKey);
}

function updateTeamDisplay(teamData) {
    const teamsContainer = document.querySelector('#teams-container');
    if (!teamsContainer) return;

    let teamBox;
    if (teamData.id) {
        teamBox = document.querySelector(`.team-box[data-team-id="${teamData.id}"]`);
        if (!teamBox) {
            teamBox = document.createElement('div');
            teamBox.className = 'team-box';
            teamBox.setAttribute('data-team-id', teamData.id);
            teamsContainer.appendChild(teamBox);
        }
    } else {
        console.error('Team data missing ID:', teamData);
        return;
    }

    teamBox.innerHTML = `
        <div class="team-header">
            <h3>${teamData.name}</h3>
            <div class="team-actions">
                ${teamData.in_arena ? 
                    `<span class="arena-warning">Equipe dans l'arène!</span>` :
                    `<button class="icon-btn edit-btn" onclick="openEditTeamPopup(${teamData.id})">
                        <i class="fas fa-pencil-alt"></i>
                    </button>
                    <button class="icon-btn delete-btn" onclick="deleteTeam(${teamData.id})">
                        <i class="fas fa-trash"></i>
                    </button>`
                }
            </div>
        </div>
        <div class="team-members">
            <div class="team-dino">${teamData.dino1.name} (Nv. ${teamData.dino1.level})</div>
            <div class="team-dino">${teamData.dino2.name} (Nv. ${teamData.dino2.level})</div>
            <div class="team-dino">${teamData.dino3.name} (Nv. ${teamData.dino3.level})</div>
        </div>
    `;
}

function handleTeamSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const teamId = form.dataset.teamId;
    const formData = new FormData(form);
    
    const url = teamId ? `/dinowars/edit_team/${teamId}/` : '/dinowars/edit_team/';
    
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Team updated:', data.team);
            updateTeamDisplay(data.team);
            closeEditTeamPopup();
        } else {
            alert(data.error || 'An error occurred while updating the team.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while updating the team.');
    });
}

function deleteTeam(teamId) {
    if (!confirm('Are you sure you want to delete this team?')) {
        return;
    }

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch(`/dinowars/delete_team/${teamId}/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const teamBox = document.querySelector(`.team-box[data-team-id="${teamId}"]`);
            if (teamBox) {
                teamBox.remove();
            }
        } else {
            alert(data.error || 'Failed to delete team');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while deleting the team');
    });
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function initializeDinoCards() {
    const dinoCards = document.querySelectorAll('.dino-card');
    dinoCards.forEach(card => {
        card.addEventListener('click', function() {
            const dinoId = this.getAttribute('data-dino-id');
            showDinoDetails(dinoId);
        });
    });
}

function showDinoDetails(dinoId) {
    const popup = document.getElementById('dinoDetailPopup');
    const content = document.getElementById('dinoDetailContent');
    
    fetch(`/dinowars/dino/${dinoId}/`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.text())
    .then(html => {
        content.innerHTML = html;
        popup.style.display = 'block';
        
        document.addEventListener('mousedown', handleDinoDetailClickOutside);
        document.addEventListener('keydown', handleDinoDetailEscKey);
    });
}

function closeDinoDetailPopup() {
    const popup = document.getElementById('dinoDetailPopup');
    popup.style.display = 'none';
    document.removeEventListener('mousedown', handleDinoDetailClickOutside);
    document.removeEventListener('keydown', handleDinoDetailEscKey);
}

function handleDinoDetailClickOutside(event) {
    const popup = document.getElementById('dinoDetailPopup');
    const content = document.getElementById('dinoDetailContent');
    
    if (popup && !content.contains(event.target)) {
        closeDinoDetailPopup();
    }
}

function handleDinoDetailEscKey(event) {
    if (event.key === 'Escape') {
        closeDinoDetailPopup();
    }
}

function openRunesPopup(dinoId) {
    const popup = document.getElementById('dinoDetailPopup');
    const content = document.getElementById('dinoDetailContent');
    
    fetch(`/dinowars/dino/${dinoId}/runes/`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.text())
    .then(html => {
        content.innerHTML = html;
        if (popup.style.display !== 'block') {
            popup.style.display = 'block';
            document.addEventListener('mousedown', handleDinoDetailClickOutside);
            document.addEventListener('keydown', handleDinoDetailEscKey);
        }
    });
}

function showInventory(slotType) {
    const inventoryPanel = document.querySelector('.inventory-panel');
    inventoryPanel.style.display = 'flex';
    inventoryPanel.dataset.currentSlot = slotType;
    equipped_item = document.querySelector(`.rune-slot[data-slot="${slotType}"] .slot-item-skin`).getAttribute('data');
    const currentItem = document.getElementById('currentItem');
    currentItem.textContent = equipped_item;
    currentItem.parentElement.parentElement.style.display = equipped_item !== 'None' ? 'block' : 'none';
    
    fetch(`/dinowars/inventory/runes/`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        const inventoryItems = document.querySelector('.inventory-items');
        inventoryItems.innerHTML = data.items.map(item => `
            <div class="inventory-item" onclick="equipRune(${item.id}, '${slotType}')">
                <span class="item-name">${item.name}</span>
                <span class="item-rarity ${getRarityClass(item.rarity)}">${item.rarity}</span>
            </div>
        `).join('');
    });
}

function getIconClass(slotType) {
    const iconMapping = {
        'hp': 'heart',
        'atk': 'sword-alt',
        'defense': 'shield',
        'spd': 'bolt',
        'crit': 'location-crosshairs',
        'crit_dmg': 'burst'
    };
    return iconMapping[slotType] || 'circle-question';
}

function equipRune(itemId, slotType) {
    const dinoId = document.querySelector('.runes-container').dataset.dinoId;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch(`/dinowars/dino/${dinoId}/equip-rune/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            item_id: itemId,
            slot: slotType
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const slotContainer = document.querySelector(`.rune-slot[data-slot="${slotType}"]`);
            // Update icon with rarity class
            const slotItem = slotContainer.querySelector('.slot-item');
            const rarityClass = data.skin_rarity ? getRarityClass(data.skin_rarity) : '';
            slotItem.innerHTML = `<i class="fi fi-ss-${getIconClass(slotType)} equipped ${rarityClass}"></i>`;
            
            // Update the dino card
            updateDinoCard(dinoId, slotType, data.icon_type, rarityClass);

            // Update stat display
            const slotNumber = slotContainer.querySelector('.slot-number');
            slotNumber.innerHTML = `${data.total_stat} (${data.base_stat}+${data.bonus})`;
            
            // Hide inventory panel
            document.querySelector('.inventory-panel').style.display = 'none';
            document.querySelector(`.rune-slot[data-slot="${slotType}"] .slot-item-skin`).setAttribute('data', data.skin_name);
            const currentItem = document.getElementById('currentItem');
            currentItem.textContent = data.skin_name;
            currentItem.parentElement.parentElement.style.display = 'block';
        }
    });
}

function getRarityClass(rarity) {
    const rarityMapping = {
        'common': 'fi-cyan',
        'uncommon': 'fi-blue',
        'rare': 'fi-purple',
        'legendary': 'fi-red'
    };
    return rarityMapping[rarity] || 'fi-cyan';
}

function emptySlot() {
    const slotType = document.querySelector('.inventory-panel').dataset.currentSlot;
    const dinoId = document.querySelector('.runes-container').dataset.dinoId;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch(`/dinowars/dino/${dinoId}/equip-rune/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            slot: slotType,
            remove: true
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const slotContainer = document.querySelector(`.rune-slot[data-slot="${slotType}"]`);
            // Update icon
            const slotItem = slotContainer.querySelector('.slot-item');
            slotItem.innerHTML = `<i class="fi fi-rs-${getIconClass(slotType)} unequipped"></i>`;
            
            // Update stat display
            const slotNumber = slotContainer.querySelector('.slot-number');
            slotNumber.innerHTML = `${data.total_stat} (${data.base_stat}+0)`;
            
            // Update the dino card
            updateDinoCard(dinoId, slotType, data.icon_type, '');
            
            // Hide inventory panel
            document.querySelector('.inventory-panel').style.display = 'none';
            document.querySelector(`.rune-slot[data-slot="${slotType}"] .slot-item-skin`).setAttribute('data', 'None');
            const currentItem = document.getElementById('currentItem');
            currentItem.textContent = 'None';
            currentItem.parentElement.parentElement.style.display = 'none';
        }
    });
}

function updateDinoCard(dinoId, slotType, iconType, rarityClass) {
    const dinoCard = document.querySelector(`.dino-card[data-dino-id="${dinoId}"]`);
    if (dinoCard) {
        const runeIcon = dinoCard.querySelector(`.runes i[class*="${getIconClass(slotType)}"]`);
        if (runeIcon) {
            // Remove all existing rarity classes
            runeIcon.classList.remove('fi-cyan', 'fi-blue', 'fi-purple', 'fi-red');
            // Update the icon class
            runeIcon.className = `fi fi-${iconType}-${getIconClass(slotType)}${rarityClass ? ' ' + rarityClass : ''}`;
        }
    }
}

function fuseDinos(dinoId1) {
    // Get dino info from the card
    const dinoCard = document.querySelector(`.dino-card[data-dino-id="${dinoId1}"]`);
    const dinoName = dinoCard.querySelector('h3').textContent;
    const dinoLevel = parseInt(dinoCard.dataset.level);
    
    // Get the first eligible dino, excluding those in arena
    const eligibleDino = Array.from(document.querySelectorAll('.dino-card'))
        .find(card => 
            card.querySelector('h3').textContent === dinoName && 
            parseInt(card.dataset.level) === dinoLevel &&
            parseInt(card.dataset.dinoId) !== dinoId1 &&
            !card.hasAttribute('data-in-arena') &&  // Skip arena dinos
            !card.hasAttribute('data-in-arena-team')  // Skip dinos in arena teams
        );

    if (!eligibleDino) {
        alert('Aucun dino éligible trouvé pour la fusion');
        return;
    }
    
    const dinoId2 = eligibleDino.dataset.dinoId;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    if (confirm('Êtes-vous sûr de vouloir fusionner ces dinos ? Cette action ne peut pas être annulée. (Les runes seront déséquipées avant la fusion)')) {
        fetch('/dinowars/fuse-dinos/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                dino_id1: dinoId1,
                dino_id2: dinoId2
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                localStorage.setItem('showDinoAfterLoad', data.new_dino_id);
                window.location.href = '/dinowars';
            } else {
                alert(data.error || 'La fusion a échoué');
            }
        });
    }
}

function openHatchPopup() {
    document.getElementById('hatchPopup').style.display = 'flex';
}

function closeHatchPopup() {
    document.getElementById('hatchPopup').style.display = 'none';
}

document.querySelector('.hatch-btn').addEventListener('click', openHatchPopup);

document.getElementById('confirmHatchBtn').addEventListener('click', function() {
    fetch('/dinowars/hatch/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Redirection vers la page dinowars
            localStorage.setItem('showDinoAfterLoad', data.dino_id);
            window.location.href = '/dinowars';
        } else {
            alert(data.error);
        }
    });
});

function openBattlePopup() {
    const popup = document.getElementById('battlePopup');
    const content = document.getElementById('battleContent');
    
    fetch('/dinowars/battle/', {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.text())
    .then(html => {
        content.innerHTML = html;
        popup.style.display = 'block';
        
        // Setup event listeners
        const userTeamSelect = document.getElementById('userTeamSelect');
        const opponentTeams = document.querySelectorAll('.opponent-team');
        const startBattleBtn = document.getElementById('startBattleBtn');
        const opponentSection = document.getElementById('opponentsSection');
        
        let selectedOpponentTeam = null;
        
        userTeamSelect.addEventListener('change', updateBattleButton);
        opponentTeams.forEach(team => {
            team.addEventListener('click', function() {
                opponentTeams.forEach(t => t.classList.remove('selected'));
                team.classList.add('selected');
                selectedOpponentTeam = team.dataset.teamId;
                updateBattleButton();
            });
        });

        // Add battle button event listener here
        startBattleBtn.addEventListener('click', function() {
            const userTeamSelect = document.getElementById('userTeamSelect');
            let opponentTeamId;
            let gamemode = 'duel';
            opponentTeamId = document.querySelector('.opponent-team.selected').dataset.teamId;

            fetch('/dinowars/start_battle/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    attacker_team_id: userTeamSelect.value,
                    defender_team_id: opponentTeamId,
                    gamemode: gamemode
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = `/dinowars/battle/analytics/${data.fight_id}/`;
                } else {
                    alert(data.error || 'An error occurred during battle');
                }
            });
        });
        
        function updateBattleButton() {
            startBattleBtn.style.display = 
                userTeamSelect.value && selectedOpponentTeam ? 'block' : 'none';
            opponentSection.setAttribute('style',
                userTeamSelect.value && selectedOpponentTeam ? 'max-height: 51vh;' : 'max-height: 60vh;'
            );
        }
    });
}

function closeBattlePopup() {
    const popup = document.getElementById('battlePopup');
    popup.style.display = 'none';
}

// Add event listener to battle button
document.querySelector('.battle-btn').addEventListener('click', openBattlePopup);

function openArenaPopup() {
    const popup = document.getElementById('arenaPopup');
    const content = document.getElementById('arenaContent');
    
    fetch('/dinowars/arena/', {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.text())
    .then(html => {
        content.innerHTML = html;
        popup.style.display = 'block';
        
        // Setup event listeners
        const userTeamSelect = document.getElementById('userTeamSelect');
        const startBattleBtn = document.getElementById('startBattleBtn');
        const championUsername = document.getElementById('championUsername');
        const teamSelectorSection = document.getElementById('teamSelectorSection');
        const arenaEnergy = parseInt(teamSelectorSection.getAttribute('data-arenaEnergy') || 0);

        if (arenaEnergy <= 0) {
            teamSelectorSection.innerHTML = '<p class="energy-empty">Energie d\'arène vide...</p>';
            if (startBattleBtn) startBattleBtn.style.display = 'none';
            return;
        }

        // If the current user is the champion, hide the user team select
        if (championUsername.innerText === userTeamSelect.getAttribute('data-username')) {
            teamSelectorSection.style.display = 'none';
            return;
        }

        userTeamSelect.addEventListener('change', () => {
            startBattleBtn.style.display = userTeamSelect.value ? 'block' : 'none';
        });

        // Add arena battle button event listener
        if (startBattleBtn) {
            startBattleBtn.addEventListener('click', function() {
                const championTeam = document.querySelector('.champion-team');
                if (!championTeam) {
                    alert('No champion team found!');
                    return;
                }

                fetch('/dinowars/start_battle/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify({
                        attacker_team_id: userTeamSelect.value,
                        defender_team_id: championTeam.dataset.teamId,
                        gamemode: 'arena'
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.href = `/dinowars/battle/analytics/${data.fight_id}/`;
                    } else {
                        alert(data.error || 'An error occurred during arena battle');
                    }
                })
            });
        }
    });
}

function closeArenaPopup() {
    const popup = document.getElementById('arenaPopup');
    popup.style.display = 'none';
}

// Add event listener to arena button
document.querySelector('.arena-btn').addEventListener('click', openArenaPopup);
