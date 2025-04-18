document.addEventListener('DOMContentLoaded', function() {
    // Initialize UI elements
    initializeUIElements();
    
    // Add event listeners
    setupEventListeners();
    
    // Initialize run dino cards
    initializeDinoCards();
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
            // This would trigger the next fight in the run
            alert('Preparing next fight... Feature coming soon!');
            // In a real implementation, this would send a request to get the next enemy
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
            
            // Update buttons based on remaining points
            updateLevelUpButtons(data.remaining_points);
        } else {
            alert('Erreur: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Une erreur est survenue lors de la mise à jour des statistiques.');
    });
}

function updateLevelUpButtons(remainingPoints) {
    const buttons = document.querySelectorAll('.stat-level-up-btn');
    buttons.forEach(button => {
        const cost = parseInt(button.getAttribute('data-cost'));
        button.disabled = (cost > remainingPoints);
    });
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
