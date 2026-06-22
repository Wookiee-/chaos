# MBII Chaos Plugin: Career & Economic Framework

A high-performance Python framework for Movie Battles II (Jedi Academy) that introduces persistent progression, a galactic economy, and dynamic career systems.

## 🛡️ Core Systems

### 1. Career & Identification Systems
* **Unlimited Progression**: An XP system with no level cap. Players climb indefinitely — the only limit is their dedication. Titles evolve every 10 levels to reflect the player's growing legend.
* **100 Titles Per Career**: Each of the 14 career paths features 100 unique titles. The first 20 are hand-crafted; titles 21-100 are dynamically generated using tier prefixes (Veteran, Elite, Master, Grand, Prime, Transcendent, Eternal, Mythic) with path-specific core nouns.
* **UI Stability Protocol**: Optimized for the JKA engine's font rendering; uses color-code anchoring to eliminate spacing gaps and "Chaos" text alignment issues in the chat box.
* **Imperial Datapad (`!rank`)**: Displays real-time global standings with a text-based telemetry bar `[IIIIII....]` for clear visual progress tracking.
* **Last Stand Protocol**: Dynamic XP deduction on casualties with a safety floor to maintain player retention.

### 2. "Smart Switch" Mode Awareness
* **Duel Mode Protocol**: Real-time detection of `g_authenticity` (Mode 3). When active, the system overrides selected careers to force Jedi/Sith titles for immersion.
* **Dynamic Command Filtering**: The `!title` system and help menus automatically update their logic based on active server variables (cvars) to prevent invalid career selections.

### 3. Economic & Banking
* **Galactic Banking**: Persistent credit storage utilizing JSON. Credits are earned through combat and saved instantly via IP/GUID signatures to prevent data loss.
* **Pazaak Implementation**: A full replica of the KOTOR card game. Features include customizable side-decks (`!pazaak`), dealer pots, and persistent session handling to ensure bets are refunded on script restarts.

### 4. Advanced Combat Logic
* **Dynamic XP System**: XP rewards scale dynamically based on three factors:
  - **Level Scaling**: Bonus XP based on the victim's level (`victim.level ÷ xp_level_scaling`)
  - **Underdog Bonus**: Extra XP for killing higher-level enemies (`victim.level - killer.level`)
  - **Faction Warfare**: Bonus XP for cross-faction kills (Hero vs Villain)
* **Dynamic XP Loss**: XP loss on death mirrors the gain formula — higher-level killers inflict more XP loss.
* **Killstreaks & Nemesis**: Tracks consecutive eliminations. Identifying a "Nemesis" (3+ kills on same target) unlocks a +200cr Revenge Bonus for the victim upon retaliation.
* **Force Surge**: Random 5% chance for a 3x XP boost on kills.
* **Force Drain**: Random 5% chance for a 3x XP penalty on death — the dark mirror of Force Surge. Both events are independent and can occur simultaneously on the same kill.
* **Capital Theft**: 5% credit transfer when eliminating High-Value Targets (>5,000cr).
* **Vault Heists**: A 5cr "House Tax" is applied to every kill. Players have a 1% chance to breach the vault, stealing 20%—or a 50% "Mega Heist" if the vault exceeds 5,000cr.

### 5. Infrastructure & Security
* **SMOD Admin Integration**: A robust parser for `SMOD smsay` that allows admins to manage the economy and levels in real-time with global `[ADMIN]` chat feedback. Admin commands have no level caps.
* **RCON Sync Engine**: Forces real-time name resolution via RCON `status` to prevent "New Player" placeholders and ensure 100% accurate database logging.
* **Multi-Instance Stability**: Employs file-locking and atomic writes, allowing multiple server instances to share a single `players.json` without corruption.

---

## 🛠️ Game Commands

Available to all players in the sector via global chat.

| Command | Functional Parameters |
| :--- | :--- |
| **Identity** | |
| `!rank` | Access your Imperial Datapad (Dossier, Sector Rank, & Training). |
| `!title <career>` | Select your career path (e.g., `!title mando`). Use `!title list` to see all 100 titles. Force-only in Duel. |
| `!bank` | Query personal credit reserves. |
| **Finance** | |
| `!pay <name> <amt>` | Authorize a secure credit transfer to another player. |
| `!top` / `!wealth` | Display top-tier personnel (XP Leaderboard or Credit Rankings). |
| `!vault` | Check House Vault reserves (Monitors Heist potential). |
| **Contracts** | |
| `!bounty <name> <amt>` | Issue a contract on a target's head. |
| `!bounties` | View all currently active Marks in the sector. |
| **Minigames** | |
| `!pazaak` | Challenge the Dealer or a player to a game of Pazaak. |

---

## 🛡️ SMOD Admin Commands

Authorized SMODs can manage the server via `smsay` (Admin Chat). All actions are broadcast in the `[ADMIN]` format.

| Command | Arguments | Description |
| :--- | :--- | :--- |
| `!help` | N/A | Lists all available Chaos admin commands. |
| `!setlevel` | `<name> <level>` | Sets a player's level (no cap). |
| `!givexp` | `<name> <amount>` | Adds XP to a player (no cap). |
| `!takexp` | `<name> <amount>` | Deducts XP from a player (Floor at Lv. 1). |
| `!givecredits`| `<name> <amount>` | Adds credits to a player's bank balance. |
| `!takecredits`| `<name> <amount>` | Removes credits from a player's balance. |
| `!resetplayer`| `<name>` | Completely wipes a player's XP and Credits. |

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

# --- Progression ---
xp_per_kill = 25            # Base XP awarded per kill
xp_loss = 15                # Base XP lost on death
xp_per_level = 250          # XP required per level
starting_credits = 100      # Credits new players start with

# --- Dynamic XP Scaling ---
faction_bonus = 15          # Bonus XP for cross-faction kills (Hero vs Villain)
xp_level_scaling = 10       # Lower = faster level scaling (e.g., 5 = 2x, 20 = half)

# --- Economy ---
passive_credit_gain = 10    # Credits earned per kill
db_file = players.json      # Persistent player database

# --- Pazaak ---
pazaak_difficulty = 15      # Dealer minimum hand (higher = harder)
```

### Dynamic XP Formula

When a kill occurs, XP is calculated as follows:

**Killer XP Gain:**
```
base_xp + (victim.level ÷ xp_level_scaling) + max(0, victim.level - killer.level) + faction_bonus
```

**Victim XP Loss:**
```
base_loss + (killer.level ÷ xp_level_scaling) + max(0, killer.level - victim.level) + faction_bonus
```

### Random Events

**Force Surge** (5% chance) — The killer's XP gain is tripled.

**Force Drain** (5% chance) — The victim's XP loss is tripled.

Both events are independent and can trigger on the same kill (e.g., a Force Surged killer dealing a Force Drained victim).

**Faction alignment** determines the cross-faction bonus:
- **Heroes**: Rebel, Elite Trooper, Clone Trooper, ARC Trooper, Hero, Wookiee, Jedi
- **Villains**: Imperial, Commander, Bounty Hunter, Mandalorian, Droideka, SBD, Sith

### 💡 Pro-Tip for Linux Paths
If you are running multiple servers on one Linux machine, your path will typically look like this:
`/home/mbiiez/server1/MBII/server.log`

### 💡 Pro-Tip for Windows Paths
In Python (which `chaos.py` uses), backslashes in Windows paths can sometimes cause issues. It is often safer to use double backslashes or forward slashes in the config file:
`logname = C:\\Users\\Admin\\Desktop\\MBII\\GameDatabase\\MBII\\server.log`
**OR**
`logname = C:/Users/Admin/Desktop/MBII/GameDatabase/MBII/server.log`

## 📋 Multi-Server Configuration (`server1.cfg`, `server2.cfg`)

For running multiple server instances, each server gets its own config file. The files are identical in format to `chaos.cfg` — just copy and adjust the unique values (ports, RCON passwords, log paths).

```ini
# server1.cfg
[SETTINGS]
ip = 127.0.0.1
port = 29070
rcon = server1_password
logname = /home/mbiiez/server1/MBII/server.log
db_file = players.json  # Shared DB allows cross-server persistence!
# ... all other settings same as chaos.cfg
```

```ini
# server2.cfg
[SETTINGS]
ip = 127.0.0.1
port = 29071
rcon = server2_password
logname = /home/mbiiez/server2/MBII/server.log
db_file = players.json  # Same DB file = shared progression
# ... all other settings same as chaos.cfg
```

> **Note**: All configs can share the same `db_file` — the plugin uses file-locking to prevent corruption, so players keep their levels and credits across servers.

---

## 🛠️ Management & Execution

### 🐧 Linux (Ubuntu/Debian)
Requires `screen` and `python3`.
* **Single Server**: `./start_chaos.sh {start|stop|status|attach}`
* **Multi-Server**: `./multi_chaos.sh start server1.cfg`

### 🪟 Windows
* **Menu Management**: Run `start_chaos.bat` for a guided UI
* **Multi-Server**: `multi_chaos.bat start server1.cfg`
