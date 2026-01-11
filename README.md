# MBII Chaos Plugin
The `chaos.py` script is a comprehensive RPG-style server management system for **Movie Battles II** that integrates character progression, a dynamic economy, and real-time server-state awareness.

## 🛡️ Core Systems

### 1. Career & Identification Systems
 * **20-Tier Career Paths**: 14 distinct career paths (7 Hero, 7 Villain), each featuring 20 unique titles that evolve every 2.5 levels.
 * **Access Clearance (Leveling)**: Players gain XP through eliminations and lose progress upon casualties. A "Last Stand" protocol prevents clearance from dropping below Level 1.
 * **Imperial Datapad (Dossier)**: Consolidates !level, !rank, and !stats into a single immersive terminal view.
 * **Automated Rank Calculation**: The !stats command queries the global database in real-time to display the player's exact numerical standing (e.g., 1st of 500 players) within the sector.
 * **Optimized Progress Display**: Employs a text-based telemetry bar [====>-] to bypass engine limitations and provide 100% visibility in the game console.

### 2. "Smart Switch" Mode Awareness
* **Duel Mode Protocol (Mode 3)**: Automatically detects g_authenticity settings, restricting all personnel to "Jedi" or "Sith" clearance titles, regardless of their career choice.
* **Open Mode Unlocks**: In all other modes (Open/Semi-Open), the full diversity of careers (Mandalorian, ARC Trooper, Droideka, etc.) is automatically enabled.
* **Command Filtering**: The !title interface dynamically updates its help menu based on the active server mode to prevent invalid career selections.

### 3. Economic & Cantina Features
* **Banking Infrastructure**: Credits are secured in the players.db. Every elimination grants a passive credit gain.
* **Cantina Games (Pazaak)**: A high-stakes Pazaak system with !hit, !stand, and !side (side-deck) commands. Features a 3x payout for a "Natural 20" and a persistent Dealer Pot.
* **Deathroll (PvP Gambling)**: A turn-based high-low rolling game with an integrated turn-handler (!roll) to ensure fair play between challengers.
* **Bounty Contracts**: Players can place credits on a target's head. The process_kill logic automatically liquidates the contract and awards the total to the successful hunter.
* **Sarlacc Lottery**: A server-wide pool where players buy in via !sarlacc. The entire pot is awarded to one random survivor at the end of the map.

### 4. Advanced Combat Logic
* **Imperial Killstreaks**: Tracks consecutive eliminations without a casualty, broadcasting global "War Reports" to the entire server.
* **Nemesis & Revenge**: Identifies "dominance" (3+ kills on a single player). Terminating a Nemesis grants a +200cr Revenge Bonus and clears the feud logs.
* **Force Surge**: A 5% chance on any elimination to trigger a surge, granting 3x XP.
* **Wealth Redistribution (Theft)**: Eliminating a "High-Value Target" (over 5,000cr) automatically transfers 5% of their liquid capital to the victor.
* **Progressive Vault Heist**: A 1% chance on kill to breach the House Vault, stealing 20% of the Dealer's credits.
* **Vault Escalation**: Every kill on the server adds a 5cr "tax" to the House Vault. If the vault exceeds 5,000cr, the reward escalates to a 50% Mega Heist.

### 5. Persistent Infrastructure
* **IP-Based Record Syncing**: The database tracks last_ip. If a player changes their alias, the system recognizes the IP signature and automatically re-links their XP, credits, and career progress.
* **Multi-Instance Ready**: Uses SQLite timeout=20 and conn.commit() logic, allowing multiple server instances (e.g., Port 29070 and 29071) to share the same database without corruption.
* **Robust Regex Parsing**: Captures Slot ID, Name, and IP simultaneously, ensuring the script maintains 100% accuracy of the "Who's Who" on the server.

### 6. Asset Protection & Anti-Grief
* **Live Team Tracking**: Monitors Team IDs (Rebel vs. Imperial) in real-time to prevent friendly-fire rewards.
* **Traitor Sanctions**: Automatically detects Team Kills. Traitors are penalized -500 XP and -1000cr, accompanied by a global server-wide condemnation.
* **Environment Filtering**: Ignores world deaths (falling, hazards) and suicides to protect player XP and prevent "farming" of the economy.
* **Anti-Farming Logic**: Validates both the killer and victim's team status before any XP or Credit rewards are finalized..

---

## 🛠️Game Commands
| Command | Functional Parameters | Datapad Action |
| :--- | :--- |
| **Identity** |
| \`!stats\` / \`!rank\` | Access your Imperial Datapad (Dossier, Sector Rank, & Training). |
| \`!title <name>,<career_name>\` | Select your career path (e.g., !title mando). Force-only in Duel. |
| \`!bank\` | Query personal credit reserves. |
| **Finance** |
| \`!pay <name> <amt>\` | Authorize a secure credit transfer to another player. |
| \`!top\` / !\`wealth\` | (Global),Display top-tier personnel (XP Leaderboard or Credit Rankings). |
| \`!vault\` | Check House Vault reserves (Monitors Heist potential). |
| **Contracts** |
| \`!bounty <name> <amt> | Issue a contract on a target's head. |
| \`!bounties\` | View all currently active Marks in the sector. |
| **Cantina Games** |
| \`!pazaak <amt>\` | Start a match vs Dealer. Use !hit, !stand, or !side. |
| \`!deathroll <name> <amt>\` | Challenge a peer to a roll-off. Use !roll to execute turns. |
| \`!sarlacc\` |Purchase a lottery ticket (500cr) for the map-end payout. |
| \`!highlo\` / \`!holo,<amt>\` | Standard games of chance and holotable slots. |

---

## ⚙️ Plugin Configuration (`chaos.cfg`)
The `logname` must be the **absolute path** to your server's log file so the plugin can read game events as they happen.

```ini
[SETTINGS]
ip = 127.0.0.1
port = 29070
rcon = your_password

# --- LOG PATH EXAMPLES ---
# Linux: /home/username/mbii/GameDatabase/MBII/server.log
# Windows: C:\Games\MBII\GameDatabase\MBII\server.log
logname = /path/to/your/server.log

db_file = players.json
xp_per_kill = 25
xp_loss = 15
xp_per_level = 250
starting_credits = 100
pazaak_difficulty = 15
```
---

### Server.cfg

### 💡 Pro-Tip for Linux Paths
If you are running multiple servers on one Linux machine, your path will typically look like this:
`/home/mbiiez/server1/MBII/server.log`

### 💡 Pro-Tip for Windows Paths
In Python (which `chaos.py` uses), backslashes in Windows paths can sometimes cause issues. It is often safer to use double backslashes or forward slashes in the config file:
`logname = C:\\Users\\Admin\\Desktop\\MBII\\GameDatabase\\MBII\\server.log`
**OR**
`logname = C:/Users/Admin/Desktop/MBII/GameDatabase/MBII/server.log`

---

## 🛠️ Management & Execution

### 🐧 Linux (Ubuntu/Debian)
Requires `screen` and `python3`.
* **Single Server**: `./start_chaos.sh {start|stop|status|attach}`
* **Multi-Server**: `./multi_chaos.sh start server1.cfg`. 

### 🪟 Windows
* **Menu Management**: Run `start_chaos.bat` for a guided UI
* **Multi-Server**: `multi_chaos.bat start server1.cfg`.