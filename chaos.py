import os
import time
import re
import json
import socket
import sys
import random
import configparser
import sqlite3
import unicodedata

def normalize(name):
    if not name: return ""
    # Strip color codes (^ and whatever follows)
    name = re.sub(r'\^.', '', name)
    # Strip brackets and symbols
    name = re.sub(r'[^a-zA-Z0-9]', '', name)
    return name.lower().strip()

class Player:
    def __init__(self, sid, name, xp=0, kills=0, deaths=0, faction="jedi", credits=0, config=None):
        self.id = sid
        self.name = name
        self.xp = max(0, xp) 
        self.kills = kills
        self.deaths = deaths
        self.faction = faction.lower()
        self.streak = 0 
        self.credits = max(0, credits) 
        self.bounty = {}                      
        self.nemesis_map = {} 
        self.xp_per_lvl = int(config['xp_per_level'])
        self.dealer_credits = 0

    @property
    def level(self):
        lvl = (self.xp // self.xp_per_lvl) + 1
        return min(lvl, 50)

    @property
    def kdr(self):
        if self.deaths == 0: return float(self.kills)
        return round(self.kills / self.deaths, 2)

    def get_title(self, current_mode=0):
        lvl = self.level
        idx = int(min((lvl - 1) // 2.5, 19)) # Changes every 2.5 levels
        
        # Define the dictionary of 20-title paths
        paths = {
            "rebel": ["Rebel Recruit", "Rebel Grunt", "Rebel Soldier", "Frontline Scout", "Corporal", "Sergeant", "Staff Sergeant", "Master Sergeant", "Lieutenant", "Captain", "Major", "Lt Colonel", "Colonel", "Brigadier", "General", "High General", "Alliance Hero", "Alliance Leader", "Rebel Legend", "Freedom Fighter"],
            "elitetrooper": ["SpecOps Trainee", "Infiltrator", "Elite Trooper", "Commando", "Vanguard", "Specialist", "Elite Scout", "Pathfinder", "Saboteur", "Heavy Gunner", "Demolitions", "Marksman", "Elite Sergeant", "Elite Captain", "SpecOps Lead", "Elite Commander", "Tactical Lead", "Shadow Trooper", "Elite Legend", "Prime Commando"],
            "clonetrooper": ["Clone Shiny", "Clone Trooper", "Clone Private", "Clone Corporal", "Clone Sergeant", "Clone Lieutenant", "Clone Captain", "Clone Major", "Clone Commander", "Marshal Commander", "Regiment Lead", "Legion Commander", "Veteran Clone", "Frontline Clone", "Clone Hero", "Clone Specialist", "Tactical Clone", "Clone Guard", "Clone Legend", "Prime Clone"],
            "arctrooper": ["ARC Cadet", "ARC Trainee", "ARC Private", "ARC Trooper", "ARC Veteran", "ARC Scout", "ARC Sniper", "ARC Heavy", "ARC Sergeant", "ARC Lieutenant", "ARC Captain", "ARC Commander", "ARC Lead", "ARC Specialist", "Alpha Class", "Null Class", "ARC Hero", "ARC Legend", "Prime ARC", "ARC Overlord"],
            "hero": ["Hopeful", "Protector", "Defender", "Guardian", "Peacekeeper", "Champion", "Hero", "Veteran Hero", "Noble Hero", "Valiant Hero", "Bold Hero", "Renowned Hero", "Great Hero", "Grand Hero", "Galactic Hero", "Epic Hero", "Legendary Hero", "Mythic Hero", "Hero Legend", "Galactic Savior"],
            "wookiee": ["Wookiee Pup", "Wookiee Youth", "Wookiee Scout", "Wookiee Trainee", "Wookiee Warrior", "Wookiee Guard", "Wookiee Defender", "Wookiee Hunter", "Wookiee Tracker", "Wookiee Veteran", "Wookiee Berserker", "Wookiee Strongman", "Wookiee Brawler", "Wookiee Leader", "Wookiee Elder", "Wookiee Chieftain", "Forest Master", "Kashyyyk Hero", "Wookiee Legend", "The Great Bark"],
            
            "imperial": ["Imp Recruit", "Imp Trooper", "Imp Soldier", "Imp Guard", "Imp Corporal", "Imp Sergeant", "Staff Sergeant", "Master Sergeant", "Imp Lieutenant", "Imp Captain", "Imp Major", "Imp Colonel", "High Colonel", "Imp General", "High General", "Grand General", "Imperial Hero", "Imperial Leader", "Imperial Legend", "Empire's Hand"],
            "commander": ["Imp Cadet", "Imp Officer", "Field Officer", "Tactical Officer", "Lieutenant", "Flight Officer", "Staff Officer", "Captain", "Commander", "High Commander", "Major", "Lt Colonel", "Colonel", "Brigadier", "General", "Grand General", "Admiral", "Fleet Admiral", "Grand Admiral", "Supreme Commander"],
            "bountyhunter": ["Novice Hunter", "Amateur Hunter", "Contractor", "Tracker", "Enforcer", "Assassin", "Mercenary", "Bounty Hunter", "Professional Hunter", "Veteran Hunter", "Elite Hunter", "Master Hunter", "Notorious Hunter", "Famed Hunter", "Legendary Hunter", "Grand Hunter", "Prime Hunter", "Guild Master", "Hunter Legend", "The Ultimate Prize"],
            "mandalorian": ["Foundling", "Acolyte", "Initiate", "Mando Trainee", "Mando Warrior", "Mando Soldier", "Mando Guard", "Mando Veteran", "Mando Scout", "Mando Sniper", "Mando Heavy", "Clan Member", "Clan Guard", "Clan Leader", "House Leader", "Mando Hero", "Mando Commander", "The Armorer", "Mando Legend", "The Mandalore"],
            "droideka": ["Mk I Unit", "Mk II Unit", "Mk III Unit", "Drone", "Sentinel", "Guard", "Droideka", "Advanced Deka", "Elite Deka", "Heavy Deka", "Shield Deka", "Rapid Deka", "Sniper Deka", "Veteran Deka", "Droideka Master", "Droideka Prime", "Droideka Lead", "Droideka Ace", "Destroyer Prime", "The Rolling Death"],
            "sbd": ["B2 Unit", "B2 Grunt", "B2 Soldier", "B2 Guard", "B2 Trooper", "B2 Veteran", "B2 Elite", "B2 Specialist", "B2 Sniper", "B2 Heavy", "B2 Commando", "B2 Captain", "B2 Commander", "B2 Lead", "B2 Hero", "B2 Prime", "B2 Ace", "B2 Master", "B2 Legend", "Iron Will"],
            
            "jedi": ["Youngling", "Padawan", "Initiate", "Apprentice", "Service Corps", "Jedi Knight", "Jedi Hero", "Guardian", "Consular", "Sentinel", "Investigator", "Jedi Master", "Council Member", "Master of the Order", "Grand Master", "Force Spirit", "Force Entity", "The Chosen One", "Whill Overseer", "Jedi Legend"],
            "sith": ["Hopeful", "Acolyte", "Initiate", "Apprentice", "Neophyte", "Adept", "Soldier", "Warrior", "Marauder", "Assassin", "Executioner", "Champion", "Inquisitor", "Lord", "High Lord", "Darth", "Dark Councilor", "Sorcerer", "Overlord", "Sith Emperor"]
        }
        
        dark_side = ["imperial", "commander", "bountyhunter", "mandalorian", "droideka", "sbd", "sith"]

        if current_mode == 3:
            if self.faction in dark_side:
                title_list = paths["sith"]
                return f"^1{title_list[idx]}"
            else:
                title_list = paths["jedi"]
                return f"^5{title_list[idx]}"

        title_list = paths.get(self.faction, paths["jedi"])
        color = "^1" if self.faction in dark_side else "^5"
        
        return f"{color}{title_list[idx]}"

    def get_progress_bar(self):
        # Ensure we don't divide by zero
        if self.xp_per_lvl <= 0: return "[..........] 0/100"
        
        # Calculate XP within the current level
        xp_into_level = self.xp % self.xp_per_lvl
        percentage = min((1.0 * xp_into_level) / self.xp_per_lvl, 1.0)
        
        # 10-segment bar: I for filled, . for empty
        filled = int(percentage * 10)
        bar = "^2" + "I" * filled + "^7" + "." * (10 - filled)
        
        xp_left = self.xp_per_lvl - xp_into_level
        display_percent = int(percentage * 100)
        
        # Using /100 style to bypass the JKA % character filter
        return f"[{bar}^7] ^2{display_percent}^7/100 (^3{xp_left} XP left^7)"              

class MBIIChaosPlugin:
    def __init__(self):
        if len(sys.argv) > 1:
            self.config_file = sys.argv[1]
        else:
            self.config_file = 'chaos.cfg' # Default fallback
        self.settings = {}
        self.db_filename = 'players.db'
        self.load_config()
        self.players = []
        self.current_server_mode = 0
        self.active_bets = {}
        self.active_pazaak = {} # NEW: Tracks active card games
        self.dealer_credits = 0  
        self.init_sqlite()
        self.last_sync_time = 0

    def init_sqlite(self):
        with sqlite3.connect(self.db_filename, timeout=20) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    clean_name TEXT UNIQUE,
                    last_ip TEXT,
                    xp INTEGER DEFAULT 0,
                    credits INTEGER DEFAULT 100,
                    kills INTEGER DEFAULT 0,
                    deaths INTEGER DEFAULT 0,
                    faction TEXT DEFAULT 'jedi'
                )
            ''')
            conn.commit()

    def load_config(self):
        config = configparser.ConfigParser()
        # Uses absolute pathing regardless of OS
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, self.config_file)
        
        if not os.path.exists(config_path): 
            sys.exit(f"Error: {config_path} not found.")
        
        config.read(config_path)
        self.settings = dict(config['SETTINGS'])
        
        # Ensure the SQL database also uses compatible paths
        db_name = self.settings.get('db_file', 'players.db')
        self.db_filename = os.path.join(base_dir, db_name)

    def sync_player(self, sid, raw_name, ip="0.0.0.0"):
        # We still clean the name for display purposes (!top, !rank)
        display_name = re.sub(r'\^.', '', raw_name).replace('[', '').replace(']', '').strip()
        clean = normalize(raw_name)
        
        # Default stats for a brand new IP
        xp, kills, deaths, faction, credits = 0, 0, 0, "jedi", 100
        
        with sqlite3.connect(self.db_filename, timeout=20) as conn:
            cursor = conn.cursor()
            
            # --- THE IP-ONLY LOOKUP ---
            cursor.execute("SELECT clean_name, xp, kills, deaths, faction, credits FROM players WHERE last_ip = ?", (ip,))
            data = cursor.fetchone()
            
            if data:
                # Found existing user by IP!
                db_clean, xp, kills, deaths, faction, credits = data
                
                # --- THE FIX ---
                # ONLY update the display name. 
                # Removing 'clean_name = ?' here stops the UNIQUE constraint errors.
                try:
                    cursor.execute("UPDATE players SET name = ? WHERE last_ip = ?", (display_name, ip))
                    conn.commit()
                except sqlite3.Error as e:
                    print(f"[!] Update Error: {e}")
            else:
                # Truly a new IP (New Player)
                try:
                    cursor.execute("INSERT INTO players (name, clean_name, last_ip, xp, kills, deaths, faction, credits) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                   (display_name, clean, ip, xp, kills, deaths, faction, credits))
                    conn.commit()
                except sqlite3.IntegrityError:
                    # If this name is already taken by ANOTHER IP, give them a unique ID
                    unique_clean = f"{clean}_{int(time.time())}"
                    cursor.execute("INSERT INTO players (name, clean_name, last_ip, xp, kills, deaths, faction, credits) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                   (display_name, unique_clean, ip, xp, kills, deaths, faction, credits))
                    conn.commit()

        # Update Memory: Remove the old slot data to make room for the fresh sync
        self.players = [p for p in self.players if p.id != sid]
        
        # Note: We use the existing 'xp' and 'credits' found in the DB
        p = Player(sid, display_name, xp, kills, deaths, faction, credits, self.settings)
        p.raw_name = raw_name
        p.ip = ip 
        self.players.append(p)
        return p

    def save_player_stat(self, p):
        """Saves a single player's stats to SQLite. Call this after kills or transactions."""
        with sqlite3.connect(self.db_filename, timeout=20) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE players 
                SET xp = ?, credits = ?, kills = ?, deaths = ?, faction = ?, name = ?
                WHERE clean_name = ?
            ''', (p.xp, p.credits, p.kills, p.deaths, p.faction, p.name, normalize(p.name)))
            conn.commit()    

    def send_rcon(self, command, get_response=False):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client.settimeout(1.0)
            prefix = b'\xff\xff\xff\xff'
            msg = prefix + f'rcon "{self.settings["rcon"]}" {command}'.encode()
            client.sendto(msg, (self.settings["ip"], int(self.settings["port"])))
            
            if get_response:
                full_response = ""
                # We need to loop multiple times because the server 
                # sends ID 0-7, then ID 8-15, then ID 16-23 in separate bursts.
                for _ in range(10): 
                    try:
                        data, _ = client.recvfrom(65535) # Maximum UDP size
                        # Linux servers often prefix every packet with the same header
                        chunk = data.decode('utf-8', 'ignore').replace('\xff\xff\xff\xffprint\n', '')
                        full_response += chunk
                        
                        # If we see "50000" (the ping/rate column) near the end, 
                        # but the packet is small, it might be the end.
                        if len(data) < 500: break 
                    except socket.timeout:
                        break
                return full_response
            return None
        except Exception as e:
            print(f"RCON Error: {e}")
            return None

    def sync_current_players(self):
        response = self.send_rcon("status", True)
        if not response: 
            print("[!] Status check failed: No response from server.")
            return
        
        lines = response.split('\n')
        active_sids = []

        for line in lines:
            # NEW REGEX BASED ON YOUR SCREENSHOT:
            # 1. ^\s*(\d+) -> Capture Slot ID (2)
            # 2. \s+\-?\d+\s+\d+ -> Skip Score (0) and Ping (199)
            # 3. \s+(.*?)\s+ -> Capture Name (^7Valzhar), stopping at the first big space
            # 4. (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) -> Find the IP as the anchor
            match = re.search(r'^\s*(\d+)\s+\-?\d+\s+\d+\s+(.*?)\s{2,}(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
            
            if match:
                try:
                    sid = int(match.group(1))
                    raw_name = match.group(2).strip()
                    ip = match.group(3)
                    
                    # Your status shows ^7 before the name. Let's strip that.
                    if raw_name.startswith("^7"):
                        raw_name = raw_name[2:].strip()
                    
                    # Remove any extra quotes if the server adds them
                    raw_name = raw_name.replace('"', '')
                    
                    active_sids.append(sid)
                    
                    norm_name = normalize(raw_name)
                    p = next((x for x in self.players if normalize(x.name) == norm_name), None)
                    
                    if not p:
                        p = self.sync_player(sid, raw_name, ip)
                    else:
                        p.id = sid
                        
                except Exception as e:
                    print(f"[!] Status Parse Error: {e}")

        self.players = [p for p in self.players if p.id in active_sids]
        # print(f"[DEBUG] Sync Complete. Active Players: {[p.name for p in self.players]}")

    def check_rank_change(self, player, old_level):
        new_level = player.level
        current_title = player.get_title(self.current_server_mode)
        
        if new_level > old_level:
            self.send_rcon(f'say "^3RANK UP: ^2{player.name} ^7is now a {current_title} ^2(Lvl {new_level})!"')
            
            if new_level == 50:
                self.send_rcon(f'say "^5LEGENDARY: ^7{player.name} has reached the pinnacle of their career!"')
                
        elif new_level < old_level:
            self.send_rcon(f'say "^1DEMOTION: ^1{player.name} ^7has fallen to {current_title} ^1(Lvl {new_level})..."')

    def process_kill(self, k_id, v_id, w_id, raw_line=""):
        try: 
            k_id, v_id, w_id = int(k_id), int(v_id), int(w_id)
        except: return

        # 1. Capture names from the log line
        m = re.search(r'Kill:\s*\d+\s+\d+\s+\d+:\s*(.*?)\s+killed\s+(.*?)\s+by', raw_line)
        k_name_log = m.group(1).strip() if m else None
        v_name_log = m.group(2).strip() if m else None

        # 2. OBJECT RETRIEVAL (Look in memory first, don't wipe memory with sync_player yet)
        killer = next((x for x in self.players if x.id == k_id), None)
        victim = next((x for x in self.players if x.id == v_id), None)

        # Fallback: if they aren't in memory but are valid players, sync them now
        if not killer and k_id < 1000 and k_name_log:
            killer = self.sync_player(k_id, k_name_log)
        if not victim and v_id < 1000 and v_name_log:
            victim = self.sync_player(v_id, v_name_log)

        # 3. SAFETY CHECKS
        if not victim: return 
        if k_id == v_id or w_id in [97, 100]: # Suicide or World/falling
            victim.streak = 0
            return

        # 4. TEAM KILL CHECK (Logic separation)
        is_teamkill = False
        if killer and self.current_server_mode != 3: # Mode 3 is Duel (No TK)
            k_team = getattr(killer, 'team', -1)
            v_team = getattr(victim, 'team', -2)
            if k_team == v_team and k_team != 0 and k_team != -1:
                is_teamkill = True

        if is_teamkill:
            tk_penalty = 500
            killer.xp = max(0, killer.xp - tk_penalty)
            killer.credits = max(0, killer.credits - 1000)
            killer.streak = 0
            self.send_rcon(f'say "^1TRAITOR: ^7{killer.name} killed a teammate! Lost ^1{tk_penalty} XP^7!"')
            self.save_player_stat(killer)
            return

        # 5. VICTIM LOGIC (XP Loss)
        old_lvl_v = victim.level
        loss = int(self.settings.get('xp_loss', 10))
        if victim.xp >= loss:
            victim.xp -= loss
            loss_str = f"^1(-{loss} XP)"
        else:
            victim.xp = 0
            loss_str = "^5[Last Stand Protection]"
        
        victim.deaths += 1
        victim.streak = 0

        # 6. KILLER LOGIC (Rewards)
        if killer and k_id != 1022:
            old_lvl_k = killer.level
            xp_gain = int(self.settings.get('xp_per_kill', 50))
            cred_gain = int(self.settings.get('passive_credit_gain', 10))
            bonus_str = ""

            # --- Random Events ---
            mult = 3 if random.random() < 0.05 else 1
            if mult > 1: 
                self.send_rcon(f'say "^3FORCE SURGE: ^7{killer.name} tapped into the Force for ^23x XP^7!"')
            
            # --- Revenge ---
            if killer.name in victim.nemesis_map and victim.nemesis_map[killer.name] >= 3:
                revenge_bonus = 200
                killer.credits += revenge_bonus
                victim.nemesis_map[killer.name] = 0
                bonus_str += f" ^5[REVENGE +{revenge_bonus}cr]"

            # --- Theft ---
            if victim.credits > 5000:
                stolen = int(victim.credits * 0.05)
                victim.credits -= stolen
                killer.credits += stolen
                bonus_str += f" ^1[STOLE {stolen}cr]"

            # --- PROGRESSIVE BANK HEIST ---
            # 1. Every kill adds a small "tax" to the House Vault
            self.dealer_credits += 5 

            # 2. Roll for the Heist (1% chance)
            if random.random() < 0.01 and self.dealer_credits > 100:
                # Calculate payout (20% of current vault)
                heist = int(self.dealer_credits * 0.20)
                
                # Check for "MEGA JACKPOT" (If vault is huge, take 50% instead!)
                if self.dealer_credits > 5000:
                    heist = int(self.dealer_credits * 0.50)
                    self.send_rcon(f'say "^1MEGA HEIST: ^7{killer.name} cleaned out the Vault for ^2{heist}cr^7!"')
                else:
                    self.send_rcon(f'say "^3HEIST: ^7{killer.name} cracked the House Vault for ^2{heist}cr^7!"')

                self.dealer_credits -= heist
                killer.credits += heist    

            # --- Stats Update ---
            killer.kills += 1
            killer.streak += 1
            killer.xp += (xp_gain * mult)
            
            # --- Nemesis Tracking ---
            killer.nemesis_map[victim.name] = killer.nemesis_map.get(victim.name, 0) + 1
            if killer.nemesis_map[victim.name] == 3:
                self.send_rcon(f'say "^1NEMESIS: ^7{killer.name} is dominating {victim.name}!"')

            # --- Payouts (Bounties/Bets) ---
            b_reward = 0
            if hasattr(victim, 'bounty') and isinstance(victim.bounty, dict):
                b_reward = sum(victim.bounty.values())
                victim.bounty = {}

            bet_reward = 0
            if killer.id in self.active_bets:
                bet_data = self.active_bets.pop(killer.id)
                bet_reward = (sum(bet_data.values()) if isinstance(bet_data, dict) else int(bet_data)) * 2

            killer.credits += (cred_gain + b_reward + bet_reward)

            # --- Final Announcement ---
            payout_val = b_reward + bet_reward
            payout_str = f" & secured ^3{payout_val}cr^7" if payout_val > 0 else ""
            k_title = killer.get_title(self.current_server_mode)
            v_title = victim.get_title(self.current_server_mode)
            
            self.send_rcon(f'say "{k_title} ^2{killer.name} ^7defeated {v_title} ^1{victim.name} ^3(+{xp_gain * mult} XP){payout_str} {loss_str}{bonus_str}"')
            
            # Final Save & Check
            self.check_rank_change(killer, old_lvl_k)
            self.save_player_stat(killer)

        # Always save the victim (for death count/xp loss/theft)
        self.save_player_stat(victim)

    def play_pazaak(self, p, amount):
        if p.credits < amount:
            self.send_rcon(f'svtell {p.id} "^1Error: You need more credits!"')
            return
        if amount <= 0: return

        p.credits -= amount
        # Add a portion of the bet to the dealer's bonus pot immediately
        self.dealer_credits += int(amount * 0.1) 
        
        card = random.randint(1, 10)
        self.active_pazaak[p.name] = {"score": card, "bet": amount}
        
        self.send_rcon(f'svtell {p.id} "^5[PAZAAK] ^7Bet: ^3{amount}cr ^7| Dealer Bonus: ^2{self.dealer_credits}cr"')
        self.send_rcon(f'svtell {p.id} "^7Your Hand: ^2{card} ^7| !hit or !stand?"')
        self.save_player_stat(p)

    def handle_chat(self, sid, name, msg):
        clean_log_name = normalize(name)
        msg = msg.lower().strip()
        
        if not msg.startswith("!"):
            return

        # Try to find the player in memory
        # We check if the name matches OR the SID matches
        p = next((x for x in self.players if normalize(x.name) == clean_log_name or x.id == sid), None)
        
        if not p:
            # If not found, the memory is out of sync. Force a refresh.
            print(f"[!] Player {clean_log_name} not in memory. Syncing...")
            self.sync_current_players()
            # Try finding again after sync
            p = next((x for x in self.players if normalize(x.name) == clean_log_name or x.id == sid), None)

        if not p:
            print(f"[!] Still could not resolve '{clean_log_name}'. Check RCON 'status' output format.")
            return

        # Now that we have 'p', use the ID from the server status, not the log
        target_sid = p.id
        # print(f"[#] Executing {msg} for {p.name} on SID {p.id}")   
            
        msg = msg.lower().strip()

        if msg == "!title" or msg.startswith("!title "):
            parts = msg.split(" ", 1)
            
            # Dynamically set the help lists based on the current mode
            if self.current_server_mode == 3:
                hero_list = "jedi"
                villain_list = "sith"
                mode_note = "^1(^7Duel Mode Active: ^5Jedi^1/^1Sith)"
            else:
                hero_list = "rebel, elite, clone, arc, hero, wookiee, jedi"
                villain_list = "imperial, commander, bh, mando, deka, sbd, sith"
                mode_note = "^2(All Modes)"

            # Usage check
            if len(parts) < 2 or parts[1].strip() == "":
                # Notice the 'f' before the quote!
                self.send_rcon(f'svtell {p.id} "^3Usage: !title <career_name> {mode_note}"')
                self.send_rcon(f'svtell {p.id} "^5Hero: ^7{hero_list}"')
                self.send_rcon(f'svtell {p.id} "^1Villain: ^7{villain_list}"')
                return

            choice = parts[1].lower().strip().replace(" ", "")
            
            mapping = {
                "rebel": "rebel", "soldier": "rebel",
                "elite": "elitetrooper", "elitetrooper": "elitetrooper",
                "clone": "clonetrooper", "clonetrooper": "clonetrooper",
                "arc": "arctrooper", "arctrooper": "arctrooper",
                "hero": "hero",
                "wookiee": "wookiee", "wookie": "wookiee",
                "jedi": "jedi",
                "imperial": "imperial", "imp": "imperial",
                "commander": "commander",
                "bountyhunter": "bountyhunter", "bh": "bountyhunter",
                "mandalorian": "mandalorian", "mando": "mandalorian",
                "droideka": "droideka", "deka": "droideka",
                "sbd": "sbd", "superbattledroid": "sbd",
                "sith": "sith"
            }
            
            if choice in mapping:
                target_faction = mapping[choice]
                if self.current_server_mode == 3 and target_faction not in ["jedi", "sith"]:
                    self.send_rcon(f'svtell {p.id} "^1Error: ^7The career ^3{choice} ^7is not available in Duel Mode!"')
                    return 

                p.faction = target_faction
                self.save_player_stat(p)
                title_display = p.get_title(self.current_server_mode)
                self.send_rcon(f'say "^7{p.name} ^7has chosen the career: {title_display}^7!"')
            else:
                self.send_rcon(f'svtell {p.id} "^1Error: ^7Career \'{choice}\' not found."')
                self.send_rcon(f'svtell {p.id} "^5Hero: ^7{hero_list}"')
                self.send_rcon(f'svtell {p.id} "^1Villain: ^7{villain_list}"')

        elif msg == "!help" or msg == "!commands":        
            self.send_rcon(f'svtell {p.id} "^5--- CHAOS COMMANDS ---"')
            self.send_rcon(f'svtell {p.id} "^3Personal: ^7!rank, !stats, !bank, !title !level"')
            self.send_rcon(f'svtell {p.id} "^3Economy: ^7!pay <name> <amt>, !wealth, !top" !vault !house')
            self.send_rcon(f'svtell {p.id} "^3Gambling: ^7!pazaak <amt>, !bet <name> <amt>, !bounty <name> <amt>"')
            self.send_rcon(f'svtell {p.id} "^2Pazaak Info: ^7Hit 20 for 3x Payout!"')
        # Check for the command without a space first, or the command with a space
        elif msg == "!pazaak" or msg.startswith("!pazaak "):
            parts = msg.split()
            if len(parts) < 2:
                # Yellow usage text
                self.send_rcon(f'svtell {p.id} "^3Usage: !pazaak <amount>"')
            else:
                try:
                    amt = int(parts[1])
                    self.play_pazaak(p, amt)
                except ValueError:
                    self.send_rcon(f'svtell {p.id} "^1Error: Amount must be a number."')
        elif msg == "!hit" and p.name in self.active_pazaak:
            game = self.active_pazaak[p.name]
            card = random.randint(1, 10)
            game["score"] += card
            
            if game["score"] == 20:
                win = game["bet"] * 3
                p.credits += win
                # High visibility Magenta and Green for the big win
                self.send_rcon(f'say "^6PAZAAK! ^5{p.name} ^7hit ^220 ^7and wins ^3{win}cr ^2(3x Payout)!"')
                del self.active_pazaak[p.name]
            elif game["score"] > 20:
                self.send_rcon(f'say "^7{p.name} ^1BUSTED ^7with ^1{game["score"]}!. ^7Dealer Pot is now ^3{self.dealer_credits}^3cr^7."')
                del self.active_pazaak[p.name]
            else:
                self.send_rcon(f'svtell {p.id} "^5[PAZAAK] ^7{p.name} ^7draws {card}. ^7Total: ^2{game["score"]}"')
            self.save_player_stat(p)
        elif msg == "!stand" and p.name in self.active_pazaak:
            game = self.active_pazaak[p.name]
            diff = int(self.settings.get('pazaak_difficulty', 17))
            dealer_hand = random.randint(diff, 20)
            
            self.send_rcon(f'say "^5[PAZAAK] ^7{p.name}(^2{game["score"]}^7) vs Dealer(^1{dealer_hand}^7)"')
            
            if game["score"] > dealer_hand:
                # Player Wins: Double bet + Dealer's accumulated pool
                bonus = self.dealer_credits
                win = (game["bet"] * 2) + bonus
                p.credits += win
                self.send_rcon(f'say "^2WIN! ^7{p.name} beat the house and took the ^3{bonus}cr ^7bonus pot! Total: ^3{win}cr^7!"')
                self.dealer_credits = 0 # Reset the pot after a win
            elif game["score"] == dealer_hand:
                p.credits += game["bet"]
                self.send_rcon(f'say "^3PUSH! ^7Scores tied at {dealer_hand}. Bet returned."')
            else:
                # Player Loses: Their bet stays with the dealer, increasing the next winner's payout
                self.dealer_credits += game["bet"]
                self.send_rcon(f'say "^1LOSS! ^7The House wins. Dealer Pot is now ^3{self.dealer_credits}cr^7."')
            
            del self.active_pazaak[p.name]
            self.save_player_stat(p)     
        elif msg == "!rank": 
            display_title = p.get_title(self.current_server_mode)
            self.send_rcon(f'svtell {p.id} "^7{p.name}: {display_title} ^7| Lvl: ^2{p.level} ^7| XP: ^2{p.xp}"')
        elif msg == "!stats": 
            self.send_rcon(f'svtell {p.id} "^7STATS: {p.name} ^2Kills: {p.kills} ^1Deaths: {p.deaths}"')
        elif msg == "!wealth":
            with sqlite3.connect(self.db_filename, timeout=20) as conn:
                cursor = conn.cursor()
                # Fetch the top 5 directly from the database
                cursor.execute("SELECT name, credits FROM players ORDER BY credits DESC LIMIT 5")
                rows = cursor.fetchall()
                txt = "^3Wealthy 5: " + " ".join([f"^5{r[0]}(^3{r[1]}cr^7)" for r in rows])
                self.send_rcon(f'say "{txt}"')
        elif msg == "!bank" or msg == "!wallet" or msg == "!credits":
            # Sum up the total value of all bounty contributions
            total_bounty = sum(p.bounty.values()) if isinstance(p.bounty, dict) else 0
            b_msg = f" ^1(Bounty: {total_bounty})" if total_bounty > 0 else ""
            self.send_rcon(f'svtell {p.id} "^5[BANK] ^2{p.name}^7, you have ^3{p.credits} Credits^7.{b_msg}"')
        elif msg == "!bounties":
            active_bounties = [pl for pl in self.players if isinstance(pl.bounty, dict) and sum(pl.bounty.values()) > 0]
        
            if not active_bounties:
                self.send_rcon(f'say "^5[BANK] ^7There are currently no active ^1BOUNTIES^7."')
            else:
                # Display the sum of contributions for each player
                txt = "^1Active Bounties: " + " ".join([f"^5{pl.name}(^1{sum(pl.bounty.values())}^7)" for pl in active_bounties])
                self.send_rcon(f'say "{txt}"')       
        elif msg.startswith("!bounty"):
            parts = msg.split(" ")
            
            if len(parts) == 2 and parts[1] == "cancel":

                found_bounty = False
                for target in self.players:
                    if isinstance(target.bounty, dict) and p.name in target.bounty:
                        refund = target.bounty.pop(p.name)
                        p.credits += refund
                        self.send_rcon(f'say "^5[BANK] ^7{p.name} cancelled their bounty on {target.name}. ^2{refund}cr ^7refunded."')
                        found_bounty = True
                        self.save_player_stat(p)
                        break 
                
                if not found_bounty:
                    self.send_rcon(f'svtell {p.id} "^1Error: ^7You do not have any active bounties to cancel."')
                return

            try:
                if len(parts) < 3:
                    self.send_rcon(f'svtell {p.id} "^3Usage: !bounty <name> <amount> ^7OR ^3!bounty cancel"')
                    return

                target_name = parts[1].lower()
                amount = int(parts[2])
                target = next((x for x in self.players if target_name in x.name.lower()), None)

                if target and p.credits >= amount and amount > 0:
                    if not isinstance(target.bounty, dict): target.bounty = {}
                    
                    p.credits -= amount
                    # Add to existing contribution or start a new one
                    target.bounty[p.name] = target.bounty.get(p.name, 0) + amount
                    
                    total = sum(target.bounty.values())
                    self.send_rcon(f'say "^1WAGER: ^7{p.name} put a ^3{amount}cr ^7bounty on {target.name}! Total: ^1{total}cr^7!"')
                    self.save_player_stat(p)
                elif not target:
                    self.send_rcon(f'svtell {p.id} "^1Error: ^7Player \'{parts[1]}\' not found."')
            except ValueError:
                self.send_rcon(f'svtell {p.id} "^1Error: ^7Amount must be a number."')
        elif msg.startswith("!bet"):
            try:
                parts = msg.split(" ")
                if len(parts) < 3:
                    self.send_rcon(f'svtell {p.id} "^7Usage: !bet <name> <amount>"')
                    return
                
                target_name = parts[1].lower()
                amt = int(parts[2])
                target = next((x for x in self.players if target_name in x.name.lower()), None)

                if not target:
                    self.send_rcon(f'svtell {p.id} "^1Error: ^7Player \'{parts[1]}\' not found."')
                    return

                if p.credits >= amt and amt > 0:
                    p.credits -= amt
                    
                    # Track bets using a nested dictionary: {target_id: {player_name: amount}}
                    if target.id not in self.active_bets:
                        self.active_bets[target.id] = {}
                    
                    # Store the original bet amount (we calculate the 2x payout later)
                    self.active_bets[target.id][p.name] = self.active_bets[target.id].get(p.name, 0) + amt
                    
                    self.send_rcon(f'say "^2BET: ^5{p.name} ^7bet ^3{amt}cr ^7on ^5{target.name}^7!"')
                    self.save_player_stat(p)
                else:
                    self.send_rcon(f'svtell {p.id} "^1Error: ^7Insufficient credits."')
            except ValueError:
                self.send_rcon(f'svtell {p.id} "^1Error: ^7Amount must be a number."')
        elif msg.startswith("!pay"):
            try:
                parts = msg.split(" ")
                if len(parts) < 3:
                    self.send_rcon(f'svtell {p.id} "^7Usage: !pay <name> <amount>"')
                    return
                
                target_name = parts[1].lower()
                amount = int(parts[2])

                # Find the target player in the current server list
                target = next((x for x in self.players if target_name in x.name.lower()), None)

                if not target:
                    self.send_rcon(f'svtell {p.id} "^1Error: ^7Player \'{parts[1]}\' not found."')
                    return
                
                if target == p:
                    self.send_rcon(f'svtell {p.id} "^1Error: ^7You cannot pay yourself!"')
                    return

                if p.credits >= amount and amount > 0:
                    p.credits -= amount
                    target.credits += amount
                    self.send_rcon(f'say "^2TRANSFER: ^7{p.name} sent ^3{amount} Credits ^7to {target.name}!"')
                    self.save_player_stat(p)
                else:
                    self.send_rcon(f'svtell {p.id} "^1Error: ^7Insufficient credits."')
            except:
                self.send_rcon(f'svtell {p.id} "^7Usage: !pay <name> <amount>"')  
        elif msg == "!top":
            with sqlite3.connect(self.db_filename, timeout=20) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name, xp FROM players ORDER BY xp DESC LIMIT 5")
                rows = cursor.fetchall()

            xpl = int(self.settings.get('xp_per_level', 1000))
            txt = "^5Top 5: " + " ".join([f"^7{r[0]}(^2Lvl {(r[1]//xpl)+1}^7)" for r in rows])
            self.send_rcon(f'say "{txt}"')
        elif msg == "!level":
            title = p.get_title(self.current_server_mode)
            progress = p.get_progress_bar()
            self.send_rcon(f'svtell {p.id} "{title} ^7{p.name} ^7- Lvl ^2{p.level} ^7| {progress}"')
        elif msg == "!vault" or msg == "!house":
            # Show the current progressive jackpot
            self.send_rcon(f'svtell {p.id} "^5[HOUSE] ^7Current Vault: ^3{self.dealer_credits} Credits ^7(1 percent chance to heist on kill)"')                  

    def run(self):
        log = self.settings['logname']
        print(f"[*] Chaos Plugin Active. Monitoring: {log}")
        
        # Initial sync on startup
        self.sync_current_players()
        # Timer initialization
        self.last_sync_time = time.time() 

        startup_resp = str(self.send_rcon("g_authenticity", True)).lower()
        if '="3"' in startup_resp.replace("^7", "").replace("^9", "").replace(" ", ""):
            self.current_server_mode = 3
        else:
            self.current_server_mode = 0

        last_sz = os.path.getsize(log) if os.path.exists(log) else 0
        while True:
            # --- ALWAYS SYNCED LOGIC (TIMER) ---
            # Every 60 seconds, refresh the player list to clean out 
            # players who disconnected without the log noticing.
            if time.time() - self.last_sync_time > 60:
                self.sync_current_players()
                self.last_sync_time = time.time()

            if not os.path.exists(log):
                time.sleep(1); continue
            curr_sz = os.path.getsize(log)
            if curr_sz < last_sz: last_sz = 0
            if curr_sz > last_sz:
                # 'newline=None' handles both Windows \r\n and Linux \n automatically
                with open(log, 'r', encoding='utf-8', errors='ignore', newline=None) as f:
                    f.seek(last_sz)
                    for line in f:
                        line = line.strip() # Remove hidden \r or trailing spaces
                        if not line: continue
                        # Keep your existing InitGame logic as a backup for map changes
                        if "InitGame:" in line: 
                            self.players = [] 
                            
                            # Re-detect game mode (Duel vs Open)
                            line_low = line.lower()
                            if "g_authenticity\\3" in line_low.replace(" ", ""):
                                self.current_server_mode = 3
                            else:
                                self.current_server_mode = 0
                                
                            # Re-scan the server immediately to get new SIDs
                            time.sleep(2) # Wait a moment for server to stabilize
                            self.sync_current_players()
                            self.last_sync_time = time.time()
                            continue
                        if "ClientUserinfoChanged:" in line:
                            m = re.search(r'ClientUserinfoChanged:\s*(\d+)\s*n\\([^\\]+)', line)
                            if m:
                                sid, name = int(m.group(1)), m.group(2)
                                # Only keeps the player data synced; no chat announcement sent
                                self.sync_player(sid, name)
                        if "ClientDisconnect:" in line or "entered the game" in line:
                            m = re.search(r'(ClientDisconnect:|entered the game:)\s*(\d+)', line)
                            if m:
                                t_sid = int(m.group(2))
                                t_p = next((x for x in self.players if x.id == t_sid), None)
                                
                                if t_p:
                                    # Refund Bounties
                                    if isinstance(t_p.bounty, dict):
                                        for name, amt in t_p.bounty.items():
                                            contributor = next((x for x in self.players if x.name == name), None)
                                            if contributor:
                                                contributor.credits += amt
                                                self.save_player_stat(contributor) # Save the person getting the money back
                                        t_p.bounty = {}

                                    # Refund Bets
                                    if t_sid in self.active_bets:
                                        bet_dict = self.active_bets.pop(t_sid)
                                        for name, amt in bet_dict.items():
                                            contributor = next((x for x in self.players if x.name == name), None)
                                            if contributor:
                                                contributor.credits += amt
                                                self.save_player_stat(contributor) # Save the person getting the money back
                                        
                                    self.send_rcon(f'say "^5[BANK] ^7Bets/Bounties on ^5{t_p.name} ^7refunded (Left/Spec)."')
                                    self.save_player_stat(t_p)        
                        elif "Kill: " in line:
                            m = re.search(r'Kill:\s*(\d+)\s+(\d+)\s+(\d+):', line)
                            if m:
                                self.process_kill(m.group(1), m.group(2), m.group(3), line)
                        # Inside your run() loop
                        elif "say:" in line:
                            # 1. Correctly extract the real SID (the number right before 'say:')
                            # In "1265:44 2: say:", this matches the '2'
                            sid_match = re.search(r'(\d+):\s+say:', line)
                            log_sid = int(sid_match.group(1)) if sid_match else -1
                            
                            # 2. Extract Name and Message
                            m_chat = re.search(r'say:\s+(?:\^0\[\^7)?(.*?)(?:\^0\])?:\s*"(.*)"', line)
                            
                            if m_chat:
                                name_raw = m_chat.group(1).strip()
                                message = m_chat.group(2).strip()
                                
                                # Pass the REAL log_sid (2) to handle_chat
                                self.handle_chat(log_sid, name_raw, message)

                        # Updated detection for Private Messages (tell)
                        elif "tell:" in line:
                            # Skips timestamp and captures Sender to Receiver: "Message"
                            m_tell = re.search(r'tell:\s+(?:\^0\[\^7)?(.*?)(?:\^0\])? to .*?:\s*"(.*)"', line)
                            
                            if m_tell:
                                name_raw = m_tell.group(1).strip()
                                message = m_tell.group(2).strip()
                                name_clean = normalize(name_raw)
                                
                                p = next((x for x in self.players if normalize(x.name) == name_clean), None)
                                if p:
                                    self.handle_chat(p.id, name_raw, message)
                        
                last_sz = curr_sz
            time.sleep(0.2)

if __name__ == "__main__":
    MBIIChaosPlugin().run()