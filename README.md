
### Carrom Game Features:
1. **Authentic Carrom Gameplay**:
   - 2-player carrom board simulation with physics-based mechanics
   - Pocket coins using a striker with realistic collision detection
   - Score tracking for both players

2. **Advanced Physics Engine**:
   - Friction modeling for natural deceleration
   - Elastic collisions between coins/striker
   - Momentum conservation in collisions
   - Pocket detection with animation effects

3. **Visual Elements**:
   - High-quality carrom board with wooden texture
   - Realistic coin designs (white, black, red queen)
   - Striker with aiming guide (rotating arc)
   - Animated pocketing effects (coins shrink into pockets)
   - Player turn indicators with border animations

4. **Game Flow Management**:
   - Turn-based gameplay with player switching
   - Automatic scoring and win detection
   - Queen covering mechanics (special rules for red coin)
   - Foul detection and penalty system:
     - Striker pocketing
     - Failed queen cover attempts
     - Penalty coin placement

5. **Special Features**:
   - **Pre-game coin rotation**: Customize starting positions
   - **Time-limited turns**: 10-second shot timer with visual warning
   - **Dynamic camera**: Board rotates 180° when players switch sides
   - **Win animations**: Celebration effects with winner announcement

6. **Audio System**:
   - Collision sounds (different for coin-coin and coin-edge)
   - Pocketing sounds (distinct for coins vs queen)
   - Striker dragging friction sound
   - Turn timer ticking sound
   - Victory/foul sound effects

7. **Game Management**:
   - Save/Load functionality (persists between sessions)
   - Pause/resume with menu
   - Main menu with New Game/Continue options
   - Automatic game state saving on exit
   - Window position/size memory

### Technical Implementation Highlights:
1. **Physics Simulation**:
   - Velocity vectors and friction calculations
   - Collision response using impulse physics
   - Minimum velocity thresholds for movement

2. **UI Components**:
   - Custom slider for striker positioning
   - Drag-based power control for shots
   - Dynamic aiming line with dot trajectory
   - Animated text overlays (fouls, wins, queen cover)

3. **Game State Management**:
   - JSON-based save format
   - Config file for window settings
   - Player statistics persistence
   - Turn state tracking

4. **Resource Handling**:
   - Cross-platform resource loading
   - Windows-specific taskbar integration
   - Dynamic asset scaling
   - Error handling for missing files

5. **Animation System**:
   - Coin pocketing animations
   - Border pulse animations for turn timer
   - Text scaling/color effects
   - Smooth overlay transitions

### Game Rules Implementation:
- **Standard Carrom Rules** with 9 white/black coins + 1 red queen
- **Queen Cover Requirement**: Must pocket a color coin after queen
- **Foul Penalties**:
  - Return pocketed coin to center
  - Place extra coin if no coins pocketed
- **Turn Continuation**: Player continues after successful pocket
- **Win Condition**: Pocket all coins + cover queen first

The game provides a complete digital carrom experience with realistic physics, engaging visuals, and comprehensive game management features suitable for both casual play and competitive matches.

# Demo Images
<img width="815" height="981" alt="Screenshot 2025-07-18 110357" src="https://github.com/user-attachments/assets/dc02264b-62f4-42a4-a0ac-0e27cb2eb723" />
<img width="834" height="997" alt="Screenshot 2025-07-18 110431" src="https://github.com/user-attachments/assets/637eae3e-fc05-40a3-a0c2-45ee3f9f0d7e" />
<img width="817" height="986" alt="Screenshot 2025-07-18 110500" src="https://github.com/user-attachments/assets/aef8eb4a-fc61-406e-9cf8-4c6b5a181b61" />
<img width="815" height="985" alt="Screenshot 2025-07-18 110521" src="https://github.com/user-attachments/assets/d1f396bd-846c-4cb1-ab28-53dd4c2c0b55" />
<img width="817" height="992" alt="Screenshot 2025-07-18 110533" src="https://github.com/user-attachments/assets/bddb1595-955f-4b93-b187-aeedc9793124" />
<img width="811" height="987" alt="Screenshot 2025-07-18 110551" src="https://github.com/user-attachments/assets/a30465a8-0027-4e7c-8eee-d455ebe1be1f" />

# DEMO VIDEO


https://github.com/user-attachments/assets/f097b4ec-14be-49a9-9218-8f2f0b337314



