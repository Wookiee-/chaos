# MBII Chaos Plugin
A Python-based RCON and log-parsing integration for **Movie Battles II**. This plugin transforms a standard server into a persistent RPG environment with real-time tracking of player progress, economy, and dynamic roles.

## 🛡️ Core Systems

### 1. Persistent RPG Progression
The script monitors server logs to translate gameplay into experience points (XP).
* **XP Economy**: Configurable rewards (default: +25 XP per kill, -15 XP per death).
* **Leveling System**: 50 levels of progression based on the \`xp_per_level\` setting.
* **Career Paths**: 14+ factions including Jedi, Sith, Mandalorian, and ARC Trooper with unique titles every 2.5 levels.
* **Data Persistence**: All stats are stored in \`players.json\`.

### 2. Economy & Bounties
* **Credits**: Earned through kills and passive income.
* **Bounties**: Use \`!bounty <name> <amount>\` to place hits on players. Credits are held in escrow and paid to the killer automatically.
* **Transfers**: Players can send funds to others using the \`!pay\` command.

### 3. Pazaak Gambling
* **High-Stakes AI**: Play against a "House" AI with adjustable difficulty.
* **Special Rules**: Hitting exactly 20 pays out **3x the wager**.
* **Dealer Pot**: Failed bets increase the "Dealer Bonus," which can be won by beating the house.

### 4. Advanced RCON (Linux Fix)
* **Packet Reconstruction**: Solves the "fragmented UDP" issue on Linux MBII servers to ensure reliable communication.
* **Slot ID Resolution**: Correct indexing for players in high-numbered slots (e.g., Slot 17+).

## 🛠️ Management & Commands
| Command | Function |
| :--- | :--- |
| \`!rank\` / \`!level\` | Check your current level, title, and XP progress. |
| \`!title <name>\` | Choose your career path (e.g., \`!title mando\`). |
| \`!pazaak <amt>\` | Start a card game against the dealer. |
| \`!bet <name> <amt>\` | Bet on another player to win their next fight. |
| \`!top\` / \`!wealth\` | View the XP or Credit leaderboards. |

## 🚀 Execution (Linux)
Use the provided shell script to manage the background process:
\`\`\`bash
./start_chaos.sh start    # Start the plugin in a screen session
./start_chaos.sh status   # Check if plugin is running
./start_chaos.sh attach   # View live logs
\`\`\`
