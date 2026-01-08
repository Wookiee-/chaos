# MBII Chaos Plugin

A Python-based RCON integration for Movie Battles II that adds an RPG-style layer to your server. 

## 🛡️ Feature Deep-Dive

### 1. RPG Progression (XP & Leveling)
* [cite_start]**XP Economy**: Players earn a configurable amount of XP per kill and lose XP upon death[cite: 1].
* [cite_start]**Leveling Thresholds**: The `xp_per_level` setting determines the difficulty of reaching the next rank[cite: 1].
* [cite_start]**Persistence**: All progress is stored in a local JSON database[cite: 1].

### 2. Economy & Bounties
* [cite_start]**Starting Capital**: New players are granted an initial credit balance[cite: 1].
* [cite_start]**Passive Income**: Players earn a steady flow of credits while active on the server[cite: 1].
* **Bounty Hunting**: Players can place hits on others; the killer automatically claims the reward.

### 3. High-Stakes Pazaak (Gambling)
* [cite_start]**Difficulty Tuning**: Adjustable dealer behavior via `pazaak_difficulty`[cite: 1].
* **Special Payouts**: Achieving a score of 20 grants a 3x payout.

### 4. Advanced RCON Synchronization (Linux Fix)
* **Multi-Packet Reconstruction**: Engineered to capture fragmented UDP packets on Linux, ensuring players in high Slot IDs (like Slot 17) are correctly indexed.

## 🛠️ Configuration & Management

### 1. Configuration (`chaos.cfg`)
 [cite_start][cite: 1]
\`\`\`ini
[SETTINGS]
ip = 127.0.0.1
port = 29070
rcon = your_password
logname = server.log
xp_per_kill = 25
xp_loss = 15
xp_per_level = 250
starting_credits = 100
passive_credit_gain = 10
db_file = players.json
pazaak_difficulty = 15
\`\`\`

### 2. Management Script (`start_chaos.sh`)

\`\`\`bash
# Start: ./start_chaos.sh start
# View: ./start_chaos.sh attach
# Stop: ./start_chaos.sh stop
\`\`\`
