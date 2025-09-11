document.addEventListener('DOMContentLoaded', function() {
    // Initialize UI elements
    initializeUIElements();
    
    // Add event listeners
    setupEventListeners();
    
    // Initialize run dino cards
    initializeDinoCards();
    
    // Initialize ability cards
    initializeAbilityCards();
    
    // Initialize terrain tooltip functionality
    initializeTerrainTooltip();
});

function initializeUIElements() {
    // Disable the start battle button initially
    const startBattleButton = document.getElementById('start-pvm-battle');
    if (startBattleButton) {
        startBattleButton.disabled = true;
    }
    
    // Hide the enemies container initially
    const enemiesContainer = document.getElementById('enemies-container');
    if (enemiesContainer) {
        enemiesContainer.style.display = 'none';
    }
}

function setupEventListeners() {
    // Back button to return to the main dino page
    const backButton = document.querySelector('.back-btn');
    if (backButton) {
        backButton.addEventListener('click', function() {
            window.location.href = '/dinowars/';
        });
    }
    
    // Next Fight button
    const nextFightButton = document.querySelector('.next-fight-btn');
    if (nextFightButton) {
        nextFightButton.addEventListener('click', function() {
            startBattle();
        });
    }
    
    // Fight History button
    const fightHistoryButton = document.querySelector('.fight-history-btn');
    if (fightHistoryButton) {
        fightHistoryButton.addEventListener('click', function() {
            showFightHistoryPopup();
        });
    }
}

function initializeDinoCards() {
    const dinoCards = document.querySelectorAll('.dino-card');
    dinoCards.forEach(card => {
        card.addEventListener('click', function() {
            const dinoId = this.getAttribute('data-dino-id');
            const enemy = this.getAttribute('data-enemy');
            showDinoDetails(dinoId, enemy);
        });
    });
}

// Store ability click handlers in a map (abilityId -> function)
const abilityClickHandlers = new Map();

function initializeAbilityCards() {
    const nextAbilityCards = document.querySelectorAll('#next-abilities-container .ability-card:not(.selected-ability):not(.discarded-ability)');
    nextAbilityCards.forEach(card => {
        if (card.getAttribute('data-selected') !== 'true' && card.getAttribute('data-discarded') !== 'true') {
            const abilityId = card.getAttribute('data-ability-id');
            // Create and store a named function for this card
            const clickHandler = function() {
                selectAbility(abilityId);
            };
            abilityClickHandlers.set(abilityId, clickHandler);
            card.addEventListener('click', clickHandler);
        }
    });
}

function showDinoDetails(dinoId, enemy) {
    const popup = document.getElementById('dinoDetailPopup');
    const content = document.getElementById('dinoDetailContent');
        
    fetch(`/dinowars/pvm/dino/${dinoId}/`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'enemy': enemy,
        }
    })
    .then(response => response.text())
    .then(html => {
        content.innerHTML = html;
        popup.style.display = 'block';

        // Add event listener for level up stats button
        const levelUpStatsBtn = document.getElementById('levelUpStatsBtn');
        if (levelUpStatsBtn) {
            levelUpStatsBtn.addEventListener('click', function() {
                const dinoId = this.getAttribute('data-dino-id');
                showStatAllocationPopup(dinoId);
            });
        }

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
    
    if (popup && !content.contains(event.target) && !event.target.classList.contains('close-popup')) {
        closeDinoDetailPopup();
    }
}

function handleDinoDetailEscKey(event) {
    if (event.key === 'Escape') {
        closeDinoDetailPopup();
    }
}

function showStatAllocationPopup(dinoId) {
    const popup = document.getElementById('statAllocationPopup');
    const content = document.getElementById('statAllocationContent');
    
    fetch(`/dinowars/pvm/dino/${dinoId}/level-up/`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.text())
    .then(html => {
        content.innerHTML = html;
        popup.style.display = 'block';
        
        // Add event listeners to all level up buttons
        const levelUpButtons = document.querySelectorAll('.stat-level-up-btn');
        levelUpButtons.forEach(button => {
            button.addEventListener('click', function() {
                const stat = this.getAttribute('data-stat');
                const cost = parseInt(this.getAttribute('data-cost'));
                levelUpStat(dinoId, stat, cost);
            });
        });
        
        // Add event listener to close button
        const closeBtn = document.getElementById('closeStatAllocationBtn');
        if (closeBtn) {
            closeBtn.addEventListener('click', closeStatAllocationPopup);
        }
        
        document.addEventListener('mousedown', handleStatAllocationClickOutside);
        document.addEventListener('keydown', handleStatAllocationEscKey);
    });
}

function levelUpStat(dinoId, statName, cost) {
    fetch(`/dinowars/pvm/dino/${dinoId}/level-up/${statName}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ cost: cost })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Refresh the stat allocation popup to show updated values
            showStatAllocationPopup(dinoId);
            
            // Update the available stat points in the current popup
            const availablePointsElem = document.getElementById('availableStatPoints');
            if (availablePointsElem) {
                availablePointsElem.textContent = data.remaining_points;
            }
            
            // Update the main page's stat points counter
            updateMainPageStatPoints(data.remaining_points);
        } else {
            alert('Erreur: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Une erreur est survenue lors de la mise à jour des statistiques.');
    });
}

// Function to update the main page's stat points counter
function updateMainPageStatPoints(remainingPoints) {
    // Update the stat points counter in the user info section
    const mainStatPointsElement = document.getElementById('main-stat-points-counter');
    if (mainStatPointsElement) {
        mainStatPointsElement.textContent = remainingPoints;
    }
}

function closeStatAllocationPopup() {
    const popup = document.getElementById('statAllocationPopup');
    popup.style.display = 'none';
    document.removeEventListener('mousedown', handleStatAllocationClickOutside);
    document.removeEventListener('keydown', handleStatAllocationEscKey);
    
    // Refresh the dino details popup to show updated stats
    const dinoDetailLevelUpBtn = document.getElementById('levelUpStatsBtn');
    if (dinoDetailLevelUpBtn) {
        const dinoId = dinoDetailLevelUpBtn.getAttribute('data-dino-id');
        showDinoDetails(dinoId, 'false');
    }
}

function handleStatAllocationClickOutside(event) {
    const popup = document.getElementById('statAllocationPopup');
    const content = document.getElementById('statAllocationContent');
    
    if (popup && !content.contains(event.target) && !event.target.classList.contains('close-popup')) {
        closeStatAllocationPopup();
    }
}

function handleStatAllocationEscKey(event) {
    if (event.key === 'Escape') {
        closeStatAllocationPopup();
    }
}

function selectAbility(abilityId) {
    fetch(`/dinowars/pvm/ability/${abilityId}/select/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the appearance of all ability cards
            const nextAbilitiesContainer = document.getElementById('next-abilities-container');
            const allAbilityCards = nextAbilitiesContainer.querySelectorAll('.ability-card');
            
            allAbilityCards.forEach(card => {
                const cardAbilityId = card.getAttribute('data-ability-id');
                
                // Properly remove event listener using the stored reference
                const clickHandler = abilityClickHandlers.get(cardAbilityId);
                if (clickHandler) {
                    card.removeEventListener('click', clickHandler);
                    // Clear from the map
                    abilityClickHandlers.delete(cardAbilityId);
                }
                
                if (cardAbilityId === abilityId) {
                    // This is the selected card
                    card.classList.remove('selectable-ability');
                    card.classList.add('selected-ability');
                    
                    // Update the prompt text
                    const promptSpan = card.querySelector('.select-prompt');
                    if (promptSpan) {
                        promptSpan.className = 'selected-prompt';
                        promptSpan.textContent = 'Capacité sélectionnée';
                    }
                    
                    card.style.cursor = 'default';
                } else {
                    // These are discarded cards
                    card.classList.remove('selectable-ability');
                    card.classList.add('discarded-ability');
                    
                    // Remove the prompt text
                    const promptSpan = card.querySelector('.select-prompt');
                    if (promptSpan) {
                        promptSpan.remove();
                    }
                    
                    card.style.cursor = 'default';
                }
            });
            
            // Check if this ability needs to be assigned to a dino
            if (data.to_dino) {
                // Show the dino selection popup
                showDinoSelectionPopup(data.ability_id);
            } else {
                // Add the selected ability to the abilities container directly
                addSelectedAbilityToList(data);
            }
        } else {
            alert('Erreur: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Une erreur est survenue lors de la sélection de la capacité: ' + error);
    });
}

function addSelectedAbilityToList(data) {
    // Add the selected ability to the abilities container
    const abilitiesContainer = document.getElementById('abilities-container');
    const newAbilityCard = document.createElement('div');
    newAbilityCard.className = 'ability-card newly-added';
    newAbilityCard.innerHTML = `
        <h3>${data.ability_name}</h3>
        <p>${data.ability_description}</p>
        <span class="ability-status">Nouvellement acquise</span>
    `;
    
    // Add to top of list
    if (abilitiesContainer.firstChild) {
        abilitiesContainer.insertBefore(newAbilityCard, abilitiesContainer.firstChild);
    } else {
        abilitiesContainer.appendChild(newAbilityCard);
    }
    
    // Clear "no abilities" message if it exists
    const noAbilitiesMessage = abilitiesContainer.querySelector('p:not(:has(*))');
    if (noAbilitiesMessage && !noAbilitiesMessage.parentElement.classList.contains('ability-card')) {
        noAbilitiesMessage.remove();
    }
    
    // Highlight the new ability card
    setTimeout(() => {
        newAbilityCard.classList.remove('newly-added');
    }, 5000); // Remove the highlight after 5 seconds
}

function showDinoSelectionPopup(abilityId) {
    const popup = document.getElementById('dinoSelectionPopup');
    if (!popup) return;
    
    // Set the current ability ID in the hidden field
    document.getElementById('currentAbilityId').value = abilityId;
    
    // Show the popup
    popup.style.display = 'block';
    
    // Add click event listeners to the dino cards
    const dinoCards = document.querySelectorAll('#dinosSelectionGrid .dino-card');
    dinoCards.forEach(card => {
        card.addEventListener('click', function() {
            const dinoId = this.getAttribute('data-dino-id');
            selectAbilityDino(abilityId, dinoId);
        });
    });
    
}

function closeDinoSelectionPopup() {
    const popup = document.getElementById('dinoSelectionPopup');
    popup.style.display = 'none';
}

function selectAbilityDino(abilityId, dinoId) {
    fetch(`/dinowars/pvm/ability/${abilityId}/select-dino/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ dino_id: dinoId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Close the dino selection popup
            closeDinoSelectionPopup();
            
            // Add the selected ability to the abilities list with dino info
            const abilitiesContainer = document.getElementById('abilities-container');
            const newAbilityCard = document.createElement('div');
            newAbilityCard.className = 'ability-card newly-added';
            
            // Get ability name and description from the selected ability card
            const selectedAbilityCard = document.querySelector(`.selected-ability`);
            const abilityName = selectedAbilityCard.querySelector('h3').textContent;
            const abilityDesc = selectedAbilityCard.querySelector('p').textContent;
            
            newAbilityCard.innerHTML = `
                <h3>${abilityName}</h3>
                <p>${abilityDesc}</p>
                <p class="ability-dino-info">Assignée à: ${data.dino_name}</p>
                <span class="ability-status">Nouvellement acquise</span>
            `;
            
            // Add to top of list
            if (abilitiesContainer.firstChild) {
                abilitiesContainer.insertBefore(newAbilityCard, abilitiesContainer.firstChild);
            } else {
                abilitiesContainer.appendChild(newAbilityCard);
            }
            
            // Clear "no abilities" message if it exists
            const noAbilitiesMessage = abilitiesContainer.querySelector('p:not(:has(*))');
            if (noAbilitiesMessage && !noAbilitiesMessage.parentElement.classList.contains('ability-card')) {
                noAbilitiesMessage.remove();
            }
            
            // Highlight the new ability card
            setTimeout(() => {
                newAbilityCard.classList.remove('newly-added');
            }, 5000); // Remove the highlight after 5 seconds
        } else {
            alert('Erreur: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Une erreur est survenue lors de la sélection du dinosaure: ' + error);
    });
}

function startBattle() {
    // Show loading indicator or disable button
    const nextFightButton = document.querySelector('.next-fight-btn');
    if (nextFightButton) {
        nextFightButton.disabled = true;
        nextFightButton.textContent = 'Combat en cours...';
    }
    
    fetch('/dinowars/pvm/start_battle/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.fight_id) {
            // Redirect to battle analytics page with the fight ID
            window.location.href = `/dinowars/battle/analytics/${data.fight_id}/`;
        } else if (data.redirect) {
            window.location.href = data.redirect;
        } else if (data.message) {
            alert(data.message);
            // Reset button
            if (nextFightButton) {
                nextFightButton.disabled = false;
                nextFightButton.textContent = 'Combat';
            }
        }
        else {
            return response.json().then(data => {
                throw new Error(errorData.message || 'Server error: ' + response.status);
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Une erreur est survenue lors du lancement du combat.');
        // Reset button
        if (nextFightButton) {
            nextFightButton.disabled = false;
            nextFightButton.textContent = 'Combat';
        }
    });
}

function initializeTerrainTooltip() {
    const terrainElement = document.getElementById('terrain');
    if (terrainElement) {
        const description = terrainElement.getAttribute('data-desc');
        if (description) {
            terrainElement.setAttribute('title', description);
        }
    }
}

function showFightHistoryPopup() {
    const popup = document.getElementById('fightHistoryPopup');
    const content = document.getElementById('fightHistoryContent');
    const loadingMessage = content.querySelector('.loading-message');
    const fightsList = document.getElementById('fightsList');
    
    // Show popup and loading message
    popup.style.display = 'block';
    loadingMessage.style.display = 'block';
    fightsList.innerHTML = '';
    
    // Fetch fight history
    fetch('/dinowars/pvm/run-fights/', {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        loadingMessage.style.display = 'none';
        
        if (data.success) {
            if (data.fights.length === 0) {
                fightsList.innerHTML = '<p class="no-fights-message">Aucun combat effectué dans cette run.</p>';
            } else {
                displayFightsList(data.fights, data.run_level);
            }
        } else {
            fightsList.innerHTML = `<p class="error-message">Erreur: ${data.error}</p>`;
        }
    })
    .catch(error => {
        console.error('Error fetching fight history:', error);
        loadingMessage.style.display = 'none';
        fightsList.innerHTML = '<p class="error-message">Une erreur est survenue lors du chargement de l\'historique.</p>';
    });
    
    // Add event listeners for popup interactions
    document.addEventListener('mousedown', handleFightHistoryClickOutside);
    document.addEventListener('keydown', handleFightHistoryEscKey);
}

function displayFightsList(fights, runLevel) {
    const fightsList = document.getElementById('fightsList');
    
    // Compact header
    let fightsHtml = `<div class="fights-header"><p>Run niveau ${runLevel} — ${fights.length} combat${fights.length > 1 ? 's' : ''}</p></div>`;

    // Render each fight as a single compact line
    fights.forEach((fight, index) => {
        const resultClass = fight.is_victory ? 'victory' : 'defeat';
        const resultText = fight.is_victory ? 'Victoire' : 'Défaite';
        const fightNumber = fights.length - index; // newest first

        fightsHtml += `
            <div class="fight-item compact ${resultClass}">
            <div class="fight-line">
                <span class="fight-number">#${fightNumber}</span>
                <span class="fight-date">${fight.date.split(' ')[1]}</span>
                <span class="fight-teams">${fight.user2_team}</span>
                <span class="fight-result ${resultClass}">${resultText}</span>
                <a href="/dinowars/battle/analytics/${fight.id}/" class="analytics-link" target="_blank" title="Voir les analytics" style="display: none;"></a>
            </div>
            </div>
        `;
    });

    fightsList.innerHTML = fightsHtml;

    // Make each compact fight row clickable (open analytics). If the user clicks the actual analytics link,
    // let the link handle the action instead.
    const compactItems = fightsList.querySelectorAll('.fight-item.compact');
    compactItems.forEach(item => {
        const link = item.querySelector('.analytics-link');
        const url = link ? link.href : null;
        if (!url) return;

        // set pointer cursor for better affordance
        item.style.cursor = 'pointer';

        item.addEventListener('click', (e) => {
            // if the click originated on the analytics link (or its children), do nothing (allow default)
            if (e.target.closest && e.target.closest('.analytics-link')) return;
            // open analytics in a new tab
            window.open(url, '_blank');
        });
    });
}

function closeFightHistoryPopup() {
    const popup = document.getElementById('fightHistoryPopup');
    popup.style.display = 'none';
    document.removeEventListener('mousedown', handleFightHistoryClickOutside);
    document.removeEventListener('keydown', handleFightHistoryEscKey);
}

function handleFightHistoryClickOutside(event) {
    const popup = document.getElementById('fightHistoryPopup');
    const content = popup.querySelector('.popup-content');
    
    if (popup && !content.contains(event.target) && !event.target.classList.contains('close-popup')) {
        closeFightHistoryPopup();
    }
}

function handleFightHistoryEscKey(event) {
    if (event.key === 'Escape') {
        closeFightHistoryPopup();
    }
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
