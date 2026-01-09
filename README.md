# MBII Chaos Plugin
The `chaos.py` script is a comprehensive RPG-style server management system for **Movie Battles II** that integrates character progression, a dynamic economy, and real-time server-state awareness.

## 🛡️ Core Systems

### 1. The Core Progression System
* **20-Tier Career Paths**: There are 14 distinct career paths (7 Hero, 7 Villain), each containing 20 unique titles that evolve every 2.5 levels.
* **Leveling & XP**: Players earn XP through kills and lose a configurable amount upon death[cite: 1, 2]. "Last Stand Protection" prevents XP from dropping below zero.
* **Dynamic Title Logic**: The `get_title` system automatically assigns colors (Cyan for Heroes, Red for Villains) and ranks based on the player's chosen faction and current level.

### 2. "Smart Switch" Mode Awareness
* **Duel Mode Restriction (Mode 3)**: The script scans the server's `g_authenticity` setting; if set to Mode 3, all players are visually restricted to "Jedi" or "Sith" titles.
* **Open Mode (0, 1, 2, 4)**: In all other modes, the full diversity of careers (Mandalorian, ARC Trooper, Droideka, etc.) is unlocked.
* **Command Blocking**: If a player attempts to change to a non-Force career while in Duel Mode, the script blocks the change with an error message.

### 3. Economic & Gambling Features
* **Banking System**: Players accumulate credits via passive gains or kills to spend on bounties, bets, or pazaak.
* **Pazaak (Casino)**: A card game where players can `!hit` or `!stand` against a dealer, featuring a **3x payout** for hitting exactly 20.
* **Bounty & Bet Systems**: Place bounties on rivals or bet on allies; successful kills collect these pots and announce payouts to the server.
* **Peer-to-Peer Transfers**: The `!pay` command allows players to transfer credits directly to one another.

### 4. Advanced Combat Logic
* **Force Surge**: A rare (5%) chance on any kill to trigger a "Force Surge," granting the killer **3x XP**
* **Nemesis System**: Tracks "dominance" by announcing when one player kills another three times in a row
* **Global Kill Feed**: Replaces standard messages with high-visibility RCON announcements showing titles, XP gains, and credit rewards

### 5. Persistent Infrastructure
* **Shared Database**: SQLite Database: Migrated from JSON to players.db. It uses clean_name (normalized via unicodedata) as the PRIMARY KEY to ensure players keep their stats regardless of name symbols or color codes.
* **Name-Based Syncing**: The sync_current_players function uses a Regex anchor `r'^\s*(\d+)\s+-?\d+\s+\d+\s+(.*?)\s+\d+\s+\d{1,3}\.\d'` to correctly parse names even if they contain spaces or ASCII symbols.
* **Multi-Server Ready**: Designed for multi-port environments. Every database connection uses timeout=20 to prevent "Database is locked" errors when two or more server ports write to the shared players.db simultaneously.

---

## 🛠️Game Commands
| Command | Function |
| :--- | :--- |
| \`!rank\` / \`!level\` | Check your current level, title, and XP progress. |
| \`!title <name>\` | Choose your career path (e.g., \`!title mando\`). |
| \`!pazaak <amt>\` | Start a card game against the dealer. |
| \`!bet <name> <amt>\` | Bet on another player to win their next fight. |
| \`!top\` / \`!wealth\` | View the XP or Credit leaderboards. |

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