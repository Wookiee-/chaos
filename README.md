# MBII Chaos Plugin
The `chaos.py` script is a comprehensive RPG-style server management system for **Movie Battles II** that integrates character progression, a dynamic economy, and real-time server-state awareness.

## 🛡️ Core Systems

### 1. Career & Identification Systems
* **20-Tier Career Paths**: 14 distinct paths (e.g., Rebel, ARC Trooper, Droideka, Sith) are fully implemented, each featuring 20 unique titles.
* **Title Evolution**: Ranks evolve every 2.5 levels. The `!title` list command uses a 4-line split to ensure 100% visibility in the JKA console.
* **Imperial Datapad (`!stats`)**: Displays real-time global standings and uses a text-based telemetry bar `[IIIIII....]` for clear progress tracking.
* **Last Stand Protocol**: XP is deducted on casualties, but a safety check ensures clearance never drops below Level 1 (XP 0).

### 2. "Smart Switch" Mode Awareness
* **Duel Mode Protocol**: Automatically detects `g_authenticity` settings (Mode 3). When active, it forces Jedi/Sith titles regardless of the player's career.
* **Command Filtering**: The `!title` help menu dynamically updates based on the active server mode to prevent invalid career selections.

### 3. Economic & Cantina Features
* **Holo-Slots (!holo / !slot)**: A high-stakes terminal costing 150cr per spin. Features rewards for 3, 4, and 5 matches (up to 10,000cr) with a 10% chance for a random x2-x5 multiplier on wins.
* **High-Low (!highlo)**: A rapid-fire gambling game where players bet an amount and guess if a second hidden card will be "high" or "low" compared to the first.
    - Payout: Winning doubles the bet (2x payout), while losing contributes the full bet to the House Vault.
* **Banking & Pazaak**: Persistent credit storage in `players.db` with a full Pazaak system including side-decks and persistent dealer pots.
* **Deathroll (PvP Gambling)**: Managed via a global dictionary in the main plugin to ensure reliable match handling between different players.
* **Sarlacc Lottery**: A global server event where the pot and entrants are tracked by the plugin and awarded at the end of the map.

### 4. Advanced Combat Logic
* **Killstreaks & Nemesis**: Tracks consecutive eliminations and identifies a "Nemesis" after 3 kills on the same target. Terminating a Nemesis grants a +200cr Revenge Bonus.
* **Force Surge & Theft**: Includes a 5% chance for a 3x XP Surge on kills and triggers a 5% capital transfer when eliminating "High-Value Targets" (>5,000cr).
* **Vault Heists**: Every kill adds a 5cr "tax" to the House Vault. Players have a 1% chance on kill to breach the vault, stealing 20% (or 50% for "Mega Heists" if the vault exceeds 5,000cr).

### 5. Persistent Infrastructure
* **IP-Based Record Syncing**: The system uses IP signatures to automatically re-link XP, credits, and career progress if a player changes their alias.
* **Multi-Instance Stability**: Employs SQLite timeout and commit logic to allow multiple server instances to share the same database without corruption.

### 6. Asset Protection & Anti-Grief
* **Traitor Sanctions**: Automatically detects Team Kills, penalizing traitors -500 XP and -1000cr with a global condemnation message.
* **Environment Filtering**: Suicides and world deaths (falling, hazards) are ignored to prevent XP farming and economic manipulation.
* **Leaderboard Promotion**: Uses a persistent is_top5 flag to ensure global announcements only trigger once when a player breaks into the Top 5.

---

## 🛠️Game Commands
| Command | Functional Parameters 
| :--- | :--- 
| **Identity** |
| \`!stats\` / \`!rank\` | Access your Imperial Datapad (Dossier, Sector Rank, & Training). |
| \`!title <name>,<career_name>\` | Select your career path (e.g., !title mando). Force-only in Duel. |
| \`!bank\` | Query personal credit reserves. |
| **Finance** |
| \`!pay <name> <amt>\` | Authorize a secure credit transfer to another player. |
| \`!top\` / !\`wealth\` | Display top-tier personnel (XP Leaderboard or Credit Rankings). |
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