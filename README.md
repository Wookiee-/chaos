# MBII Chaos Plugin
The `chaos.py` script is a comprehensive RPG-style server management system for **Movie Battles II** that integrates character progression, a dynamic economy, and real-time server-state awareness.

## 🛡️ Core Systems

### 1. The Core Progression System
* **20-Tier Career Paths**: There are 14 distinct career paths (7 Hero, 7 Villain), each containing 20 unique titles that evolve every 2.5 levels.
* **Leveling & XP**: Players earn XP through kills and lose a configurable amount upon death[cite: 1, 2]. "Last Stand Protection" prevents XP from dropping below zero.
* **Dynamic Title Logic**: The `get_title` system automatically assigns colors (Cyan for Heroes, Red for Villains) and ranks based on the player's chosen faction and current level.

### 2. "Smart Switch" Mode Awareness
* **Duel Mode Restriction (Mode 3)**: Automatically detects `g_authenticity` setting and restricts all players to "Jedi" or "Sith" titles, regardless of their chosen career.
* **Open Mode (0, 1, 2, 4)**: In all other modes, the full diversity of careers (Mandalorian, ARC Trooper, Droideka, etc.) is unlocked.
* **Command Blocking**: Prevents players from switching to non-Force careers via `!title` while the server is in Duel Mode.

### 3. Economic & Gambling Features
* **Banking System**: Credits are stored in the SQLite `players.db`. Players earn a `passive_credit_gain` on every kill.
* **Pazaak (Casino)**: A fully functional !pazaak game with `!hit` and `!stand` commands. Features a **3x** payout for hitting exactly 20 and a persistent **Dealer Pot**.
* **Bounty & Bet Systems**: Contributors can pool credits onto a target's head. The `process_kill` logic automatically sums the dictionary and awards the total to the victor.
* **Peer-to-Peer Transfers**: Validated `!pay` transfers allow players to move capital between accounts safely.

### 4. Advanced Combat Logic

* **Killing Spree System**: Tracks consecutive kills without dying. Triggers global server announcements at 5 (Killing Spree), 10 (Unstoppable), and 15 (Godlike) kills.
* **Nemesis & Revenge**: Tracks "dominance" (3+ kills in a row). Breaking a Nemesis cycle grants a +200cr Revenge Bonus and resets the feud.
* **Force Surge**: A 5% chance on any kill to trigger a surge, granting 3x XP.
* **Wealth Redistribution (Theft)**: Killing a "Wealthy" player (over 5,000cr) automatically steals 5% of their credits for the killer.
* **Bank Heist**: A rare 1% chance to "crack the House Vault," stealing 20% of the Pazaak Dealer's credits.

### 5. Persistent Infrastructure

* **IP-Based Record Syncing**: The database now tracks `last_ip`. If a player changes their name, the script recognizes their IP and automatically re-links their XP, credits, and titles to the new name.
* **SQLite Backend**: Migrated to `players.db` using `clean_name` as a primary key. This ensures data persistence across name changes and server restarts.
* **Multi-Port Ready**: Uses `timeout=20` and `conn.commit()` logic to allow multiple server instances (different ports) to read and write to the same database file without corruption or locking issues.
* **Robust Regex Parsing**: Captures Slot ID, Name, and IP simultaneously to ensure the script always knows exactly who is on the server at any given second.

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