import os
import time
import re
import json
import socket
import platform
import sys
import random
import configparser
import unicodedata

def normalize(text):
    if not text: return ""
    text = " ".join(text.split()).strip()
    while text.startswith("^7"): text = text[2:].strip()
    while text.endswith("^7"): text = text[:-2].strip()
    return text

def strip_colors(text):
    if not text: return ""
    return re.sub(r'\^.','', text)

# Tier prefixes for extended titles (beyond the first 20 base titles)
# Each prefix spans 10 levels (titles idx 20-29, 30-39, ..., 90-99)
TIER_PREFIXES = ["Veteran ", "Elite ", "Master ", "Grand ", "Prime ",
                 "Transcendent ", "Eternal ", "Mythic "]

# Dark side (villain) factions used for faction bonuses and title coloring
DARK_SIDE_FACTIONS = ["imperial", "commander", "bountyhunter", "mandalorian", "droideka", "sbd", "sith"]


class Player:
    def __init__(self, sid, name, xp=0, kills=0, deaths=0, faction="jedi", credits=0, config=None, guid=""):
        self.id = sid
        self.name = name if name else "New Player"
        self.xp = max(0, xp) 
        self.kills = kills
        self.deaths = deaths
        self.faction = faction.lower()
        self.streak = 0 
        self.credits = max(0, min(9999999, credits)) 
        self.bounty = {}                      
        self.nemesis_map = {} 
        self.xp_per_lvl = int(config.get('xp_per_level', 250))
        self.dealer_credits = 0
        self.side_deck = [random.randint(-5, 5) for _ in range(4)]
        self.is_top5 = False
        self.guid = guid

        self.paths = {
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

        # Core nouns for extended title generation (indices 20-99)
        self.core_nouns = {
            "rebel": ["Rebel", "Soldier", "Scout", "Guardian", "Fighter", "Commando", "Agent", "Operative", "Striker", "Vanguard"],
            "elitetrooper": ["Trooper", "Commando", "Specialist", "Scout", "Gunner", "Sniper", "Operator", "Vanguard", "Pathfinder", "Saboteur"],
            "clonetrooper": ["Clone", "Trooper", "Soldier", "Guardian", "Commando", "Specialist", "Veteran", "Warrior", "Fighter", "Legend"],
            "arctrooper": ["ARC", "Trooper", "Commando", "Specialist", "Scout", "Sniper", "Heavy", "Operator", "Vanguard", "Legend"],
            "hero": ["Hero", "Champion", "Defender", "Guardian", "Protector", "Savior", "Paladin", "Vanguard", "Sentinel", "Paragon"],
            "wookiee": ["Wookiee", "Warrior", "Guardian", "Hunter", "Berserker", "Chieftain", "Defender", "Brawler", "Tracker", "Legend"],
            "imperial": ["Imperial", "Trooper", "Soldier", "Guardian", "Officer", "Commando", "Agent", "Operator", "Striker", "Hand"],
            "commander": ["Officer", "Commander", "Admiral", "Strategist", "Tactician", "Commando", "Marshal", "General", "Leader", "Director"],
            "bountyhunter": ["Hunter", "Tracker", "Assassin", "Mercenary", "Enforcer", "Slayer", "Collector", "Operator", "Striker", "Reaper"],
            "mandalorian": ["Mando", "Warrior", "Hunter", "Commando", "Berzerker", "Guardian", "Leader", "Champion", "Legend", "Mandalore"],
            "droideka": ["Deka", "Unit", "Drone", "Sentinel", "Guard", "Destroyer", "Annihilator", "Warrior", "Legend", "Colossus"],
            "sbd": ["Unit", "Trooper", "Commando", "Guardian", "Destroyer", "Annihilator", "Warrior", "Specialist", "Titan", "Colossus"],
            "jedi": ["Jedi", "Knight", "Guardian", "Consular", "Sentinel", "Sage", "Master", "Warden", "Champion", "Force"],
            "sith": ["Sith", "Lord", "Warrior", "Assassin", "Marauder", "Inquisitor", "Champion", "Sorcerer", "Overlord", "Emperor"]
        }

    @property
    def level(self):
        return (self.xp // self.xp_per_lvl) + 1

    @property
    def kdr(self):
        if self.deaths == 0: return float(self.kills)
        return round(self.kills / self.deaths, 2)

    @property
    def clean_name(self):
        """Returns the name without redundant color resets or trailing spaces."""
        # Use regex to strip any ^7 specifically if it's at the start or end
        name = self.name.strip()
        while name.startswith("^7"): name = name[2:].strip()
        while name.endswith("^7"): name = name[:-2].strip()
        return name      

    def get_title(self, current_mode=0):
        # New title every 10 levels (was every 2.5)
        idx = (self.level - 1) // 10
        # Cap at 99 (level 1000) — beyond that stays at the final title
        idx = min(idx, 99)
        
        color = "^1" if self.faction in DARK_SIDE_FACTIONS else "^5"

        def _get_title_at_index(faction_key, index):
            """Resolve title at a given index (0-99), using base titles or generated."""
            base = self.paths.get(faction_key, self.paths["jedi"])
            if index < 20:
                return base[index]
            # Generated extended title: prefix + core noun
            tier_idx = (index - 20) // 10  # 0-7
            noun_idx = (index - 20) % 10   # 0-9
            prefix = TIER_PREFIXES[tier_idx] if tier_idx < len(TIER_PREFIXES) else "Ultimate "
            nouns = self.core_nouns.get(faction_key, self.core_nouns["jedi"])
            noun = nouns[noun_idx % len(nouns)]
            return f"{prefix}{noun}"

        # Force Jedi/Sith titles in Duel Mode (Mode 3)
        if current_mode == 3:
            faction_key = "sith" if self.faction in DARK_SIDE_FACTIONS else "jedi"
            title = _get_title_at_index(faction_key, idx)
            return f"{color}{title}^7 "

        # Standard career path
        faction_key = self.faction if self.faction in self.paths else "jedi"
        title = _get_title_at_index(faction_key, idx)
        return f"{color}{title}^7"
        
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
        self.db_filename = 'players.json'
        self.load_config()
        self.players = []
        self.current_server_mode = 0
        self.active_bets = {}
        self.active_pazaak = {} # NEW: Tracks active card games
        self.dealer_credits = 0 
        self.active_deathrolls = {}
        self.init_sqlite()
        self.last_sync_time = 0
        self.last_nemesis_cleanup = 0
        self.last_kill_sig = ""

    def init_sqlite(self):
        # Initialize JSON-backed DB stored in self.db (dict keyed by GUID)
        self.db = {}
        # Map clean_name -> guid for quick lookups; saved together in JSON
        self.name_map = {}
        # Ensure filename ends with .json
        if not self.db_filename.lower().endswith('.json'):
            base, _ = os.path.splitext(self.db_filename)
            self.db_filename = base + '.json'

        # Create file if missing
        if not os.path.exists(self.db_filename):
            try:
                with open(self.db_filename, 'w', encoding='utf-8') as f:
                    json.dump({}, f, indent=2)
            except Exception:
                pass

        # Load into memory (support two formats: wrapper {players,names} or flat players dict)
        try:
            lock_fd = None
            try:
                lock_fd = self._acquire_lock()
            except Exception:
                lock_fd = None

            with open(self.db_filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict) and 'players' in data:
                    self.db = data.get('players', {}) or {}
                    self.name_map = data.get('names', {}) or {}
                elif isinstance(data, dict):
                    # old flat format: build name_map from records
                    self.db = data
                    self.name_map = {}
                    for gk, rec in self.db.items():
                        try:
                            clean = strip_colors(rec.get('clean_name', rec.get('name', ''))).lower()
                            if clean:
                                self.name_map[clean] = gk
                        except Exception:
                            pass
                else:
                    self.db = {}
                    self.name_map = {}
        except Exception:
            self.db = {}
            self.name_map = {}
        finally:
            try:
                if lock_fd:
                    self._release_lock(lock_fd)
            except Exception:
                pass

    def _save_db_quick(self):
        # Write atomically with lock: write to a temp file then replace
        tmp_path = self.db_filename + '.tmp'
        lock_fd = None
        try:
            lock_fd = self._acquire_lock()
        except Exception:
            lock_fd = None

        try:
            try:
                with open(tmp_path, 'w', encoding='utf-8') as f:
                    wrapper = {'players': self.db, 'names': self.name_map}
                    json.dump(wrapper, f, indent=2)
                    f.flush()
                    try:
                        os.fsync(f.fileno())
                    except Exception:
                        pass

                # atomic replace
                try:
                    os.replace(tmp_path, self.db_filename)
                except Exception:
                    # fallback to rename
                    os.rename(tmp_path, self.db_filename)
            except Exception as e:
                print(f"[ERROR] Could not write DB temp file: {e}")
        finally:
            try:
                if lock_fd:
                    self._release_lock(lock_fd)
            except Exception:
                pass

    def _acquire_lock(self):
        """Acquire a cross-platform exclusive lock on a small lockfile next to the DB.
        Returns the open file descriptor that must be passed to _release_lock.
        """
        lock_path = self.db_filename + '.lock'
        # ensure lock dir exists
        d = os.path.dirname(self.db_filename)
        if d and not os.path.exists(d):
            try:
                os.makedirs(d, exist_ok=True)
            except Exception:
                pass

        # open the lock file
        lock_fd = open(lock_path, 'a+b')

        # apply platform-specific locking
        if os.name == 'nt':
            # Windows
            import msvcrt
            try:
                msvcrt.locking(lock_fd.fileno(), msvcrt.LK_LOCK, 1)
            except Exception:
                # fallback: try to write and flush
                try:
                    lock_fd.write(b'1')
                    lock_fd.flush()
                except Exception:
                    pass
        else:
            # POSIX
            import fcntl
            fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX)

        return lock_fd

    def _release_lock(self, lock_fd):
        try:
            if os.name == 'nt':
                import msvcrt
                try:
                    lock_fd.seek(0)
                    msvcrt.locking(lock_fd.fileno(), msvcrt.LK_UNLCK, 1)
                except Exception:
                    pass
            else:
                import fcntl
                try:
                    fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
                except Exception:
                    pass
        finally:
            try:
                lock_fd.close()
            except Exception:
                pass

    def get_leaderboard_pos(self, p):
        # Use in-memory JSON DB to compute rank/total
        all_players = list(self.db.values()) if hasattr(self, 'db') else []
        rank = sum(1 for r in all_players if int(r.get('xp', 0)) > int(p.xp)) + 1
        total = len(all_players)

        # Formatting (1st, 2nd, 3rd, 4th...)
        suffix = "th"
        if rank % 10 == 1 and rank % 100 != 11: suffix = "st"
        elif rank % 10 == 2 and rank % 100 != 12: suffix = "nd"
        elif rank % 10 == 3 and rank % 100 != 13: suffix = "rd"

        return f"{rank}{suffix}", total

    def check_leaderboard_promotion(self, p):
        """Checks if a player has recently entered the Top 5 and persists the status."""
        all_players = sorted(list(self.db.values()) if hasattr(self, 'db') else [], key=lambda x: int(x.get('xp', 0)), reverse=True)
        fifth_place_xp = None
        if len(all_players) >= 5:
            fifth_place_xp = int(all_players[4].get('xp', 0))

        if fifth_place_xp is not None:
            if p.xp >= fifth_place_xp:
                if not p.is_top5:
                    self.send_rcon(f'say "^5[NETWORK ALERT] {p.clean_name} ^7has broken into the ^2TOP 5 ^7Leaderboard!"')
                    p.is_top5 = True
                    rec = self.db.get(p.guid)
                    if rec is not None:
                        rec['top5'] = 1
                        self._save_db_quick()
            else:
                if p.is_top5:
                    p.is_top5 = False
                    rec = self.db.get(p.guid)
                    if rec is not None:
                        rec['top5'] = 0
                        self._save_db_quick()

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
        # Default to JSON storage filename
        db_name = self.settings.get('db_file', 'players.json')
        self.db_filename = os.path.join(base_dir, db_name)

    def sync_player(self, sid, raw_name, guid, ip="0.0.0.0"):
        # 1. Prepare display names
        # Preserve color codes in display_name but build a clean lookup key without colors
        display_name = raw_name.strip() if raw_name else f"Player_{sid}"
        if not display_name:
            display_name = f"Player_{sid}"
        clean = strip_colors(display_name).lower()

        # Default starting values
        xp, kills, deaths, faction, credits, top5_db = 0, 0, 0, "jedi", 100, 0
        
        # Use JSON DB for lookup/update
        data = None
        top5_db = 0

        # Normalize guid
        guid_key = guid if guid else None

        # 1) Try GUID lookup
        if guid_key and guid_key not in ["0", "N/A", ""] and hasattr(self, 'db'):
            rec = self.db.get(guid_key)
            if rec:
                data = rec

        # 2) Fallback: lookup by IP
        if not data and ip and ip != "0.0.0.0" and hasattr(self, 'db'):
            found_key = None
            for gk, rec in list(self.db.items()):
                if rec.get('last_ip') == ip:
                    found_key = gk
                    data = rec
                    break

            # If we found a record by IP and a real GUID is now provided, migrate it
            if data and guid_key and guid_key not in ["0", "N/A", ""]:
                # Move record to new guid key
                try:
                    data['guid'] = guid_key
                    self.db[guid_key] = data
                    if found_key and found_key != guid_key:
                        del self.db[found_key]
                    # update name map
                    try:
                        clean_key = strip_colors(data.get('clean_name', data.get('name', ''))).lower()
                        if clean_key:
                            self.name_map[clean_key] = guid_key
                    except Exception:
                        pass
                    self._save_db_quick()
                except Exception:
                    pass

        # 3) Create or update record
        if data:
            xp = int(data.get('xp', 0))
            kills = int(data.get('kills', 0))
            deaths = int(data.get('deaths', 0))
            faction = data.get('faction', 'jedi')
            credits = int(data.get('credits', 100))
            top5_db = int(data.get('top5', 0))

            # Update name and IP (preserve color codes in 'name')
            data['name'] = display_name
            data['clean_name'] = clean
            data['last_ip'] = ip
            # Ensure GUID key exists
            if guid_key and guid_key not in ["0", "N/A", ""]:
                data['guid'] = guid_key
                self.db[guid_key] = data
            # update name_map
            try:
                clean_key = strip_colors(clean).lower()
                if clean_key:
                    self.name_map[clean_key] = data.get('guid', guid_key)
            except Exception:
                pass
            self._save_db_quick()
        else:
            # Insert new record
            key = guid_key if guid_key else f"TEMP_{ip}"
            data = {
                'guid': key,
                'name': display_name,
                'clean_name': clean,
                'last_ip': ip,
                'xp': xp,
                'credits': credits,
                'kills': kills,
                'deaths': deaths,
                'faction': faction,
                'top5': 0
            }
            self.db[key] = data
            try:
                clean_key = strip_colors(clean).lower()
                if clean_key:
                    self.name_map[clean_key] = key
            except Exception:
                pass
            self._save_db_quick()

        # 4. Update Memory (Critical for !top/!wealth commands)
        # We remove any existing instance of this player from the active list
        self.players = [p for p in self.players if p.id != sid]
        if guid and guid not in ["0", "N/A", ""]:
            self.players = [p for p in self.players if p.guid != guid]

        # 5. Finalize Player Object with the NEW name
        p = Player(sid, display_name, xp, kills, deaths, faction, credits, self.settings, guid=guid)
        p.raw_name = raw_name
        p.ip = ip 
        p.is_top5 = True if top5_db == 1 else False
        
        self.players.append(p)
        
        return p

    def save_player_stat(self, p):
        """Saves player stats using GUID as the Primary Key to prevent title resets."""
        # 1. Critical Safety: Never save if GUID is missing/bad.
        # This prevents an uninitialized session from overwriting high-level DB data.
        if not p or not hasattr(p, 'guid') or not p.guid or p.guid in ["0", "N/A", "Unknown", ""]:
            return

        # 2. Data Safety Caps
        p.credits = max(0, min(9999999, p.credits))
        p.xp = max(0, p.xp)
        top5_val = 1 if getattr(p, 'is_top5', False) else 0
        clean_name = strip_colors(p.name).lower()
        ip_to_save = getattr(p, 'ip', '0.0.0.0')

        # Persist to JSON-backed DB using GUID as the key
        rec_key = p.guid
        if not hasattr(self, 'db'):
            self.db = {}
        if not hasattr(self, 'name_map'):
            self.name_map = {}

        rec = {
            'guid': rec_key,
            # preserve colors in stored name
            'name': p.name,
            'clean_name': clean_name,
            'last_ip': ip_to_save,
            'xp': int(p.xp),
            'credits': int(p.credits),
            'kills': int(p.kills),
            'deaths': int(p.deaths),
            'faction': p.faction,
            'top5': int(top5_val)
        }

        self.db[rec_key] = rec

        # update name map so lookups by name can find the guid
        try:
            clean_key = strip_colors(clean_name).lower()
            if clean_key:
                self.name_map[clean_key] = rec_key
        except Exception:
            pass

        max_retries = 3
        for attempt in range(max_retries):
            try:
                self._save_db_quick()
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(0.5)
                else:
                    print(f"[CRITICAL] Could not persist player {p.name}: {e}")

    def send_rcon(self, command, get_response=False):
        try:
            if '"' in command:
                parts = command.split('"', 2)
                if len(parts) >= 3:
                    # Check if this is a 'say' command
                    if command.lower().startswith("say"):
                        # Keep stripping ^7 for 'say'
                        clean_msg = normalize(parts[1])
                    else:
                        # For 'svtell' and others, keep the ^7 (only strip whitespace)
                        clean_msg = parts[1].strip()
                        
                    command = f'{parts[0]}"{clean_msg}"{parts[2]}'

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
            return
        
        lines = response.split('\n')
        active_sids = []

        for line in lines:
            # Regex to catch Slot ID, Name, and IP
            match = re.search(r'^\s*(\d+)\s+\-?\d+\s+\d+\s+(.*?)\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)

            if match and match.group(1) and match.group(2) and match.group(3):
                try:
                    sid = int(match.group(1))
                    raw_name = match.group(2).strip().replace('"', '')
                    ip = match.group(3)
                    active_sids.append(sid)
                    
                    # 1. Check if they are ALREADY in memory (RAM)
                    # We match by SID or IP since 'status' doesn't usually show GUID
                    p = next((x for x in self.players if x.id == sid or x.ip == ip), None)
                    
                    if p:
                        p.id = sid 
                        p.ip = ip
                        # We don't overwrite p.name here to keep the cleaned version from sync_player
                    else:
                        # 2. If NOT in memory, use your new sync_player logic
                        # We pass "0" or None for GUID because 'status' doesn't provide it.
                        # Your updated sync_player will automatically find them via IP!
                        self.sync_player(sid, raw_name, guid=None, ip=ip)
                        
                except Exception as e:
                    print(f"[!] Status Parse Error: {e}")

        # 3. Clean up disconnected players
        self.players = [p for p in self.players if p.id in active_sids]

    def load_player_by_guid(self, sid, guid):
        """Loads or creates a player based on their unique ja_guid."""
        rec = None
        if hasattr(self, 'db'):
            rec = self.db.get(guid)

        if rec:
            name = rec.get('name', 'New Player')
            xp = int(rec.get('xp', 0))
            credits = int(rec.get('credits', 100))
            kills = int(rec.get('kills', 0))
            deaths = int(rec.get('deaths', 0))
            faction = rec.get('faction', 'jedi')
            top5 = int(rec.get('top5', 0))
            p = Player(sid, name, xp, kills, deaths, faction, credits, self.settings, guid=guid)
            p.is_top5 = True if top5 == 1 else False
        else:
            # Create default record
            new_rec = {
                'guid': guid,
                'name': 'New Player',
                'clean_name': 'new player',
                'last_ip': '0.0.0.0',
                'xp': 0,
                'credits': 100,
                'kills': 0,
                'deaths': 0,
                'faction': 'jedi',
                'top5': 0
            }
            if not hasattr(self, 'db'):
                self.db = {}
            self.db[guid] = new_rec
            self._save_db_quick()
            p = Player(sid, 'New Player', 0, 0, 0, 'jedi', 100, self.settings, guid=guid)

        return p

    def check_rank_change(self, player, old_level):
        new_level = player.level
        current_title = player.get_title(self.current_server_mode)
        
        if new_level > old_level:
            self.send_rcon(f'say "^3RANK UP: ^2{player.clean_name} ^7is now a {current_title} ^2(Lvl {new_level})!"')
            
            if new_level % 100 == 0:
                self.send_rcon(f'say "^5MILESTONE: ^7{player.clean_name} has reached Level ^2{new_level}^7!"')
                
        elif new_level < old_level:
            self.send_rcon(f'say "^1DEMOTION: ^1{player.clean_name} ^7has fallen to {current_title} ^1(Lvl {new_level})..."')

    def get_player_rank(self, p):
        """Returns the player's numerical rank based on total XP (e.g., 1st, 2nd)."""
        all_players = sorted(list(self.db.values()) if hasattr(self, 'db') else [], key=lambda x: int(x.get('xp', 0)), reverse=True)
        higher_count = sum(1 for r in all_players if int(r.get('xp', 0)) > int(p.xp))
        total_players = len(all_players)

        rank = higher_count + 1

        # Formatting the suffix (st, nd, rd, th)
        if 11 <= (rank % 100) <= 13:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(rank % 10, "th")

        return f"{rank}{suffix}", total_players

    def process_kill(self, k_id, v_id, w_id, raw_line=""):
        try:
            k_id, v_id = int(k_id), int(v_id)
        except: return

        # IMPORTANT: Look up by .id (the slot number), NOT .name
        killer = next((p for p in self.players if p.id == k_id), None)
        victim = next((p for p in self.players if p.id == v_id), None)

        if not killer or not victim:
            # print(f"Debug: Kill ignored. Killer({k_id}) or Victim({v_id}) not in memory.")
            return

        if killer and victim and killer != victim:
            try:
                if hasattr(self, 'db'):
                    rec = self.db.get(killer.guid)
                    if rec and 'credits' in rec:
                        try:
                            killer.credits = int(rec.get('credits', killer.credits))
                        except Exception:
                            pass
            except Exception as e:
                print(f"[ERROR] Could not sync credits for kill: {e}")

        # 3. SAFETY CHECKS
        if not victim: return 
        
        # Remove victim bet
        self.active_bets.pop(victim.id, None)

        if k_id == v_id or w_id in [97, 100]: # Suicide or World/falling
            victim.streak = 0
            self.save_player_stat(victim)
            return

        # 4. TEAM KILL CHECK
        is_teamkill = False
        if killer and self.current_server_mode != 3:
            k_team = getattr(killer, 'team', -1)
            v_team = getattr(victim, 'team', -2)
            if k_team == v_team and k_team in [1, 2]:
                is_teamkill = True

        if is_teamkill:
            tk_penalty = 500
            killer.xp = max(0, killer.xp - tk_penalty)
            killer.credits = max(0, killer.credits - 1000)
            killer.streak = 0
            # Clean name for announcement
            k_name_clean = killer.name.strip()
            self.send_rcon(f'say "^1TRAITOR: ^7{killer.clean_name} killed a teammate! Lost ^1{tk_penalty} XP^7!"')
            self.save_player_stat(killer)
            self.save_player_stat(victim) 
            return 

        # 5. VICTIM LOGIC (Dynamic XP Loss)
        old_lvl_v = victim.level
        base_loss = int(self.settings.get('xp_loss', 10))
        xp_scale_loss = max(1, int(self.settings.get('xp_level_scaling', 10)))
        f_bonus_loss = int(self.settings.get('faction_bonus', 15))
        # Level scaling: higher-level killer causes more XP loss
        loss_scaling = killer.level // xp_scale_loss
        # Level difference: getting stomped by a much higher-level enemy hurts more
        loss_diff = max(0, killer.level - victim.level)
        # Opposite faction: same faction bonus applies to loss too
        killer_is_dark_loss = killer.faction in DARK_SIDE_FACTIONS
        victim_is_dark_loss = victim.faction in DARK_SIDE_FACTIONS
        loss_faction = f_bonus_loss if (killer_is_dark_loss != victim_is_dark_loss) else 0
        loss = base_loss + loss_scaling + loss_diff + loss_faction

        # --- Force Drain: Reverse Force Surge ---
        force_drain = random.random() < 0.05
        if force_drain:
            loss *= 3
            self.send_rcon(f'say "^1FORCE DRAIN: ^7{victim.clean_name} lost their connection to the Force for ^13x XP loss^7!"')

        victim.xp = max(0, victim.xp - loss)
        loss_str = f"^1(-{loss} XP)" if victim.xp > 0 else "^5(Protected)"
        
        victim.deaths += 1
        victim.streak = 0
        self.check_rank_change(victim, old_lvl_v)

        # 6. KILLER LOGIC (Rewards)
        if killer and k_id != 1022:
            old_lvl_k = killer.level
            cred_gain = int(self.settings.get('passive_credit_gain', 10))
            bonus_str = ""

            # --- Dynamic XP Calculation ---
            base_xp = int(self.settings.get('xp_per_kill', 50))
            xp_scale = max(1, int(self.settings.get('xp_level_scaling', 10)))
            f_bonus = int(self.settings.get('faction_bonus', 15))
            # Level scaling: bonus XP based on victim's level
            level_scaling = victim.level // xp_scale
            # Level difference: bonus XP for killing higher-level enemies (underdog reward)
            level_diff = max(0, victim.level - killer.level)
            # Opposite faction: hero kills villain or vice versa
            killer_is_dark = killer.faction in DARK_SIDE_FACTIONS
            victim_is_dark = victim.faction in DARK_SIDE_FACTIONS
            faction_bonus = f_bonus if (killer_is_dark != victim_is_dark) else 0
            xp_gain = base_xp + level_scaling + level_diff + faction_bonus
            if faction_bonus:
                bonus_str += f" ^5[FACTION +{faction_bonus}]"

            # --- Random Events ---
            mult = 3 if random.random() < 0.05 else 1
            if mult > 1: 
                self.send_rcon(f'say "^3FORCE SURGE: ^7{killer.clean_name} tapped into the Force for ^23x XP^7!"')
            
            # --- Revenge ---
            if victim.guid in killer.nemesis_map and killer.nemesis_map[victim.guid] >= 3:
                revenge_bonus = 200
                killer.credits = min(9999999, killer.credits + revenge_bonus)
                # Reset the grudge so they can't farm revenge on the next kill
                killer.nemesis_map[victim.guid] = 0
                bonus_str += f" ^5[REVENGE +{revenge_bonus}cr]"

            # --- Theft ---
            if victim.credits > 5000:
                stolen = int(victim.credits * 0.05)
                victim.credits -= stolen
                killer.credits = min(9999999, killer.credits + stolen)
                bonus_str += f" ^1[STOLE {stolen}cr]"

            # House Vault
            self.dealer_credits = min(9999999, self.dealer_credits + 5) 

            # Heist trigger
            if random.random() < 0.01 and self.dealer_credits > 100:
                heist = int(self.dealer_credits * 0.50 if self.dealer_credits > 5000 else self.dealer_credits * 0.20)
                heist_msg = "^1MEGA HEIST" if self.dealer_credits > 5000 else "^3HEIST"
                self.send_rcon(f'say "{heist_msg}: ^7{killer.clean_name} cracked the House Vault for ^2{heist}cr^7!"')
                self.dealer_credits -= heist
                killer.credits = min(9999999, killer.credits + heist)

            # --- Stats Update ---
            killer.kills += 1
            killer.streak += 1
            killer.xp += (xp_gain * mult)
            
            # --- Nemesis Tracking ---
            killer.nemesis_map[victim.guid] = killer.nemesis_map.get(victim.guid, 0) + 1
            if killer.nemesis_map[victim.guid] == 3:
                self.send_rcon(f'say "^1NEMESIS: ^7{killer.clean_name} is dominating {victim.clean_name}!"')

            # --- Payouts (Bounties/Bets) ---
            b_reward = sum(victim.bounty.values()) if hasattr(victim, 'bounty') and victim.bounty else 0
            victim.bounty = {}

            bet_reward = 0
            if killer.id in self.active_bets:
                bet_data = self.active_bets.pop(killer.id)
                raw_val = sum(bet_data.values()) if isinstance(bet_data, dict) else int(bet_data)
                actual_bet = min(10000, raw_val)
                bet_reward = int(actual_bet * 1.50)

            killer.credits = min(9999999, killer.credits + cred_gain + b_reward + bet_reward)

            payout_val = b_reward + bet_reward
            payout_str = f" ^7& secured ^3{payout_val}cr^7" if payout_val > 0 else ""
            k_title = killer.get_title(self.current_server_mode)
            v_title = victim.get_title(self.current_server_mode)
            
            self.send_rcon(f'say "{k_title} {killer.clean_name} ^3(+{xp_gain * mult} XP) ^7defeated {v_title} {victim.clean_name} {payout_str} {loss_str}{bonus_str}"')
            
            self.check_rank_change(killer, old_lvl_k)
            self.save_player_stat(killer)

        self.save_player_stat(victim)            
           
    def play_pazaak(self, p, amount):
        if p.credits < amount:
            self.send_rcon(f'svtell {p.id} "^1Error: You need more credits!"')
            return
        if amount <= 0: return

        p.credits = max(0, p.credits - amount)
        # Add a portion of the bet to the dealer's bonus pot immediately
        self.dealer_credits = min(9999999, self.dealer_credits + int(amount * 0.1))
        
        card = random.randint(1, 10)
        self.active_pazaak[p.id] = {"score": card, "bet": amount}
        
        self.send_rcon(f'svtell {p.id} "^5[PAZAAK] ^7Bet: ^3{amount}cr ^7| Dealer Bonus: ^2{self.dealer_credits}cr"')
        self.send_rcon(f'svtell {p.id} "^7Your Hand: ^2{card} ^7| !hit, !stand or !side?"')
        self.save_player_stat(p)

    def handle_chat(self, sid, name, msg):
        clean_log_name = strip_colors(name).lower().strip()
        msg = re.sub(r'\^.', '', msg).lower().strip()
        
        if not msg.startswith("!"):
            return

        p = next((x for x in self.players if x.id == sid or strip_colors(x.name).lower().strip() == clean_log_name), None)
        
        if not p:
            self.sync_current_players()
            p = next((x for x in self.players if x.id == sid or strip_colors(x.name).lower().strip() == clean_log_name), None)

        if not p:
            return

        # 5. Success! Now use the SID to reply
        target_sid = p.id

        if msg == "!title" or msg.startswith("!title "):
            parts = msg.split(" ", 1)
            
            # Dynamically set the help lists based on the current mode
            if self.current_server_mode == 3:
                hero_list, villain_list = "jedi", "sith"
                mode_note = "^1(^7Duel Mode Active: ^5Jedi^1/^1Sith)"
            else:
                hero_list = "rebel, elite, clone, arc, hero, wookiee, jedi"
                villain_list = "imperial, commander, bh, mando, deka, sbd, sith"
                mode_note = "^2(All Modes)"

            # --- Title Progression List (Tier-Based Summary) ---
            if len(parts) > 1 and parts[1].strip().lower() == "list":
                if not p: return
                
                base_titles = p.paths.get(p.faction, p.paths.get("jedi", []))
                nouns = p.core_nouns.get(p.faction, p.core_nouns["jedi"])
                
                self.send_rcon(f'svtell {p.id} "^5--- {p.faction.upper()} PROGRESSION (10 Lvl / Title) ---"')
                
                # Tier 1: Base titles (Lv 1-200)
                self.send_rcon(f'svtell {p.id} "^2Tier 1 (Lv 1-200): ^7{base_titles[0]} ^7-> ^{5 if p.faction not in ["imperial","commander","bountyhunter","mandalorian","droideka","sbd","sith"] else "1"}{base_titles[-1]}^7"')
                
                # Tiers 2-9: Generated titles with prefixes
                for t_idx, prefix in enumerate(TIER_PREFIXES):
                    start_lvl = 200 + (t_idx * 100) + 1
                    end_lvl = start_lvl + 90
                    first_title = f"{prefix}{nouns[0]}"
                    last_title = f"{prefix}{nouns[-1]}"
                    self.send_rcon(f'svtell {p.id} "^2Tier {t_idx + 2} (Lv {start_lvl}-{end_lvl}): ^7{first_title} ^7-> ^{5 if p.faction not in ["imperial","commander","bountyhunter","mandalorian","droideka","sbd","sith"] else "1"}{last_title}^7"')
                
                self.send_rcon(f'svtell {p.id} "^3Note: ^7New title every ^210 levels^7. No level cap!"')
                return  

            # Usage check
            if len(parts) < 2 or parts[1].strip() == "":
                self.send_rcon(f'svtell {p.id} "^3Usage: !title <career_name> {mode_note}"')
                self.send_rcon(f'svtell {p.id} "^2Tip: ^7Type ^3!title list ^7to see your rank progression!"')
                self.send_rcon(f'svtell {p.id} "^5Hero: ^7{hero_list}"')
                self.send_rcon(f'svtell {p.id} "^1Villain: ^7{villain_list}"')
                return

            choice = parts[1].lower().strip().replace(" ", "")
            mapping = {
                "rebel": "rebel", "soldier": "rebel", "elite": "elitetrooper", 
                "elitetrooper": "elitetrooper", "clone": "clonetrooper", 
                "clonetrooper": "clonetrooper", "arc": "arctrooper", 
                "arctrooper": "arctrooper", "hero": "hero", "wookiee": "wookiee", 
                "wookie": "wookiee", "jedi": "jedi", "imperial": "imperial", 
                "imp": "imperial", "commander": "commander", "bh": "bountyhunter",
                "bountyhunter": "bountyhunter", "mandalorian": "mandalorian", 
                "mando": "mandalorian", "droideka": "droideka", "deka": "droideka", 
                "sbd": "sbd", "superbattledroid": "sbd", "sith": "sith"
            }
            
            if choice in mapping:
                target_faction = mapping[choice]
                if self.current_server_mode == 3 and target_faction not in ["jedi", "sith"]:
                    self.send_rcon(f'svtell {p.id} "^1Error: ^7The career ^3{choice} ^7is not available in Duel Mode!"')
                    return 

                p.faction = target_faction
                self.save_player_stat(p)
                title_display = p.get_title(self.current_server_mode)
                self.send_rcon(f'say "{p.clean_name} ^7is now a ^3{title_display}^7!"')
            else:
                self.send_rcon(f'svtell {p.id} "^1Error: ^7Career \'{choice}\' not found."')

        elif msg == "!help" or msg == "!commands":        
            self.send_rcon(f'svtell {p.id} "^5--- DATA TERMINAL ---"')
            
            # Personal Section (Consolidated)
            self.send_rcon(f'svtell {p.id} "^3Identity: ^7!rank (Rank), !title (Careers), !bank"')
            
            # Economy Section
            self.send_rcon(f'svtell {p.id} "^3Finance: ^7!pay <name> <amt>, !wealth, !top (Leaderboard), !vault"')
            
            # Bounty Section
            self.send_rcon(f'svtell {p.id} "^3Contracts: ^7!bounty <name> <amt>, !bounties (Active Marks)"')
            
            # Gambling Section Breakdown
            self.send_rcon(f'svtell {p.id} "^5--- CANTINA GAMES ---"')
            self.send_rcon(f'svtell {p.id} "^3Pazaak: ^7!pazaak <amt> (Use !hit, !stand, !side)"')
            
            # Jackpot info
            self.send_rcon(f'svtell {p.id} "^2Bonus: ^7Secure the ^3!vault ^7by defeating the ^1Dealer ^7in Pazaak!"')
            
        # Check for the command without a space first, or the command with a space
        elif msg == "!pazaak" or msg.startswith("!pazaak "):
            parts = msg.split()
            if len(parts) < 2:
                self.send_rcon(f'svtell {p.id} "^3Usage: !pazaak <amount>"')
            else:
                try:
                    amt = int(parts[1])
                    
                    # 1. ENFORCE MAX BET (10k)
                    if amt > 10000:
                        amt = 10000
                        self.send_rcon(f'svtell {p.id} "^3PAZAAK: ^7Max bet is ^210,000cr^7. Bet adjusted."')
                    
                    # 2. CHECK IF PLAYER HAS ENOUGH CREDITS
                    if p.credits < amt:
                        self.send_rcon(f'svtell {p.id} "^1Error: You only have {p.credits}cr."')
                    elif amt <= 0:
                        self.send_rcon(f'svtell {p.id} "^1Error: Bet must be greater than 0."')
                    else:
                        # Proceed with the game
                        self.play_pazaak(p, amt)

                except ValueError:
                    self.send_rcon(f'svtell {p.id} "^1Error: Amount must be a number."')
        elif msg == "!hit" and p.id in self.active_pazaak:
            game = self.active_pazaak[p.id]
            card = random.randint(1, 10)
            game["score"] += card
            
            if game["score"] == 20:
                win = game["bet"] * 3
                p.credits = min(9999999, p.credits + win)
                # High visibility Magenta and Green for the big win
                self.send_rcon(f'say "^6PAZAAK! {p.clean_name} ^7hit ^220 ^7and wins ^3{win}cr ^2(3x Payout)!"')
                del self.active_pazaak[p.id]
            elif game["score"] > 20:
                remaining_bet = game["bet"] - int(game["bet"] * 0.1)
                self.dealer_credits = min(9999999, self.dealer_credits + remaining_bet)                
                self.send_rcon(f'say "{p.clean_name} ^1BUSTED ^7with ^1{game["score"]}!. ^7Dealer Pot is now ^3{self.dealer_credits}^3cr^7."')
                del self.active_pazaak[p.id]
            else:
                self.send_rcon(f'svtell {p.id} "^5[PAZAAK] {p.clean_name} ^7draws {card}. ^7Total: ^2{game["score"]}"')
            self.save_player_stat(p)
        elif msg == "!stand" and p.id in self.active_pazaak:
            game = self.active_pazaak[p.id]
            diff = int(self.settings.get('pazaak_difficulty', 17))
            dealer_hand = random.randint(diff, 20)
            
            self.send_rcon(f'say "^5[PAZAAK] {p.clean_name} (^2{game["score"]}^7) vs Dealer(^1{dealer_hand}^7)"')
            
            if game["score"] > dealer_hand:
                # Player Wins: Double bet + Dealer's current accumulated pool
                bonus = self.dealer_credits
                win = (game["bet"] * 2) + bonus
                p.credits = min(9999999, p.credits + win)
                self.dealer_credits = 0 
                self.send_rcon(f'say "^2WIN! {p.clean_name} ^7beat the house and took the ^3{bonus}cr ^7bonus pot! Total: ^3{win}cr^7!"')
            
            elif game["score"] == dealer_hand:
                p.credits += game["bet"]
                tax_refund = int(game["bet"] * 0.1)
                self.dealer_credits = max(0, self.dealer_credits - tax_refund)
                self.send_rcon(f'say "^3PUSH! ^7Scores tied at {dealer_hand}. Bet returned."')       
            else:
                remaining_bet = game["bet"] - int(game["bet"] * 0.1)
                self.dealer_credits = min(9999999, self.dealer_credits + remaining_bet)
                self.send_rcon(f'say "^1LOSS! ^7The House wins. Dealer Pot is now ^3{self.dealer_credits}cr^7."')            
            del self.active_pazaak[p.id]
            self.save_player_stat(p)
        elif msg.startswith("!side") and p.id in self.active_pazaak:
            game = self.active_pazaak[p.id]
            parts = msg.split(" ")
            
            if len(parts) < 2:
                cards_str = ", ".join([f"^{ '2' if c > 0 else '1' }{c}^7" for c in p.side_deck])
                self.send_rcon(f'svtell {p.id} "^5[SIDE DECK] ^7Your cards: {cards_str}"')
                self.send_rcon(f'svtell {p.id} "^7Use: !side <card_value> (e.g., !side -2)"')
                return

            try:
                card_val = int(parts[1])
                if card_val in p.side_deck:
                    # Apply modifier
                    game["score"] += card_val
                    p.side_deck.remove(card_val) 
                    
                    self.send_rcon(f'svtell {p.id} "^2[PAZAAK] ^7played a ^3{card_val} ^7side card! New Total: ^2{game["score"]}^7"')
                    
                    # Replenish side deck
                    p.side_deck.append(random.randint(-5, 5))
                    
                    self.save_player_stat(p) 
                    
                    if game["score"] == 20:
                        self.send_rcon(f'svtell {p.id} "^2[PAZAAK] ^7You hit 20! Type ^2!stand ^7to claim the jackpot!"')
                        # --- ADDED: Save progress at 20 ---
                        self.save_player_stat(p)
                        
                    elif game["score"] > 20:
                        remaining_bet = game["bet"] - int(game["bet"] * 0.1)
                        self.dealer_credits = min(9999999, self.dealer_credits + remaining_bet)
                        self.send_rcon(f'say "{p.clean_name} ^1BUSTED ^7after side card! Pot is ^3{self.dealer_credits}cr^7."')
                        del self.active_pazaak[p.id]
                        self.save_player_stat(p) 
                else:
                    self.send_rcon(f'svtell {p.id} "^1Error: ^7You don\'t have a {card_val} card!"')
            except ValueError:
                self.send_rcon(f'svtell {p.id} "^1Error: ^7Invalid card value."')
        elif msg == "!rank":
            rank_str, total = self.get_player_rank(p)
            title = p.get_title(self.current_server_mode)
            progress = p.get_progress_bar()
            
            self.send_rcon(f'svtell {p.id} "^5--- ACCESSING DATAPAD ---"')
            self.send_rcon(f'svtell {p.id} "^7Network Rank: ^2{rank_str} ^7in Sector ^3(of {total} players)"')
            self.send_rcon(f'svtell {p.id} "^7Clearance: {title} ^7(Lvl ^2{p.level}^7)"')
            self.send_rcon(f'svtell {p.id} "^7Logs: ^2{p.kills} Eliminations ^7| ^1{p.deaths} Casualties ^7(KDR: ^3{p.kdr}^7)"')
            self.send_rcon(f'svtell {p.id} "^7Training: {progress}"')
            self.send_rcon(f'svtell {p.id} "^7Credits: ^3{p.credits}cr"')
        elif msg == "!wealth":
            # Build grouping by clean_name and take max credits
            grouped = {}
            if hasattr(self, 'db'):
                for rec in self.db.values():
                    clean_n = rec.get('clean_name', '').lower()
                    creds = int(rec.get('credits', 0))
                    name = rec.get('name', 'Unknown Bounty')
                    if clean_n not in grouped or creds > grouped[clean_n][1]:
                        grouped[clean_n] = (name, creds)

            rich_players = sorted(grouped.values(), key=lambda x: x[1], reverse=True)[:5]
            self.send_rcon('say "^5--- MOST WANTED (FINANCIAL) ---"')
            for i, (name, credits) in enumerate(rich_players, 1):
                display_name = name if name else "Unknown Bounty"
                self.send_rcon(f'say "^7{i}.^7 ^2{display_name} ^7- ^3{credits}cr"')
        elif msg == "!bank" or msg == "!wallet" or msg == "!credits":
            # Sum up the total value of all bounty contributions
            total_bounty = sum(p.bounty.values()) if isinstance(p.bounty, dict) else 0
            b_msg = f" ^1(Bounty: {total_bounty})" if total_bounty > 0 else ""
            self.send_rcon(f'svtell {p.id} "^5[BANK] {p.clean_name}^7, you have ^3{p.credits} Credits^7.{b_msg}"')
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
                        self.send_rcon(f'say "^5[BANK] {p.clean_name} ^7cancelled their bounty on {target.name}. ^2{refund}cr ^7refunded."')
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

                if target:
                    # --- ADDED: SELF-BOUNTY CHECK ---
                    if target.id == p.id:
                        self.send_rcon(f'svtell {p.id} "^1Error: ^7You cannot put a bounty on yourself!"')
                        return

                    if p.credits >= amount and amount > 0:
                        if not isinstance(target.bounty, dict): target.bounty = {}
                        
                        p.credits -= amount
                        target.bounty[p.name] = target.bounty.get(p.name, 0) + amount
                        
                        total = sum(target.bounty.values())
                        self.send_rcon(f'say "^1WAGER: {p.clean_name} ^7put a ^3{amount}cr ^7bounty on {target.name}! Total: ^1{total}cr^7!"')
                        self.save_player_stat(p)
                else:
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

                # --- NEW: MAX BET LIMIT (10k) ---
                if amt > 10000:
                    amt = 10000
                    self.send_rcon(f'svtell {p.id} "^3BET: ^7Max bet is ^210,000cr^7. Adjusted to limit."')

                target = next((x for x in self.players if target_name in x.name.lower()), None)

                if not target:
                    self.send_rcon(f'svtell {p.id} "^1Error: ^7Player \'{parts[1]}\' not found."')
                    return

                # --- SELF-BET CHECK ---
                if target.id == p.id:
                    self.send_rcon(f'svtell {p.id} "^1Error: ^7You cannot bet on yourself!"')
                    return

                # --- CREDIT CHECK & EXECUTION ---
                if p.credits >= amt and amt > 0:
                    p.credits = max(0, p.credits - amt)
                    
                    if target.id not in self.active_bets:
                        self.active_bets[target.id] = {}
                    
                    self.active_bets[target.id][p.name] = self.active_bets[target.id].get(p.name, 0) + amt
                    
                    self.send_rcon(f'say "^2BET: {p.clean_name} ^7bet ^3{amt}cr ^7on ^5{target.name}^7!"')
                    
                    # Ensure the database reflects the deducted credits immediately
                    self.save_player_stat(p)
                else:
                    self.send_rcon(f'svtell {p.id} "^1Error: ^7Insufficient credits or invalid amount."')
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
                target = next((x for x in self.players if target_name in x.name.lower()), None)

                if not target:
                    self.send_rcon(f'svtell {p.id} "^1Error: ^7Player \'{parts[1]}\' not found."')
                    return
                
                if target == p:
                    self.send_rcon(f'svtell {p.id} "^1Error: ^7You cannot pay yourself!"')
                    return

                if p.credits >= amount and amount > 0:
                    if amount > 100000: # 100k cap check
                        self.send_rcon(f'svtell {p.id} "^1Error: ^7Max single transfer is 100k."')
                        return
                    
                    p.credits -= amount
                    target.credits += amount
                    self.send_rcon(f'say "^2TRANSFER: {p.clean_name} ^7sent ^3{amount} Credits ^7to {target.name}!"')
                    self.save_player_stat(p)
                    self.save_player_stat(target)
                else:
                    self.send_rcon(f'svtell {p.id} "^1Error: ^7Insufficient credits."')
            except ValueError:
                self.send_rcon(f'svtell {p.id} "^7Usage: !pay <name> <amount>"') 
        elif msg == "!top":
            # Group by clean_name and pick record with MAX xp
            grouped = {}
            if hasattr(self, 'db'):
                for rec in self.db.values():
                    clean_n = rec.get('clean_name', '').lower()
                    xp_val = int(rec.get('xp', 0))
                    name = rec.get('name', 'Unknown Pilot')
                    faction = rec.get('faction', 'jedi')
                    if clean_n not in grouped or xp_val > grouped[clean_n]['xp']:
                        grouped[clean_n] = {'name': name, 'xp': xp_val, 'faction': faction}

            top_players = sorted(grouped.values(), key=lambda x: x['xp'], reverse=True)[:5]
            xp_needed = 250
            self.send_rcon('say "^5--- SECTOR TOP ELIMINATORS ---"')
            for i, rec in enumerate(top_players, 1):
                display_name = rec.get('name', 'Unknown Pilot')
                xp = rec.get('xp', 0)
                faction = rec.get('faction', 'jedi')
                lvl = (xp // xp_needed) + 1
                f_name = faction.capitalize() if faction else "Jedi"
                self.send_rcon(f'say "^7{i}.^7 ^2{display_name}^7 - Lvl ^3{lvl} ^2({f_name})"')
        elif msg == "!vault" or msg == "!house":
            # Show the current progressive jackpot
            self.send_rcon(f'svtell {p.id} "^5[HOUSE] ^7Current Vault: ^3{self.dealer_credits} Credits ^7(1 percent chance to heist on kill)"') 

    def handle_smod_command(self, raw_admin_name, admin_id, full_message):
        """Processes SMOD commands and announces actions in [BANK] style."""
        # Split into arguments to mimic tkManager logic
        msg_parts = full_message.split()
        if not msg_parts:
            return

        # Extract command and strip '!' if present
        command = msg_parts[0].lower()
        if command.startswith("!"):
            command = command[1:] 

        admin_clean = normalize(raw_admin_name)

        # 1. HELP COMMAND
        if command in ["help", "commands"]:
            self.send_rcon('say "^5[ADMIN] ^7Commands: !setlevel, !givexp, !takexp, !givecredits, !takecredits, !resetplayer')
            return

        # 2. RELOAD CONFIG
        if command == "reload":
            self.config.read('chaos.cfg')
            self.settings = self.config['SETTINGS']
            self.send_rcon('say "^5[ADMIN] ^7Configuration reloaded."')
            return

        # Commands below require a target player: !cmd <target> <value>
        if len(msg_parts) < 2:
            return

        target_search = msg_parts[1].lower()
        p = next((x for x in self.players if target_search in strip_colors(x.name).lower()), None)
        
        if not p:
            return

        try:
            xp_per_lvl = int(self.settings.get('xp_per_level', 250))
            action_text = ""

            # --- LEVEL / XP CONTROL ---
            if command == "setlevel":
                if len(msg_parts) < 3: return
                val = int(msg_parts[2])
                # No level cap
                target_level = max(1, val)
                p.xp = (target_level - 1) * xp_per_lvl
                action_text = f"^7set ^5{p.name} ^7to Level ^5{target_level}"

            elif command in ["givexp", "addxp"]:
                if len(msg_parts) < 3: return
                val = int(msg_parts[2])
                p.xp = max(0, p.xp + val)
                action_text = f"^7gave ^5{val} XP ^7to ^5{p.name}"

            elif command in ["takexp", "subxp"]:
                if len(msg_parts) < 3: return
                val = abs(int(msg_parts[2]))
                p.xp = max(0, p.xp - val)
                action_text = f"^7took ^5{val} XP ^7from ^5{p.name}"

            # --- CREDIT CONTROL ---
            elif command in ["givecredits", "addcredits"]:
                if len(msg_parts) < 3: return
                val = int(msg_parts[2])
                p.credits = max(0, min(9999999, p.credits + val))
                action_text = f"^7gave ^5{val} credits ^7to ^5{p.name}"

            elif command in ["takecredits", "subcredits"]:
                if len(msg_parts) < 3: return
                val = abs(int(msg_parts[2]))
                p.credits = max(0, p.credits - val)
                action_text = f"^7took ^5{val} credits ^7from ^5{p.name}"

            # --- RESET / ADMIN UTILITY ---
            elif command == "resetplayer":
                p.xp = 0
                p.credits = 100
                action_text = f"^7reset all stats for ^5{p.name}"

            if action_text:
                self.save_player_stat(p)
                # Broadcast in the [BANK] style format requested
                self.send_rcon(f'say "^5[ADMIN] ^7{admin_clean} {action_text}"')
                print(f"[ADMIN] {admin_clean} {normalize(action_text)}")

        except (ValueError, IndexError):
            pass

    def run(self):
        log = self.settings['logname']
        print(f"[*] Chaos Plugin Active. Monitoring: {log}")
        
        # 1. Initial sync and Timer initialization
        self.sync_current_players()
        self.last_sync_time = time.time()
        self.last_save_time = time.time() 

        # 2. Check server mode (Authenticity) via RCON at startup
        try:
            startup_resp = str(self.send_rcon("g_authenticity", True)).lower()
            if '="3"' in startup_resp.replace("^7", "").replace("^9", "").replace(" ", ""):
                self.current_server_mode = 3
                print("[SYSTEM] Server detected in DUEL mode (Authenticity 3)")
            else:
                self.current_server_mode = 0
                print("[SYSTEM] Server detected in OPEN mode")
        except Exception as e:
            print(f"[ERROR] Could not fetch g_authenticity: {e}")
            self.current_server_mode = 0

        # 3. Initial Bookmark (Start at end of file)
        last_sz = os.path.getsize(log) if os.path.exists(log) else 0

        while True:
            try:
                # --- TIMER LOGIC ---
                # Refresh player list every 60s
                if time.time() - self.last_sync_time > 60:
                    self.sync_current_players()
                    self.last_sync_time = time.time()

                # Save all stats every 60s
                if time.time() - self.last_save_time > 60:
                    for p in self.players:
                        self.save_player_stat(p)
                    self.last_save_time = time.time()

                # Clean up nemesis_map entries stuck at 1 kill every 5 minutes
                if time.time() - self.last_nemesis_cleanup > 300:
                    for p in self.players:
                        p.nemesis_map = {g: c for g, c in p.nemesis_map.items() if c > 1}
                    self.last_nemesis_cleanup = time.time()

                # --- LOG MONITORING ---
                if not os.path.exists(log):
                    time.sleep(1)
                    continue

                curr_sz = os.path.getsize(log)
                
                if curr_sz < last_sz:
                    last_sz = 0 

                if curr_sz > last_sz:
                    with open(log, 'r', encoding='utf-8', errors='ignore', newline=None) as f:
                        f.seek(last_sz)
                        
                        # SPEED TWEAK: Line-by-line iterator is much faster than f.readlines()
                        while True:
                            line = f.readline()
                            if not line:
                                break
                            
                            line = line.strip()
                            if not line: continue
                            
                            # Execute parse_line. If it returns True (InitGame), 
                            # we jump the pointer to the very end of the file.
                            if self.parse_line(line) is True:
                                f.seek(0, 2)
                                last_sz = f.tell()
                                break
                        
                        last_sz = f.tell()

                time.sleep(0.1)
            except Exception as e:
                print(f"[CRITICAL ERROR] Loop failure: {e}")
                time.sleep(2) 

    def parse_line(self, line):
        # 1. PLAYER SPAWN / JOIN
        # Matches SID, Name, and GUID from the spawn line
        m_spawn = re.search(r'Player\s+(\d+).*?\\name\\(.*?)\\.*?ja_guid\\([A-Z0-9]{32})', line)
        if m_spawn:
            slot_id = int(m_spawn.group(1))
            p_name = m_spawn.group(2)
            p_guid = m_spawn.group(3)
            self.sync_player(slot_id, p_name, p_guid, "0.0.0.0")
            return

        # 2. MAP CHANGE / INIT GAME
        if "InitGame:" in line:
            print("[SYSTEM] Map Change: Saving stats and refunding active stakes...")
            for p in self.players:
                # Refund Pazaak Bets
                if hasattr(self, 'active_pazaak') and p.id in self.active_pazaak:
                    game = self.active_pazaak.pop(p.id)
                    p.credits += game["bet"]

                # Refund Bounties
                if hasattr(p, 'bounty') and isinstance(p.bounty, dict):
                    for setter_name, amt in p.bounty.items():
                        setter = next((x for x in self.players if x.name == setter_name), None)
                        if setter:
                            setter.credits += amt
                            self.save_player_stat(setter)
                    p.bounty = {}

                # Save the player's current RAM state to the DB
                self.save_player_stat(p)

            # Clear memory ONLY AFTER everything above is saved
            self.players = [] 
            
            # Re-detect game mode
            line_low = line.lower()
            if "g_authenticity\\3" in line_low.replace(" ", ""):
                self.current_server_mode = 3
            else:
                self.current_server_mode = 0
                
            time.sleep(2) 
            self.sync_current_players()
            self.last_sync_time = time.time()
            return

        # 3. NAME CHANGE
        elif "ClientUserinfoChanged:" in line:
            m = re.search(r'ClientUserinfoChanged:\s*(\d+)\s*n\\([^\\]+)', line)
            if m:
                sid, name = int(m.group(1)), m.group(2)
                # Syncing updates the name in DB and memory immediately
                self.sync_player(sid, name)
            return

        # 4. DISCONNECTS / REFUNDS
        elif "ClientDisconnect:" in line or "entered the game" in line:
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
                                self.save_player_stat(contributor)
                        t_p.bounty = {}

                    # Refund Bets
                    if t_sid in self.active_bets:
                        bet_dict = self.active_bets.pop(t_sid)
                        for name, amt in bet_dict.items():
                            contributor = next((x for x in self.players if x.name == name), None)
                            if contributor:
                                contributor.credits += amt
                                self.save_player_stat(contributor)

                    # Refund Pazaak game on disconnect
                    if t_sid in self.active_pazaak:
                        game = self.active_pazaak.pop(t_sid)
                        t_p.credits += game["bet"]

                    self.save_player_stat(t_p)
            return

        # 5. KILLS
        elif "Kill: " in line:
            m = re.search(r'Kill:\s*(\d+)\s+(\d+)\s+(\d+):', line)
            if m:
                k_id, v_id, w_id = m.group(1), m.group(2), m.group(3)
                sig = f"{k_id}-{v_id}-{w_id}-{line.strip()}"
                
                if sig == self.last_kill_sig:
                    return
                
                self.last_kill_sig = sig
                self.process_kill(k_id, v_id, w_id, line)
            return

        # 6. SMOD ADMIN COMMANDS
        elif "SMOD smsay:" in line:
            smod_match = re.search(r'SMOD smsay:\s+(.*?)\s+\(adminID:\s+(\d+)\).*?\):\s*(.*)$', line)
            if smod_match:
                admin_raw_name = smod_match.group(1).strip()
                admin_id = smod_match.group(2)
                full_message = smod_match.group(3).strip()
                self.handle_smod_command(admin_raw_name, admin_id, full_message)
            return

        # 7. CHAT (say/tell) - FIXED FOR NAME MATCHING
        elif "say:" in line.lower() or "tell:" in line.lower():
            try:
                # 1. Identify SID
                log_sid = -1
                sid_match = re.search(r'(\d+)[:\s]*(?:say|tell):', line, re.IGNORECASE)
                if sid_match:
                    sid_str = sid_match.group(1)
                    log_sid = int(sid_str[2:]) if len(sid_str) > 2 else int(sid_str)

                # 2. Extract Message Content
                msg_match = re.search(r'(?:say|tell):.*?: "(.*)"', line, re.IGNORECASE)
                if msg_match:
                    message = msg_match.group(1).strip()
                    
                    # 3. Find Player: Try SID first
                    p = next((x for x in self.players if x.id == log_sid), None)
                    
                    # 4. FALLBACK: Search by Name (Fixes "Valzhar" error)
                    if not p:
                        # Find the name between the chat type and the colon
                        name_match = re.search(r'(?:say|tell):\s*(.*?)\s*:', line, re.IGNORECASE)
                        if name_match:
                            raw_found_name = name_match.group(1).strip()
                            clean_found = strip_colors(raw_found_name).lower()
                            # Match normalized name in memory (ignore colors)
                            p = next((x for x in self.players if strip_colors(x.name).lower() == clean_found), None)

                    if p:
                        self.handle_chat(p.id, p.name, message)
                    elif "console" not in line.lower():
                        print(f"[PARSER WARNING] Could not find player for: {line.strip()}")

            except Exception as e:
                print(f"[PARSER ERROR] Chat line failed: {e}")


if __name__ == "__main__":
    # Initialize the plugin once outside the loop
    plugin = MBIIChaosPlugin()
    
    while True:
        try:
            plugin.run()
        except KeyboardInterrupt:
            print("\n[SYSTEM] Manual shutdown. Saving all players and refunding bets...")
            for p in plugin.players:
                # REFUND PAZAAK ON SCRIPT RESTART
                if hasattr(plugin, 'active_pazaak') and p.id in plugin.active_pazaak:
                    game = plugin.active_pazaak.pop(p.id)
                    p.credits += game["bet"]
                plugin.save_player_stat(p)
            sys.exit(0)
        except Exception as e:
            print(f"CRASH DETECTED: {e}")
            print("Attempting emergency safety save...")
            try:
                for p in plugin.players:
                    plugin.save_player_stat(p)
            except:
                print("Emergency save failed.")
            
            print("Restarting plugin in 5 seconds...")
            time.sleep(5) 