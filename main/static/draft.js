document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const positionFilter = document.getElementById('position-filter');
    const playerSearch = document.getElementById('player-search');
    const playerList = document.getElementById('player-list');
    const selectedPlayers = document.getElementById('selected-players');
    const autoDraftBtn = document.getElementById('auto-draft-btn');
    const completeDraftBtn = document.getElementById('complete-draft-btn');
    const currentRoundSpan = document.getElementById('current-round');
    const currentPickSpan = document.getElementById('current-pick');
    const draftTimer = document.getElementById('draft-timer');
    
    // Draft state
    const draftId = document.querySelector('.draft-simulator').dataset.draftId;
    let currentRound = 1;
    let currentPick = 1;
    let availablePlayers = [];
    let selectedPlayerIds = new Set();
    
    // Authentication tokens
    const token = localStorage.getItem('auth_token') || '';
    
    // Initialize draft
    initializeDraft();
    
    // Start timer
    startTimer();
    
    // Initialize draft data
    function initializeDraft() {
        // Fetch available players
        fetch('/api/players/', {
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                if (response.status === 401) {
                    // Unauthorized - redirect to login
                    window.location.href = '/accounts/login/?next=' + window.location.pathname;
                    return;
                }
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data) {
                availablePlayers = data;
                renderAvailablePlayers();
            }
        })
        .catch(error => console.error('Error fetching players:', error));
        
        // Fetch current draft status
        fetch(`/api/drafts/${draftId}/`, {
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                if (response.status === 401) {
                    // Unauthorized - redirect to login
                    window.location.href = '/accounts/login/?next=' + window.location.pathname;
                    return;
                }
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (!data) return;
            
            // If draft has existing picks, load them
            if (data.picks && data.picks.length > 0) {
                data.picks.forEach(pick => {
                    selectedPlayerIds.add(pick.player.id);
                    renderSelectedPlayer(pick);
                });
                
                // Update current round and pick
                const lastPick = data.picks[data.picks.length - 1];
                currentRound = lastPick.round_number;
                currentPick = lastPick.pick_number + 1;
                
                // If we're at the end of a round, move to next round
                if (currentPick > 32) {
                    currentRound++;
                    currentPick = 1;
                }
                
                updateDraftPosition();
            }
            
            // If draft is completed, disable buttons
            if (data.is_completed) {
                autoDraftBtn.disabled = true;
                completeDraftBtn.disabled = true;
                stopTimer();
            }
        })
        .catch(error => console.error('Error fetching draft data:', error));
    }
    
    // Render available players
    function renderAvailablePlayers() {
        playerList.innerHTML = '';
        
        const position = positionFilter.value;
        const searchTerm = playerSearch.value.toLowerCase();
        
        availablePlayers
            .filter(player => !selectedPlayerIds.has(player.id))
            .filter(player => position ? player.position === position : true)
            .filter(player => player.name.toLowerCase().includes(searchTerm) || 
                              player.college.toLowerCase().includes(searchTerm))
            .forEach(player => {
                const playerCard = document.createElement('div');
                playerCard.className = 'player-card';
                playerCard.dataset.position = player.position;
                
                const playerImage = player.image || `/static/images/default_player.png`;
                
                playerCard.innerHTML = `
                    <img src="${playerImage}" alt="${player.name}">
                    <div class="player-details">
                        <h3>${player.name}</h3>
                        <p>${player.position} - ${player.college}</p>
                        <div class="player-stats">
                            <span>Draft Ranking: ${player.draft_ranking}</span>
                        </div>
                        <button class="draft-player-btn" data-player-id="${player.id}">Draft</button>
                    </div>
                `;
                
                playerList.appendChild(playerCard);
            });
        
        // Attach event listeners to draft buttons
        document.querySelectorAll('.draft-player-btn').forEach(button => {
            button.addEventListener('click', function() {
                const playerId = this.dataset.playerId;
                draftPlayer(playerId);
            });
        });
    }
    
    // Draft a player
    function draftPlayer(playerId) {
        const player = availablePlayers.find(p => p.id.toString() === playerId.toString());
        
        if (!player) return;
        
        // Create draft pick
        const draftPickData = {
            player_id: playerId,
            round_number: currentRound,
            pick_number: currentPick
        };
        
        // Send API request to add the pick
        fetch(`/api/drafts/${draftId}/add_pick/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${token}`,
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(draftPickData)
        })
        .then(response => {
            if (!response.ok) {
                if (response.status === 401) {
                    // Unauthorized - redirect to login
                    window.location.href = '/accounts/login/?next=' + window.location.pathname;
                    return;
                }
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (!data) return;
            
            if (data.status === 'pick added') {
                // Add player to selected list
                selectedPlayerIds.add(parseInt(playerId));
                
                // Render selected player
                renderSelectedPlayer(data.pick);
                
                // Update available players
                renderAvailablePlayers();
                
                // Move to next pick
                currentPick++;
                
                // If at end of round, move to next round
                if (currentPick > 32) {
                    currentRound++;
                    currentPick = 1;
                }
                
                // Update draft position
                updateDraftPosition();
                
                // Check if draft is complete
                checkDraftCompletion();
            }
        })
        .catch(error => console.error('Error drafting player:', error));
    }
    
    // Render a selected player
    function renderSelectedPlayer(pick) {
        const pickElement = document.createElement('div');
        pickElement.className = 'draft-pick';
        
        pickElement.innerHTML = `
            <div class="pick-header">
                <span>Round ${pick.round_number}, Pick ${pick.pick_number}</span>
            </div>
            <div class="pick-details">
                <h3>${pick.player.name}</h3>
                <p>${pick.player.position} - ${pick.player.college}</p>
            </div>
        `;
        
        selectedPlayers.appendChild(pickElement);
    }
    
    // Update current draft position
    function updateDraftPosition() {
        currentRoundSpan.textContent = currentRound;
        currentPickSpan.textContent = currentPick;
        
        // Enable complete draft button if we've made enough picks
        if (selectedPlayerIds.size >= 7) {
            completeDraftBtn.disabled = false;
        }
    }
    
    // Check if draft is complete
    function checkDraftCompletion() {
        const maxRounds = document.querySelector('.draft-simulator').dataset.rounds || 7;
        
        if (currentRound > maxRounds) {
            completeDraft();
        }
    }
    
    // Complete the draft
    function completeDraft() {
        fetch(`/api/drafts/${draftId}/complete_draft/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${token}`,
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({})
        })
        .then(response => {
            if (!response.ok) {
                if (response.status === 401) {
                    // Unauthorized - redirect to login
                    window.location.href = '/accounts/login/?next=' + window.location.pathname;
                    return;
                }
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (!data) return;
            
            if (data.status === 'draft completed') {
                // Redirect to draft results page
                window.location.href = `/draft/${draftId}/results/`;
            }
        })
        .catch(error => console.error('Error completing draft:', error));
    }
    
    // Start the draft timer
    function startTimer() {
        timerInterval = setInterval(() => {
            if (timerSeconds === 0) {
                if (timerMinutes === 0) {
                    stopTimer();
                    return;
                }
                timerMinutes--;
                timerSeconds = 59;
            } else {
                timerSeconds--;
            }
            
            draftTimer.textContent = `${timerMinutes.toString().padStart(2, '0')}:${timerSeconds.toString().padStart(2, '0')}`;
        }, 1000);
    }
    
    // Stop the draft timer
    function stopTimer() {
        clearInterval(timerInterval);
    }
    
    // Auto draft function
    function autoDraft() {
        // Get best available player (lowest draft ranking)
        const availablePlayerIds = availablePlayers
            .filter(player => !selectedPlayerIds.has(player.id))
            .sort((a, b) => a.draft_ranking - b.draft_ranking);
        
        if (availablePlayerIds.length > 0) {
            draftPlayer(availablePlayerIds[0].id);
        }
    }
    
    // Login function for API token
    function loginWithToken(username, password) {
        fetch('/accounts/api/token/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.token) {
                localStorage.setItem('auth_token', data.token);
                // Reload the page to reinitialize with token
                window.location.reload();
            }
        })
        .catch(error => console.error('Error logging in:', error));
    }
    
    // Event listeners
    positionFilter.addEventListener('change', renderAvailablePlayers);
    playerSearch.addEventListener('input', renderAvailablePlayers);
    autoDraftBtn.addEventListener('click', autoDraft);
    completeDraftBtn.addEventListener('click', completeDraft);
    
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
});