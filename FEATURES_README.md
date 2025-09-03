# MyBlog - Paris & PVM Features Documentation

This document provides a comprehensive overview of the **Paris (Betting System)** and **PVM (Player vs Monster)** features implemented in the MyBlog Django application.

## Table of Contents

1. [Paris (Betting System) Feature](#paris-betting-system-feature)
2. [PVM (Player vs Monster) Feature](#pvm-player-vs-monster-feature)
3. [Technology Stack](#technology-stack)
4. [Installation & Setup](#installation--setup)

---

## Paris (Betting System) Feature

The Paris feature is a comprehensive betting/wagering system where users can create bets on various topics and other users can place wagers using the in-game currency (coins).

### ✅ Completed Features

#### Models & Database
- **Pari Model**: Main betting entity with name, description, creator, duration, open/close status, and admin review functionality
- **PariIssue Model**: Different betting options/outcomes for each bet, with winning status tracking
- **UserForIssue Model**: User bets on specific issues with amount (mise) and optional comments
- **Database migrations**: Complete migration system (migration 0034) for all betting-related models

#### Core Functionality
- **Bet Creation**: 
  - Users can create bets with custom names, descriptions, and multiple betting options
  - Flexible duration system supporting days, hours, and minutes (e.g., "2d3h30mn")
  - Form validation for minimum 2 betting options and proper duration format
  - Integration with quest system for bet creation objectives

- **Bet Participation**:
  - Users can place bets using their coin balance
  - Comment system for each bet
  - Validation to prevent betting after expiration
  - Prevention of multiple bets per user on the same betting event
  - Real-time balance checking

- **Bet Resolution**:
  - Admin interface for selecting winning outcomes (right-click context menu)
  - Automatic coin distribution to winners based on proportional share
  - Calculation system: `(user_bet / total_winning_bets) * total_pot`
  - Automatic bet closure and admin review marking

#### User Interface
- **List View** (`/paris/`): 
  - Separate display for open and closed bets
  - Clear status indicators
- **Detail View** (`/paris/<id>`):
  - Comprehensive bet information with expiration countdown
  - Interactive pie chart showing bet distribution (Chart.js)
  - Live betting interface with coin balance display
  - User participation tracking and betting history
  - Gains/losses display for concluded bets
- **Creation Interface** (`/paris/create`):
  - Dynamic form for adding multiple betting options
  - Duration picker with validation
  - Real-time form validation with error messaging

#### Administrative Features
- **Admin Panel Integration**: Full CRUD operations for Pari, PariIssue, and UserForIssue models
- **Bet Moderation**: Admin review system before bets become active
- **Winner Selection**: Context-menu interface for admins to select winning outcomes
- **Automatic Payouts**: Coin distribution system with transaction logging

#### Technical Implementation
- **AJAX-based Operations**: Real-time betting without page refresh
- **CSRF Protection**: Secure form submissions
- **Input Validation**: Comprehensive client and server-side validation
- **Error Handling**: User-friendly error messages and fallbacks
- **Query Optimization**: Efficient database queries with proper foreign key relationships

### 🔄 Areas for Potential Enhancement

- **Bet Categories**: System for categorizing different types of bets
- **Bet History**: Comprehensive user betting history with statistics
- **Notification System**: Alerts for bet expiration, results, and winnings
- **Advanced Statistics**: Win/loss ratios, popular betting categories
- **Mobile Optimization**: Enhanced mobile interface for betting
- **API Endpoints**: RESTful API for mobile app integration
- **Bet Templates**: Pre-defined bet formats for common scenarios
- **Social Features**: Comments, discussions, and sharing capabilities
- **Advanced Analytics**: Betting trends and user behavior insights

---

## PVM (Player vs Monster) Feature

The PVM feature is a sophisticated roguelike game mode within the DinoWars system where players embark on procedural runs with their dinosaurs, facing increasingly difficult AI opponents while collecting abilities and leveling up their creatures.

### ✅ Completed Features

#### Models & Database Structure
- **DWPvmDino Model**: PvM-specific dinosaur instances with leveling system
  - Individual stat tracking (HP, ATK, Defense, Speed, Crit, Crit Damage)
  - Per-stat level tracking for granular character progression
  - Attack assignment system for combat variety
- **DWPvmRun Model**: Core run progression tracking
  - Team composition (3 dinosaurs per run)
  - Life system (default 3 lives)
  - Level progression and stat point allocation
  - Run timestamp and ability tracking
- **DWPvmAbility System**: Comprehensive ability collection mechanics
  - Ability descriptions and effects
  - Dino-specific ability targeting
  - Ability selection history and preferences
- **Combat Preparation Models**: Next fight and ability preview system
- **Terrain System**: Daily rotating environmental effects

#### Core Game Loop
- **Run Initialization**:
  - New run creation with random dinosaur selection
  - Terrain-based stat modifications (Distortion, Ice Age effects)
  - State management for run progression
- **Combat System**:
  - Turn-based battle engine with AI opponents
  - Comprehensive battle analytics and logging
  - Critical hit mechanics and damage calculations
  - Status effects and terrain interactions
- **Progression Mechanics**:
  - Stat point allocation after victories
  - Ability selection between battles (3 choices per level)
  - Dino-specific ability targeting system
  - Level scaling for increasing difficulty

#### User Interface & Experience
- **Main PVM Interface** (`/dinowars/pvm/`):
  - Run overview with life counter visualization
  - Team composition display with stat summaries
  - Ability collection showcase
  - Next battle preview with enemy information
  - Daily terrain display and effects description
- **New Run Creation** (`/dinowars/pvm/new-run/`):
  - Multi-step run initialization process
  - Dinosaur selection interface
  - Terrain effect preview
- **Battle Interface**:
  - Real-time combat visualization
  - Battle analytics and detailed logging
  - Post-battle progression screens
- **Character Development**:
  - Detailed dinosaur stat sheets
  - Interactive stat allocation interface
  - Ability selection with detailed descriptions
  - Equipment and customization options

#### Advanced Systems
- **Daily Terrain System**:
  - Rotating environmental effects (currently supporting Distortion and Ice Age)
  - Terrain-specific stat modifications
  - Configuration-driven terrain selection
- **Ability System**:
  - Rich ability pool with varied effects
  - Smart ability selection algorithms
  - Dino-specific targeting and application
  - Selection memory and preferences
- **Analytics & Tracking**:
  - Comprehensive battle logging
  - Performance metrics and statistics
  - Run success tracking
  - User progression analytics

#### Technical Implementation
- **Battle Engine**: Sophisticated turn-based combat system with:
  - Damage calculation with variance and critical hits
  - Status effect management
  - AI decision making
  - Battle state persistence
- **Procedural Generation**: Balanced enemy scaling and encounter variety
- **State Management**: Complex game state handling with proper persistence
- **Performance Optimization**: Efficient queries and caching for real-time gameplay

### 🔄 Areas for Potential Enhancement

#### Content Expansion
- **Additional Terrains**: More diverse environmental effects and interactions
- **Expanded Ability Pool**: Greater variety of abilities with unique mechanics
- **Boss Encounters**: Special high-difficulty encounters with unique rewards
- **Artifact System**: Collectible items that modify run parameters

#### Progression Systems
- **Mastery System**: Long-term progression goals beyond individual runs
- **Prestige Mechanics**: Meta-progression for experienced players
- **Achievement System**: Challenges and recognition for various accomplishments
- **Leaderboards**: Competitive elements and community features

#### Quality of Life
- **Run Pause/Resume**: Ability to save and continue runs across sessions
- **Battle Replay System**: Review and analyze past battles
- **Enhanced Tutorials**: Better onboarding for new players
- **Mobile Optimization**: Touch-friendly interface improvements

#### Technical Improvements
- **Battle Animation System**: Visual enhancements for combat
- **Performance Optimization**: Further improvements for large-scale deployment
- **API Development**: External integrations and mobile app support
- **Advanced Analytics**: Deeper insights into player behavior and balance

---

## Technology Stack

### Backend
- **Django 5.1.5**: Main web framework
- **Python**: Server-side logic and game mechanics
- **SQLite/PostgreSQL**: Database for persistent storage
- **Django Admin**: Administrative interface

### Frontend
- **HTML5/CSS3**: Responsive user interface
- **JavaScript (ES6+)**: Interactive features and AJAX
- **Chart.js**: Data visualization for betting statistics
- **Bootstrap/Custom CSS**: Responsive design framework

### Features & Integrations
- **AJAX**: Real-time updates without page refresh
- **CSRF Protection**: Security for all form submissions
- **User Authentication**: Django's built-in auth system
- **Quest System Integration**: Cross-feature objective tracking
- **Constance**: Dynamic configuration management

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- Django 5.1.5
- Node.js (for frontend dependencies)

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd MyBlog
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Database setup**:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Load initial data** (if available):
   ```bash
   python manage.py loaddata initial_data.json
   ```

5. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

### Configuration

#### Paris Feature Setup
- Ensure user coin balances are properly initialized
- Configure admin permissions for bet moderation
- Set up quest objectives for bet creation (optional)

#### PVM Feature Setup
- Create initial dinosaur data and attacks
- Configure daily terrain rotation via Django admin
- Set up ability pool and descriptions
- Initialize user DinoWars profiles

### Usage

#### Accessing Paris Feature
- **List Bets**: Navigate to `/paris/`
- **Create Bet**: Click "Create New Bet" or visit `/paris/create`
- **Participate**: Click on any open bet to view details and place wagers
- **Admin Functions**: Use right-click context menu (admin only) to resolve bets

#### Accessing PVM Feature  
- **Start Playing**: Navigate to `/dinowars/pvm/`
- **New Run**: Follow the new run creation process if no active run exists
- **Battle**: Engage in turn-based combat with AI opponents
- **Progress**: Allocate stat points and select abilities between battles

---

## Contributing

When contributing to either feature:

1. **Follow Django best practices**: Use proper model design, view structure, and template organization
2. **Test thoroughly**: Ensure all AJAX endpoints work correctly and handle edge cases
3. **Maintain security**: Always validate user input and use CSRF protection
4. **Document changes**: Update this README when adding new features or modifications
5. **Performance considerations**: Optimize database queries and minimize JavaScript execution time

---

## Support & Maintenance

For issues, feature requests, or questions about either the Paris or PVM features, please:

1. Check the Django admin logs for any error messages
2. Review the browser console for JavaScript errors
3. Verify database integrity and migrations
4. Test with different user permission levels
5. Document any bugs with steps to reproduce

Both features are actively maintained and regularly receive updates for balance, performance, and new content.