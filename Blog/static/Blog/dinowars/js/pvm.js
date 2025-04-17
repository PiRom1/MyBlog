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
