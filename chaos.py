import os
import time
import re
import json
import socket
import sys
import random
import configparser

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
        self.bounty = 0                      
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
            # Calculate XP within the current level
            xp_into_level = self.xp % self.xp_per_lvl
            percentage = (xp_into_level / self.xp_per_lvl)
            
            # Create a 10-segment bar: I for filled, . for empty
            filled = int(percentage * 10)
            bar = "^2" + "I" * filled + "^7" + "." * (10 - filled)
            
            xp_left = self.xp_per_lvl - xp_into_level
            return f"[{bar}^7] {int(percentage * 100)}% (^3{xp_left} XP left^7)"        

class MBIIChaosPlugin:
    def __init__(self):
        if len(sys.argv) > 1:
            self.config_file = sys.argv[1]
        else:
            self.config_file = 'chaos.cfg' # Default fallback
        self.settings = {}
        self.db_filename = 'players.json'
        self.load_config()
        self.players = []
        self.db = ()
        self.current_server_mode = 0
        self.active_bets = {}
        self.active_pazaak = {} # NEW: Tracks active card games
        self.load_db()

    def load_config(self):
        config = configparser.ConfigParser()
        # Find the actual directory of chaos.py
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, self.config_file)
        
        if not os.path.exists(config_path): 
            sys.exit(f"Error: {config_path} not found.")
        
        config.read(config_path)
        self.settings = dict(config['SETTINGS'])
        
        # Ensure the JSON file path is absolute for Linux permissions
        fname = self.settings.get('db_file', 'players.json')
        self.db_filename = os.path.join(base_dir, fname)
        
    def load_db(self):
        if os.path.exists(self.db_filename):
            try:
                with open(self.db_filename, "r") as f:
                    data = json.load(f)
                    # Force conversion to list to ensure .append() works
                    self.db = list(data) if data else []
                    print(f"[*] Loaded {len(self.db)} players from database.")
            except Exception as e:
                print(f"[!] Error loading DB: {e}")
                self.db = []
        else:
            self.db = []

    def save_db(self):
        # 1. Start with the existing list in memory
        # If self.db isn't a list yet, force it to be one
        if not isinstance(self.db, list):
            self.db = list(self.db) if self.db else []

        # 2. Update self.db with current session data
        for p in self.players:
            # Skip invalid entries (IPs or blanks)
            if not p.name or "." in p.name or ":" in p.name:
                continue

            found = False
            for entry in self.db:
                if entry["name"] == p.name:
                    entry.update({
                        "xp": p.xp, "credits": p.credits, 
                        "kills": p.kills, "deaths": p.deaths, "faction": p.faction
                    })
                    found = True
                    break
            
            if not found:
                self.db.append({
                    "name": p.name, "xp": p.xp, "credits": p.credits,
                    "kills": p.kills, "deaths": p.deaths, "faction": p.faction
                })

        # 3. Secure Write for Linux
        try:
            with open(self.db_filename, "w") as f:
                json.dump(self.db, f, indent=4)
                f.flush()
                os.fsync(f.fileno()) # Forces the OS to write to disk
            return True
        except Exception as e:
            print(f"[!] Linux Save Error: {e}")
            return False

    def sync_player(self, sid, name): 
        if not name or "." in name or ":" in name:
            return None

        p = next((x for x in self.players if x.id == sid), None)
        if p:
            return p

        db_e = next((item for item in self.db if item["name"] == name), None)
        
        p = Player(sid, name,
                   xp=db_e.get("xp", 0) if db_e else 0,
                   credits=db_e.get("credits", int(self.settings.get('starting_credits', 0))) if db_e else int(self.settings.get('starting_credits', 0)), 
                   kills=db_e.get("kills", 0) if db_e else 0, 
                   deaths=db_e.get("deaths", 0) if db_e else 0,
                   faction=db_e.get("faction", "jedi") if db_e else "jedi",
                   config=self.settings)
        
        self.players.append(p)

        if not db_e:
            self.db.append({
                "name": name, "xp": p.xp, "credits": p.credits,
                "kills": p.kills, "deaths": p.deaths, "faction": p.faction
            })
        
        # Move this OUTSIDE the 'if not db_e' block so it saves 
        # whenever a player is synced or updated
        self.save_db() 
            
        return p

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
        if not response: return
        
        lines = response.split('\n')
        for line in lines:
            m = re.search(r'^\s*(\d+)\s+', line)
            if m:
                sid = int(m.group(1))
                # Split the line by spaces to handle Linux column formatting 
                parts = line.split()
                
                # Ensure there are enough segments to contain a name 
                if len(parts) > 4:
                    name_parts = []
                    for p in parts[3:]:
                        # Stop collecting name parts when we hit the IP:Port column 
                        if ":" in p and "." in p: break 
                        name_parts.append(p)
                    
                    # Rebuild the name and strip color codes 
                    name_raw = " ".join(name_parts)
                    name_final = re.sub(r'\^\d', '', name_raw).strip()
                    
                    if name_final:
                        # Link the Slot ID to the player object in memory 
                        self.sync_player(sid, name_final)

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

        # 1. UNIVERSAL SYNC: Capture names for ANY weapon/MOD in Open or FA
        # This regex grabs everything between 'Kill:' and 'killed', and 'killed' and 'by'
        m = re.search(r'Kill:\s*\d+\s+\d+\s+\d+:\s*(.*?)\s+killed\s+(.*?)\s+by', raw_line)
        k_name_log = m.group(1).strip() if m else None
        v_name_log = m.group(2).strip() if m else None

        if k_name_log and ("." in k_name_log or ":" in k_name_log):
            p_k = next((x for x in self.players if x.id == k_id), None)
            k_name_log = p_k.name if p_k else k_name_log

        if v_name_log and ("." in v_name_log or ":" in v_name_log):
            p_v = next((x for x in self.players if x.id == v_id), None)
            v_name_log = p_v.name if p_v else v_name_log

        # Instantly register players found in the log line if they aren't in our list
        killer = self.sync_player(k_id, k_name_log) if k_name_log and k_id != 1022 else next((x for x in self.players if x.id == k_id), None)
        victim = self.sync_player(v_id, v_name_log) if v_name_log else next((x for x in self.players if x.id == v_id), None)

        if victim:
            # Ignore Spectator, Team Swaps, and Suicides (Identified by matching IDs or specific MODs)
            if k_id == v_id or w_id in [97, 100]: return

            old_lvl_v = victim.level
            loss = int(self.settings['xp_loss'])
            
            # Last Stand Protection
            if victim.xp >= loss:
                victim.xp -= loss
                loss_str = f"^1(-{loss} XP)"
            else:
                victim.xp = 0
                loss_str = "^5(Last Stand Protected)"
            
            victim.deaths += 1
            victim.streak = 0
            self.check_rank_change(victim, old_lvl_v)

            # 2. AGNOSTIC KILL LOGIC: Rewardable player kill
            if k_id != 1022 and killer and killer.id != victim.id:
                old_lvl_k = killer.level
                xp_gain = int(self.settings['xp_per_kill'])
                cred_gain = int(self.settings.get('passive_credit_gain', 10))
                
                # Force Surge (5% chance for 3x XP)
                mult = 3 if random.random() < 0.05 else 1
                if mult > 1: self.send_rcon(f'say "^3FORCE SURGE: ^7{killer.name} tapped into the Force for ^23x XP^7!"')
                
                killer.xp += (xp_gain * mult)
                
                # --- Payout Logic ---
                b_reward = victim.bounty
                bet_reward = self.active_bets.pop(killer.id, 0) # Killer wins their bet pot
                self.active_bets.pop(victim.id, None)          # Victim loses their bet pot
                
                killer.credits += (cred_gain + b_reward + bet_reward)
                victim.bounty = 0  # Bounty is collected

                killer.kills += 1; killer.streak += 1
                
                # Nemesis System
                killer.nemesis_map[victim.name] = killer.nemesis_map.get(victim.name, 0) + 1
                if killer.nemesis_map[victim.name] == 3:
                    self.send_rcon(f'say "^1NEMESIS: ^7{killer.name} is dominating {victim.name}!"')

                payout_str = ""
                if b_reward > 0 and bet_reward > 0:
                    payout_str = f" & secured ^3{b_reward}cr Bounty ^7+ ^2{bet_reward}cr Bet Payout^7"
                elif b_reward > 0:
                    payout_str = f" & collected a ^3{b_reward}cr Bounty^7"
                elif bet_reward > 0:
                    payout_str = f" & pocketed ^2{bet_reward}cr in Winnings^7"

                k_title = killer.get_title(self.current_server_mode)
                v_title = victim.get_title(self.current_server_mode)

                self.send_rcon(f'say "{k_title} ^2{killer.name} ^7defeated {v_title} ^1{victim.name} ^3(+{xp_gain * mult} XP){payout_str} {loss_str}"')
                self.check_rank_change(killer, old_lvl_k)

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
        self.save_db()

    def handle_chat(self, sid, name, msg):
        clean_name = re.sub(r'\^\d', '', name).strip().lower()
        
        # 1. Try to find the player
        p = next((x for x in self.players if (sid != -1 and x.id == sid) or 
                  (clean_name in x.name.lower()) or 
                  (x.name.lower() in clean_name)), None)
        
        # 2. Re-sync if not found
        if not p:
            # print(f"[*] Name '{clean_name}' not in memory. Re-syncing status...")
            self.sync_current_players()
            p = next((x for x in self.players if (sid != -1 and x.id == sid) or 
                      (clean_name in x.name.lower())), None)

        # 3. THE FIX: If player is STILL not found, stop here!
        if p:
            target_sid = p.id
        else:
            # print(f"[!] Could not resolve target_sid for {clean_name}. Ignoring command.")
            return  # This prevents the UnboundLocalError
            
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
                self.send_rcon(f'svtell {target_sid} "^3Usage: !title <career_name> {mode_note}"')
                self.send_rcon(f'svtell {target_sid} "^5Hero: ^7{hero_list}"')
                self.send_rcon(f'svtell {target_sid} "^1Villain: ^7{villain_list}"')
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
                    self.send_rcon(f'svtell {target_sid} "^1Error: ^7The career ^3{choice} ^7is not available in Duel Mode!"')
                    return 

                p.faction = target_faction
                self.save_db()
                title_display = p.get_title(self.current_server_mode)
                self.send_rcon(f'say "^7{p.name} has chosen the career: {title_display}^7!"')
            else:
                self.send_rcon(f'svtell {target_sid} "^1Error: ^7Career \'{choice}\' not found."')
                self.send_rcon(f'svtell {target_sid} "^5Hero: ^7{hero_list}"')
                self.send_rcon(f'svtell {target_sid} "^1Villain: ^7{villain_list}"')

        elif msg == "!help" or msg == "!commands":        
            self.send_rcon(f'svtell {target_sid} "^5--- CHAOS COMMANDS ---"')
            self.send_rcon(f'svtell {target_sid} "^3Personal: ^7!rank, !stats, !bank, !title !level"')
            self.send_rcon(f'svtell {target_sid} "^3Economy: ^7!pay <name> <amt>, !wealth, !top"')
            self.send_rcon(f'svtell {target_sid} "^3Gambling: ^7!pazaak <amt>, !bet <name> <amt>, !bounty <name> <amt>"')
            self.send_rcon(f'svtell {target_sid} "^2Pazaak Info: ^7Hit 20 for 3x Payout!"')
        # Check for the command without a space first, or the command with a space
        elif msg == "!pazaak" or msg.startswith("!pazaak "):
            parts = msg.split()
            if len(parts) < 2:
                # Yellow usage text
                self.send_rcon(f'svtell {target_sid} "^3Usage: !pazaak <amount>"')
            else:
                try:
                    amt = int(parts[1])
                    self.play_pazaak(p, amt)
                except ValueError:
                    self.send_rcon(f'svtell {target_sid} "^1Error: Amount must be a number."')
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
                self.send_rcon(f'say "^7{p.name} ^1BUSTED ^7with ^1{game["score"]}!"')
                del self.active_pazaak[p.name]
            else:
                self.send_rcon(f'say "^5[PAZAAK] ^7{p.name} ^7draws {card}. ^7Total: ^2{game["score"]}"')
            self.save_db()
        elif msg == "!stand" and p.name in self.active_pazaak:
            game = self.active_pazaak[p.name]
            diff = int(self.settings.get('pazaak_difficulty', 17))
            dealer_hand = random.randint(diff, 20)
            
            self.send_rcon(f'svtell {target_sid} "^5[PAZAAK] ^7{p.name}(^2{game["score"]}^7) vs Dealer(^1{dealer_hand}^7)"')
            
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
            self.save_db()     
        elif msg == "!rank": 
            display_title = p.get_title(self.current_server_mode)
            self.send_rcon(f'svtell {target_sid} "^7{p.name}: {display_title} ^7| Lvl: ^2{p.level} ^7| XP: ^2{p.xp}"')
        elif msg == "!stats": 
            self.send_rcon(f'svtell {target_sid} "^7STATS: {p.name} ^2Kills: {p.kills} ^1Deaths: {p.deaths}"')
        elif msg == "!wealth":
            # Keep wealth as the Top 5 leaderboard
            sorted_wealth = sorted(self.db, key=lambda x: x.get('credits', 0), reverse=True)
            txt = "^3Wealthy 5: " + " ".join([f"^2{i+1}.^5{x['name']}(^3{x.get('credits',0)}cr^2)" for i,x in enumerate(sorted_wealth[:5])])
            self.send_rcon(f'say "{txt}"')
        elif msg == "!bank" or msg == "!wallet" or msg == "!credits":
            b_msg = f" ^1(Bounty: {p.bounty})" if p.bounty > 0 else ""
            self.send_rcon(f'svtell {target_sid} "^5[BANK] ^2{p.name}^7, you have ^3{p.credits} Credits^7.{b_msg}"')
        elif msg == "!bounties":
            active_bounties = [p for p in self.players if p.bounty > 0]
            if not active_bounties:
                self.send_rcon(f'say "^5[BANK] ^7There are currently no active ^1BOUNTIES^7."')
            else:
                txt = "^1Active Bounties: " + " ".join([f"^5{p.name}(^1{p.bounty}^7)" for p in active_bounties])
                self.send_rcon(f'say "{txt}"')       
        elif msg.startswith("!bounty"):
            try:
                parts = msg.split(" ")
                if len(parts) < 3:
                    self.send_rcon(f'svtell {target_sid} "^7Usage: !bounty <name> <amount>"')
                    return
                target = next((x for x in self.players if parts[1].lower() in x.name.lower()), None)
                amount = int(parts[2])
                if target and p.credits >= amount and amount > 0:
                    p.credits -= amount
                    target.bounty += amount
                    self.send_rcon(f'say "^1WAGER: ^7{p.name} put a ^3{amount} Credit ^7bounty on {target.name}!"')
                    self.save_db()
                elif not target:
                    self.send_rcon(f'svtell {target_sid} "^1Error: ^7Player \'{parts[1]}\' not found."')
            except: self.send_rcon(f'svtell {target_sid} "^7Usage: !bounty <name> <amount>"')
        elif msg.startswith("!bet"):
            try:
                parts = msg.split(" ")
                if len(parts) < 3:
                    self.send_rcon(f'svtell {target_sid} "^7Usage: !bet <name> <amount>"')
                    return
                
                target_name = parts[1].lower()
                amt = int(parts[2])

                # Search for target player by name instead of ID
                target = next((x for x in self.players if target_name in x.name.lower()), None)

                if not target:
                    self.send_rcon(f'svtell {target_sid} "^1Error: ^7Player \'{parts[1]}\' not found."')
                    return

                if p.credits >= amt and amt > 0:
                    p.credits -= amt
                    # We still use target.id internally to track the bet for the Kill processor
                    self.active_bets[target.id] = self.active_bets.get(target.id, 0) + (amt * 2)
                    self.send_rcon(f'say "^2BET: ^5{p.name} ^7bet ^3{amt}cr ^7on ^5{target.name}^7!"')
                    self.save_db()
                else:
                    self.send_rcon(f'svtell {target_sid} "^1Error: ^7Insufficient credits."')
            except: 
                self.send_rcon(f'svtell {target_sid} "^7Usage: !bet <name> <amount>"')
        elif msg.startswith("!pay"):
            try:
                parts = msg.split(" ")
                if len(parts) < 3:
                    self.send_rcon(f'svtell {target_sid} "^7Usage: !pay <name> <amount>"')
                    return
                
                target_name = parts[1].lower()
                amount = int(parts[2])

                # Find the target player in the current server list
                target = next((x for x in self.players if target_name in x.name.lower()), None)

                if not target:
                    self.send_rcon(f'svtell {target_sid} "^1Error: ^7Player \'{parts[1]}\' not found."')
                    return
                
                if target == p:
                    self.send_rcon(f'svtell {target_sid} "^1Error: ^7You cannot pay yourself!"')
                    return

                if p.credits >= amount and amount > 0:
                    p.credits -= amount
                    target.credits += amount
                    self.send_rcon(f'say "^2TRANSFER: ^7{p.name} sent ^3{amount} Credits ^7to {target.name}!"')
                    self.save_db()
                else:
                    self.send_rcon(f'svtell {target_sid} "^1Error: ^7Insufficient credits."')
            except:
                self.send_rcon(f'svtell {target_sid} "^7Usage: !pay <name> <amount>"')  
        elif msg == "!top":
            sorted_db = sorted(self.db, key=lambda x: x.get('xp', 0), reverse=True)
            xpl = int(self.settings['xp_per_level'])
            txt = "^5Top 5: " + " ".join([f"^7{i+1}.{x['name']}(^2Lvl {(x.get('xp',0)//xpl)+1}^7)" for i,x in enumerate(sorted_db[:5])])
            self.send_rcon(f'say "{txt}"')
        elif msg == "!level":
            title = p.get_title(self.current_server_mode)
            progress = p.get_progress_bar()
            
            # ADD THE 'f' HERE:
            self.send_rcon(f'svtell {target_sid} "{title} ^7{p.name} ^7- Lvl ^2{p.level} ^7| {progress}"')              

    def run(self):
        log = self.settings['logname']
        print(f"[*] Chaos Plugin Active. Monitoring: {log}")
        self.sync_current_players()

        startup_resp = str(self.send_rcon("g_authenticity", True)).lower()
        
        # This checks for the value 3 inside the quotes, ignoring color codes
        if '="3"' in startup_resp.replace("^7", "").replace("^9", "").replace(" ", ""):
            self.current_server_mode = 3
        else:
            self.current_server_mode = 0

        last_sz = os.path.getsize(log) if os.path.exists(log) else 0
        while True:
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
                            self.sync_current_players()
                            line_low = line.lower()
                            if "g_authenticity" in line_low:
                                parts = line_low.split("g_authenticity")
                                if len(parts) > 1 and "3" in parts[1][:2]:
                                    self.current_server_mode = 3
                                else:
                                    self.current_server_mode = 0
                            else:
                                self.current_server_mode = 0
                        if "ClientUserinfoChanged:" in line:
                            m = re.search(r'ClientUserinfoChanged:\s*(\d+)\s*n\\([^\\]+)', line)
                            if m:
                                sid, name = int(m.group(1)), m.group(2)
                                # Only keeps the player data synced; no chat announcement sent
                                self.sync_player(sid, name)
                        elif "Kill: " in line:
                            m = re.search(r'Kill:\s*(\d+)\s+(\d+)\s+(\d+):', line)
                            if m:
                                self.process_kill(m.group(1), m.group(2), m.group(3), line)
                        elif " say: " in line:
                            # Matches: 1271:1517: say: ^0[^7Valzhar^0]: "!title test"
                            # This captures the name between [^7 and ^0]
                            m = re.search(r'say:\s*.*?\s*\[\^7(.*?)\^0\]:\s*"(.*)"', line)
                            if m:
                                name_raw = m.group(1).strip()
                                message = m.group(2).strip().replace('"', '')
                                
                                # We pass -1 for SID because we will find the 17 in handle_chat
                                self.handle_chat(-1, name_raw, message)
                        elif "tell:" in line:
                            try:
                                # Try the bracketed version first (JMT style)
                                m = re.search(r'tell:.*?\]\^?\d?(.*?) to .*?: (.*)', line)
                                
                                # Fallback: Try the normal version (Kanan style)
                                if not m:
                                    # Matches: "1286:51tell: ^4Kanan to ^0...: message"
                                    m = re.search(r'tell:\s*\^?\d?(.*?) to .*?: (.*)', line)

                                if m:
                                    name_raw = m.group(1).strip()
                                    name_clean = re.sub(r'\^\d', '', name_raw).strip()
                                    message = m.group(2).strip().replace('"', '')
                                    self.handle_chat(-1, name_clean, message)
                            except Exception as e:
                                print(f"DEBUG ERROR: {e}")
                last_sz = curr_sz
            time.sleep(0.2)

if __name__ == "__main__":
    MBIIChaosPlugin().run()