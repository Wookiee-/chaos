# MBII Chaos Plugin

A Python-based RCON and log-parsing integration for Movie Battles II. This plugin transforms a standard server into a persistent RPG environment with real-time tracking of player progress, economy, and dynamic roles.

## 🛡️ Core Systems & Features

### 1. Persistent RPG Progression
The script monitors server logs for kill/death events and translates them into experience points (XP).
* **XP Economy**: Rewards are configurable; default settings grant 25 XP per kill and deduct 15 XP upon death.
* **Leveling System**: Players progress through 50 levels. The leveling difficulty is determined by the `xp_per_level` config setting.
* **Career Paths & Titles**: Players can choose from various factions (e.g., Jedi, Sith, Mandalorian, ARC Trooper) and earn unique titles every 2.5 levels.
* **JSON Database**: All data is stored in `players.json`, ensuring progress persists across restarts.

### 2. Economy & Bounty System
* **Credit Gains**: Players start with a set balance and earn credits through kills and passive income while active.
* **Bounties**: Players can place hits on others using `!bounty`. The script holds the credits in escrow and automatically pays the killer upon a successful kill.

### 3. High-Stakes Pazaak (Gambling)
* **Dealer AI**: Players gamble credits against a "House" AI with adjustable difficulty levels.
* **Pazaak (20)**: Hitting exactly 20 triggers a special event, paying out 3x the player's wager.

### 4. Advanced RCON Synchronization (The Linux Fix)
Standard RCON clients often fail on Linux MBII servers because the `status` response is fragmented across multiple UDP packets.
* **Packet Reconstruction**: `chaos.py` uses a specialized loop to "listen" for all fragments of the server's response. 
* **Slot ID Resolution**: This ensures that even players in high Slot IDs (like Slot 17) are correctly indexed.

---

## 🛠️ Management & Execution

### 🐧 Choice 1: Linux (Ubuntu/Debian)

#### **A. Single Server Setup (`start_chaos.sh`)**
Best for a standalone server using the default `chaos.cfg`.
```bash
./start_chaos.sh start    # Starts Chaos in a background screen session
./start_chaos.sh status   # Checks if the process is active
./start_chaos.sh attach   # View live logs (Ctrl+A then D to detach)
./start_chaos.sh stop     # Gracefully shuts down the plugin
