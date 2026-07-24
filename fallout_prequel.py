#!/usr/bin/env python3
"""
FALLOUT: THE LAST DAY BEFORE
A text-based RPG set in August 2077, two months before the Great War.
"""

import random
import time
import sys
import os
import traceback
import json
from datetime import datetime

TEST_MODE = os.environ.get("FALLOUT_TEST_MODE", "").lower() == "1"

# ============================================================
# COLOR AND FORMAT
# ============================================================
class C:
    GREEN = "\033[92m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    PURPLE = "\033[95m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

def cls():
    os.system('clear' if os.name != 'nt' else 'cls')

def slow_print(text, speed=0.015):
    if TEST_MODE:
        print(text)
    else:
        for ch in text:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(speed)
        print()

def pause():
    try:
        input(f"\n{C.DIM}--- Press Enter to continue ---{C.RESET}")
    except (EOFError, KeyboardInterrupt):
        pass

def header(text):
    border = "=" * 60
    print(f"\n{C.GREEN}{border}{C.RESET}")
    print(f"{C.GREEN}{C.BOLD}  {text.center(56)}{C.RESET}")
    print(f"{C.GREEN}{border}{C.RESET}\n")

def vault_text(text):
    speed = 0.001 if TEST_MODE else 0.03
    for line in text.split("\n"):
        print(f"{C.CYAN}{C.BOLD}{line}{C.RESET}")
        time.sleep(speed)

def choice_prompt(prompts):
    print(f"\n{C.BOLD}What do you do?{C.RESET}")
    for i, (text, _) in enumerate(prompts, 1):
        print(f"  {C.YELLOW}{i}{C.RESET}). {text}")
    while True:
        try:
            raw = input(f"\n{C.BOLD}Choose [{C.YELLOW}1-{len(prompts)}{C.RESET}]: {C.RESET}")
            idx = int(raw) - 1
            if 0 <= idx < len(prompts):
                logger.choice(prompts[idx][0])
                return idx
            print(f"{C.RED}Invalid choice.{C.RESET}")
        except (ValueError, EOFError):
            print(f"{C.RED}Please enter a number.{C.RESET}")

# ============================================================
# PLAYER
# ============================================================
class Player:
    def __init__(self):
        self.name = ""
        self.spec = {
            "Strength": 5,
            "Perception": 5,
            "Endurance": 5,
            "Charisma": 5,
            "Intelligence": 5,
            "Agility": 5,
            "Luck": 5,
        }
        self.traits = []
        self.hp = 100
        self.max_hp = 100
        self.xp = 0
        self.level = 1
        self.karma = 0
        self.inventory = []
        self.equipment = {"weapon": None, "armor": None}
        self.flags = {}
        self.caps = 200
        self.companion = None
        self.xp_to_next = 150

    def add_xp(self, amount):
        self.xp += amount
        leveled = False
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.max_hp += 20
            self.hp = min(self.hp + 20, self.max_hp)
            self.xp_to_next = self.level * 150
            leveled = True
            logger.level_up(self.level)
        return leveled

    def take_damage(self, amount):
        dodged = random.randint(1, 10) <= self.spec["Agility"]
        if dodged:
            return 0
        blocked = 0
        if self.equipment["armor"]:
            blocked = self.equipment["armor"]["defense"]
        damage = max(1, amount - blocked)
        self.hp -= damage
        return damage

    def attack(self):
        if not self.equipment["weapon"]:
            return random.randint(1, 5)
        base = self.equipment["weapon"]["damage"]
        bonus = self.spec["Strength"] // 3
        crit = 1 if random.randint(1, 10) <= self.spec["Luck"] else 0
        return base + bonus + crit * 5

    def can_do(self, stat, value):
        return self.spec[stat] >= value

player = Player()

# ============================================================
# ITEMS AND ENEMIES
# ============================================================
WEAPONS = {
    "pipe_wrench": {"name": "Pipe Wrench", "damage": 8, "desc": "A rusted pipe wrench from the workshop."},
    "10mm_pistol": {"name": "10mm Pistol", "damage": 12, "desc": "Standard military-issue sidearm."},
    "vault_sword": {"name": "Vault-Tec Survival Sword", "damage": 15, "desc": "A finely-crafted combat blade."},
    "plasma_pistol": {"name": "Plasma Pistol", "damage": 20, "desc": "Experimental energy weapon from RobCo."},
    "Fat_Man": {"name": "Fat Man", "damage": 50, "desc": "A tactical mini-nuke launcher."},
}

ARMORS = {
    "leather_jacket": {"name": "Leather Jacket", "defense": 3, "desc": "Better than nothing."},
    "leather_armored_coat": {"name": "Armored Leather Coat", "defense": 6, "desc": "Reinforced with steel plating."},
    "vault_suit": {"name": "Vault Suit", "defense": 5, "desc": "Official Vault-Tec uniform."},
    "marines_combat_armor": {"name": "Marines Combat Armor", "defense": 12, "desc": "Military-grade armor."},
}

ENEMIES = {
    "biker": {"name": "Biker Thug", "hp": 30, "attack": 7, "xp": 30, "drops": ["pipe_wrench", "wallet_50"]},
    "raider": {"name": "Steel Dawn Raider", "hp": 40, "attack": 8, "xp": 50, "drops": ["10mm_pistol", "leather_jacket"]},
    "super_mutant": {"name": "Early Super Mutant", "hp": 70, "attack": 14, "xp": 100, "drops": ["vault_sword", "leather_armored_coat"]},
    "robot_sec": {"name": "RobCo Security Bot", "hp": 45, "attack": 11, "xp": 70, "drops": ["plasma_pistol"]},
    "protector": {"name": "Vault Security Enforcer", "hp": 55, "attack": 12, "xp": 80, "drops": ["marines_combat_armor"]},
    "mastermind": {"name": "Dr. Emil Ingram", "hp": 40, "attack": 8, "xp": 200, "drops": ["Fat_Man"]},
}

COMPANIONS = {
    "sammy": {
        "name": "Sammy Alvarez",
        "desc": "A vault technician. Skilled, loyal, has family inside.",
        "role": "tech",
        "combat_bonus": 5,
    },
    "tinker": {
        "name": "Tinker Tom",
        "desc": "A genius engineer. Paranoid about the government.",
        "role": "science",
        "combat_bonus": 8,
    },
    "deputy": {
        "name": "Deputy Cooper",
        "desc": "A lawman from outside. Wants to keep order.",
        "role": "combat",
        "combat_bonus": 12,
    },
}

# ============================================================
# STORY DATA
# ============================================================

# ============================================================
# ERROR REPORTING & STATE CAPTURE
# ============================================================
class GameLogger:
    """Tracks game events and dumps state on crash."""

    def __init__(self):
        self._events = []
        self._scene_name = "startup"

    def event(self, category, message):
        entry = {
            "t": datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "s": self._scene_name,
            "c": category,
            "m": message,
        }
        self._events.append(entry)
        if len(self._events) > 200:
            self._events.pop(0)

    def scene_enter(self, name):
        self._scene_name = name
        self.event("scene", f"Entering {name}")

    def scene_exit(self, name):
        self.event("scene", f"Exited {name}")

    def choice(self, label):
        self.event("choice", label)

    def karma(self, delta, reason):
        self.event("karma", f"{delta:+d} ({reason})")

    def flag_set(self, key, value):
        self.event("flag", f"{key} = {value}")

    def combat(self, details):
        self.event("combat", details)

    def level_up(self, new_level):
        self.event("level", f"Level {new_level}")

    def dump_snapshot(self, player, exc=None):
        """Prints full debug dump to stderr and writes to log file."""
        snap = GameStateSnapshot.from_player(player, self._scene_name, self, exc)
        text = snap.render()
        print(text, file=sys.stderr)
        log_dir = os.path.expanduser("~/.local/share/fallout_prequel")
        os.makedirs(log_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"debug_{ts}.log")
        try:
            with open(log_file, "w") as f:
                f.write(text)
            print(f"\n{C.DIM}Full debug log written to: {log_file}{C.RESET}", file=sys.stderr)
            print(f"\n{C.DIM}Full debug log written to: {log_file}{C.RESET}", file=sys.stderr)
        except OSError:
            pass
        return snap


logger = GameLogger()


class GameStateSnapshot:
    """Captures complete snapshot of player state + event log."""

    @staticmethod
    def from_player(player, scene, game_logger, exc=None):
        snap = GameStateSnapshot()
        snap.name = player.name or "(unnamed)"
        snap.spec = dict(player.spec)
        snap.traits = list(player.traits)
        snap.hp = player.hp
        snap.max_hp = player.max_hp
        snap.xp = player.xp
        snap.level = player.level
        snap.karma = player.karma
        snap.caps = player.caps
        snap.inventory = list(player.inventory)
        snap.weapon = (player.equipment["weapon"]["name"] if player.equipment["weapon"]P1+r4632=1B5B32347E\P0+r2531\P0+r2638\P1+r6B62=7F\ else "None")
        snap.armor = (player.equipment["armor"]["name"] if player.equipment["armor"] else "None")
        snap.companion_name = (COMPANIONS[player.companion]["name"] if player.companion else "None")
        snap.flags = dict(player.flags)
        snap.scene = scene
        snap.events = list(game_logger._events)
        snap.exc_info = None
        if exc is not None:
            snap.exc_info = type(exc).__name__ if isinstance(exc, Exception) else str(exc)
        snap._text = None
        snap._build_text()
        return snap

    def _build_text(self):
        lines = []
        lines.append("=" * 60)
        lines.append("  FALLOUT: THE LAST DAY BEFORE - DEBUG DUMP")
        lines.append("=" * 60)
        lines.append("")
        if self.exc_info:
            lines.append(f"EXCEPTION: {self.exc_info}")
            lines.append("")
        lines.append("PLAYER STATE")
        lines.append("-" * 40)
        lines.append(f"  Name:        {self.name}")
        lines.append(f"  Level:       {self.level}")
        lines.append(f"  HP:          {self.hp}/{self.max_hp}")
        lines.append(f"  XP:          {self.xp}")
        lines.append(f"  Karma:       {self.karma}")
        lines.append(f"  Caps:        {self.caps}")
        t = ", ".join(self.traits) or "None"
        lines.append(f"  Traits:      {t}")
        lines.append(f"  Weapon:      {self.weapon}")
        lines.append(f"  Armor:       {self.armor}")
        lines.append(f"  Companion:   {self.companion_name}")
        inv = ", ".join(P0+r6B49\P1+r6B44=1B5B337E\P1+r6B68=1B4F48\P1+r4037=1B4F46\P1+r6B50=1B5B357E\P1+r6B4E=1B5B367E\self.inventory) if self.inventory else "Empty"
        lines.append(f"  Inventory:   {inv}")
        lines.append("")
        lines.append("S.P.E.C.I.A.L.")
        lines.append("-" * 40)
        for stat, val in self.spec.items():
            lines.append(f"  {stat:14s} {val}")
        lines.append("")
        lines.append("STORY FLAGS")
        lines.append("-" * 40)
        if self.flags:
            for k, v in self.flags.items():
                lines.append(f"  {k:25s} = {v}")
        else:
            lines.append("  (none)")
        lines.append("")
        lines.append(f"ACTIVE SCENE: {self.scene}")
        lines.append("")
        lines.append("RECENT EVENT LOG (last 30)")
        lines.append("-" * 40)
        for e in self.events[-30:]:
            lines.append(f"  [{e['s']:20s}] {e['c']:8s} {e['m']}")
        lines.append("")
        lines.append("=" * 60)
        self._text = "\n".join(lines)


    def render(self):
        return self._text

INTRO = """The year is August 2077.

Tensions are mounting across the nation. News feeds cycle endlessly:
resource wars in the West, protests in the East, the Great War looming
like a storm cloud. Most people pretend it won't happen to them.

But you're different. You work at Vault 37, one of Vault-Tec's
underground shelters. And you've seen things you shouldn't have.

The vault's systems are glitching. Some of the residents... aren't
supposed to be here. And there's a man in a black suit who visits
every night, asking questions no one answers.

Tonight, the emergency sirens are testing at 21:00. But something
tells you they won't stop when the test is over."""

# ============================================================
# UTILITY
# ============================================================
def give_item(p, item_key):
    if item_key.startswith("wallet_"):
        amount = int(item_key.replace("wallet_", ""))
        p.caps += amount
        print(f"\n{C.YELLOW}You found {amount} caps!{C.RESET}")
    elif item_key in WEAPONS:
        w = WEAPONS[item_key]
        current_w = p.equipment["weapon"]
        if current_w is None or w["damage"] > current_w["damage"]:
            p.equipment["weapon"] = w
            print(f"\n{C.YELLOW}You equipped: {w['name']}{C.RESET}")
        else:
            p.inventory.append(item_key)
            print(f"\n{C.YELLOW}You picked up: {w['name']}{C.RESET}")
    elif item_key in ARMORS:
        a = ARMORS[item_key]
        current_def = (p.equipment["armor"]["defense"] if p.equipment["armor"] else 0)
        if p.equipment["armor"] is None or a["defense"] > current_def:
            p.equipment["armor"] = a
            print(f"\n{C.YELLOW}You equipped: {a['name']}{C.RESET}")
        else:
            p.inventory.append(item_key)
    else:
        p.inventory.append(item_key)

def combat(p, enemy_key):
    enemy = dict(ENEMIES[enemy_key])
    header(f"COMBAT: {enemy['name']}")
    print(f"{C.RED}{enemy['name']}{C.RESET} {C.DIM}(HP: {enemy['hp']}){C.RESET}")
    logger.combat(f"vs {enemy['name']} (hp={enemy['hp']}, atk={enemy['attack']})")
    companion_bonus = 0
    if p.companion:
        companion_bonus = COMPANIONS[p.companion]["combat_bonus"]

    while enemy["hp"] > 0 and p.hp > 0:
        print(f"\n{C.BOLD}--- Your turn ---{C.RESET}")
        print(f"{C.GREEN}HP: {max(p.hp, 0)}/{p.max_hp}{C.RESET}  |  {C.YELLOW}Enemy HP: {max(enemy['hp'], 0)}{C.RESET}")
        actions = [
            ("Attack", "attack"),
            ("Check Equipment", "equip"),
        ]
        if p.companion:
            cn = COMPANIONS[p.companion]["name"]
            actions.append((f"{cn} attacks", "companion"))
        if p.hp < p.max_hp * 0.6:
            actions.append(("Flee", "flee"))
        choice = choice_prompt(actions)
        action = actions[choice][1]

        if action == "attack":
            dmg = p.attack() + companion_bonus
            enemy["hp"] -= dmg
            print(f"{C.CYAN}You deal {dmg} damage!{C.RESET}")
            if p.equipment["weapon"] and random.randint(1, 10) <= 3:
                extra = random.randint(2, 5)
                enemy["hp"] -= extra
                wn = p.equipment["weapon"]["name"]
                print(f"{C.YELLOW}Critical hit from {wn}! +{extra} damage!{C.RESET}")
        elif action == "equip":
            w = p.equipment["weapon"]
            a = p.equipment["armor"]
            wn = w["name"] if w else "Fists"
            an = a["name"] if a else "None"
            print(f"{C.DIM}Weapon: {wn}{C.RESET}")
            print(f"{C.DIM}Armor: {an}{C.RESET}")
            print(f"{C.DIM}Inventory: {p.inventory if p.inventory else 'Empty'}{C.RESET}")
            continue
        elif action == "flee":
            if random.randint(1, 10) <= p.spec["Agility"]:
                print(f"{C.YELLOW}You escaped!{C.RESET}")
                return "fled"
            else:
                print(f"{C.RED}Failed to escape!{C.RESET}")
        elif action == "companion":
            cb = COMPANIONS[p.companion]["combat_bonus"] + random.randint(3, 8)
            enemy["hp"] -= cb
            cn = COMPANIONS[p.companion]["name"]
            print(f"{C.PURPLE}{cn} deals {cb} damage!{C.RESET}")

        if enemy["hp"] > 0:
            e_dmg = enemy["attack"] + random.randint(-2, 4)
            actual = p.take_damage(e_dmg)
            armor_msg = ""
            if p.equipment["armor"] and e_dmg > actual:
                blocked = e_dmg - actual
                armor_msg = f" ({p.equipment['armor']['name']} blocked {blocked})"
            print(f"{C.RED}{enemy['name']} hits you for {actual} damage!{armor_msg}{C.RESET}")

    if p.hp <= 0:
        return "dead"
    return "won"

# ============================================================
# TITLE SCREEN
# ============================================================
def title_screen():
    for _ in range(3):
        cls()
        title = f"""{C.GREEN}{C.BOLD}
  FALLOUT: THE LAST DAY BEFORE
     ===============================
  A Prequel to the Great War

  {C.RESET}  {C.CYAN}The Last Days of Vault 37{C.RESET}
  {C.DIM}August 2077 - A Text RPG Adventure{C.RESET}

  {C.YELLOW}Press Enter to begin  |  Type 'quit' to exit{C.RESET}
"""
        print(title)
        try:
            inp = input()
            if inp.lower() == "quit":
                print(f"\n{C.DIM}Goodbye. May you live in interesting times...{C.RESET}\n")
                sys.exit(0)
        except (EOFError, KeyboardInterrupt):
            return
        time.sleep(0.3)

# ============================================================
# CHARACTER CREATION
# ============================================================
def character_creation():
    while True:
        try:
            name = input(f"\n{C.BOLD}{C.GREEN}Enter your name, citizen:{C.RESET}\n> ")
            if name.strip():
                player.name = name.strip()
                break
            print(f"{C.RED}Name cannot be empty.{C.RESET}")
        except (EOFError, KeyboardInterrupt):
            player.name = "Wastelander"
            break

    header("S.P.E.C.I.A.L. ALLOCATION")
    print(f"{C.DIM}You have {C.YELLOW}40{C.DIM} points to distribute across 7 attributes.{C.RESET}")
    print(f"{C.DIM}Each stat must be between {C.YELLOW}1{C.DIM} and {C.YELLOW}10{C.DIM}.{C.RESET}")

    stats = {k: 1 for k in player.spec}
    points_left = 40 - 7
    stat_names = list(stats.keys())

    while points_left > 0:
        print(f"\n{C.BOLD}Points remaining: {points_left}{C.RESET}")
        for s in stat_names:
            bar = " " * (10 - stats[s]) + str(stats[s])
            print(f"  {C.CYAN}{s:14s}:{C.RESET} {C.YELLOW}{bar}{C.RESET}")
        try:
            choice = input(f"\nIncrease a stat ({C.YELLOW}1-{len(stat_names)}{C.RESET}): ")
            idx = int(choice) - 1
            if 0 <= idx < len(stat_names) and stats[stat_names[idx]] < 10:
                stats[stat_names[idx]] += 1
                points_left -= 1
            elif stats[stat_names[idx]] >= 10:
                print(f"{C.RED}Stat is already at maximum!{C.RESET}")
            else:
                print(f"{C.RED}Invalid choice.{C.RESET}")
        except (ValueError, EOFError):
            for s in stat_names:
                while points_left > 0 and stats[s] < 10:
                    stats[s] += 1
                    points_left -= 1
            break

    player.spec = stats

    header("CHOOSE A TRAIT")
    traits = [
        ("Night Person", "Bonus to night-time actions, -1 Perception during day"),
        ("Fast Metabolism", "+1 Agility, but eat twice as much"),
        ("Chem Reliant", "Chemicals are more effective, but add addiction"),
        ("Wild Wasteland", "Survival skills are doubled in the outdoors"),
        ("One More Lap", "Starting HP +20, but max HP doesn't increase with level"),
        ("Small Parts", "Expertise with small components and gadgets"),
    ]
    print(f"\n{C.DIM}These traits define who you are.{C.RESET}")
    for i, (name, desc) in enumerate(traits, 1):
        print(f"  {C.PURPLE}{i}{C.RESET}). {C.BOLD}{name}{C.RESET} - {C.DIM}{desc}{C.RESET}")
    while True:
        try:
            t = int(input(f"\n{C.BOLD}Choose trait ({C.YELLOW}1-{len(traits)}{C.RESET}, or 0 to skip): ")) - 1
            if -1 <= t < len(traits):
                if t >= 0:
                    player.traits.append(traits[t][0])
                    if traits[t][0] == "One More Lap":
                        player.max_hp += 20
                        player.hp += 20
                break
        except (ValueError, EOFError):
            break

    header("YOUR FIRST DAY")
    start_weapons = [
        ("Pipe Wrench", "pipe_wrench"),
        ("Boxing Gloves", None),
        ("Combat Knife", "pipe_wrench"),
    ]
    print(f"\n{C.DIM}On your first day at Vault 37, you brought with you:{C.RESET}")
    for i, (name, _) in enumerate(start_weapons, 1):
        print(f"  {i}). {name}")
    while True:
        try:
            w = int(input(f"\n{C.BOLD}Choose ({C.YELLOW}1-3{C.RESET}): ")) - 1
            if 0 <= w < len(start_weapons):
                if start_weapons[w][1]:
                    player.equipment["weapon"] = WEAPONS[start_weapons[w][1]]
                break
        except (ValueError, EOFError):
            break

    cls()
    header(f"CHARACTER CREATED: {player.name}")
    print(f"{C.CYAN}{'S.P.E.C.I.A.L.':14s}{'Value':>10s}{C.RESET}")
    print(f"{C.CYAN}{'-'*25}{C.RESET}")
    for stat, val in player.spec.items():
        bar = str(val) + " " + ("#" * val)
        print(f"{C.CYAN}{stat:14s}{C.RESET} {C.YELLOW}{bar}{C.RESET}")
    print(f"\n{C.PURPLE}Trait:{C.RESET} {player.traits[0] if player.traits else 'None'}")
    print(f"{C.YELLOW}HP:{C.RESET} {player.hp}/{player.max_hp}")
    print(f"{C.GREEN}Caps:{C.RESET} {player.caps}")
    print(f"\n{C.DIM}Remember your choices, {player.name}. They matter.")
    pause()

# ============================================================
# SCENE: WAKE UP
# ============================================================
def scene_wake_up():
    header("DAY 1 - AUGUST 27, 2077")
    vault_text(INTRO)
    slow_print(f"\nYou wake in your quarters at Vault 37, Sector 4G.")
    slow_print("The hum of the air recyclers fills the room.")
    slow_print("Your terminal blinks with an urgent message from Overseer Klein.")

    choices = [
        ("Read the message", "read"),
        ("Check the window", "window"),
        ("Get dressed and head to work", "go"),
    ]
    c = choice_prompt(choices)

    if c == 0:
        slow_print(f'\n{C.CYAN}"All personnel report to the main concourse immediately. There has been... a development." - Overseer Klein{C.RESET}')
        slow_print(f'{C.CYAN}"Do NOT be alarmed. Everything is under control."{C.RESET}')
        slow_print(f'{C.DIM}...That is not reassuring at all.{C.RESET}')
    elif c == 1:
        slow_print("The window shows the surface: gray sky, distant smoke on the horizon.")
        slow_print("A news feed hologram flickers: 'ROBECON: MASSIVE TROOP MOVEMENTS DETECTED.'")
        if player.can_do("Perception", 7):
            slow_print(f'{C.YELLOW}You notice: the dates on the news feeds are looping. They\'ve been showing the same reports for days.{C.RESET}')
            player.flags["suspicions"] = True
    else:
        slow_print("You pull on your Vault-Tec jumpsuit. The green and gray fabric feels too thin against the chill.")

    pause()

# ============================================================
# SCENE: CONCURSE
# ============================================================
def scene_concourse():
    header("THE MAIN CONCURSE")
    slow_print("Vault 37's main concourse is packed. Residents whisper in clusters.")
    slow_print("Vault-Tec security guards stand at attention, hands on their 10mm pistols.")
    slow_print("The massive Vault door looms overhead, hydraulic pistons creaking.")

    if player.flags.get("suspicions"):
        slow_print(f'{C.YELLOW}Something feels off. The security is too heavy for a routine alert.{C.RESET}')

    slow_print(f"\nOverseer Klein approaches. Tall, silver-haired, impossibly calm.")
    slow_print(f'\n{C.CYAN}"Citizen {player.name}, welcome. I need to inform you of... developments."{C.RESET}')

    if player.can_do("Charisma", 7):
        slow_print(f'{C.YELLOW}[CHARISMA CHECK PASSED] Klein hesitates, lowering his voice.{C.RESET}')
        slow_print(f'\n{C.CYAN}"Between us, I\'ve seen the files. Vault 37 isn\'t just a shelter. It\'s an experiment."{C.RESET}')
        slow_print(f'{C.CYAN}"And I think they know something\'s coming."{C.RESET}')
        player.karma += 10
        logger.karma(10, "Klein truth reveal")
        player.flags["knows_truth"] = True
        logger.flag_set("knows_truth", True)
        print(f'\n{C.GREEN}+10 Karma{C.RESET}')

    choices = [
        ("Ask what experiment", "ask"),
        ("Demand to see the files", "demand"),
        ("Pretend to be reassured", "comply"),
    ]
    if not player.can_do("Charisma", 7):
        choices.append(("Stay silent and wait", "wait"))

    c = choice_prompt(choices)

    if c == 0:
        slow_print(f'{C.CYAN}"Vault-Tec designed each vault with... special conditions. Some to test survival. Some to test obedience."{C.RESET}')
        slow_print(f'{C.CYAN}Ours? I haven\'t found out yet. But I intend to."{C.RESET}')
    elif c == 1:
        if player.can_do("Intelligence", 6):
            slow_print("\nKlein looks around, then hands you a data chip.")
            slow_print(f"{C.CYAN}Vault 37 parameters: Psychological pressure study. Maximum occupancy exceeded by 150%. No external rescue planned.{C.RESET}")
            slow_print(f"\n{C.RED}Your hands shake. No rescue.{C.RESET}")
            player.flags["has_chip"] = True
        else:
            slow_print("\nKlein shakes his head.")
            slow_print(f'{C.CYAN}"I\'d like to, citizen. But it\'s... not appropriate during a state of emergency."{C.RESET}')
    elif c == 2:
        slow_print(f'{C.CYAN}"Good. Trust in Vault-Tec, citizen. Everything will be fine."{C.RESET}')
        player.karma -= 5
    else:
        slow_print("\nYou say nothing. Klein reads your silence.")
        slow_print(f'{C.CYAN}"I understand. Go about your duties until further notice."{C.RESET}')

    pause()

# ============================================================
# SCENE: ENCOUNTER
# ============================================================
def scene_encounter():
    header("THE LOWER TUNNELS")
    slow_print("You descend into the maintenance tunnels beneath Vault 37.")
    slow_print("The fluorescent lights flicker. The air tastes metallic.")
    slow_print("You've heard rumors: unauthorized personnel have been spotted here.")

    roll = random.randint(1, 10)

    if roll <= 3:
        # Meet Sammy
        slow_print("\nSomeone ahead - a female voice arguing softly with a terminal.")
        slow_print("A woman in a Vault technician's uniform looks up. It's Sammy Alvarez.")
        slow_print(f'{C.CYAN}"Hey! I thought you\'d show. I\'ve been trying to crack the security logs and I need help."{C.RESET}')
        slow_print(f'{C.CYAN}"The vault\'s occupancy numbers are wrong. There are{C.YELLOW} two hundred{C.CYAN}{C.RESET}')
        slow_print(f'{C.CYAN}more people here than the manifest says. Locked in Sector D, below us."{C.RESET}')

        if player.can_do("Intelligence", 6):
            slow_print(f'{C.YELLOW}[INTELLIGENCE CHECK PASSED] You notice her terminal has a backdoor exploit.{C.RESET}')
            slow_print("You help her break through the encryption.")
            slow_print(f"{C.CYAN}Sector D manifest: Civilian detainees. Source: RobCo Industries. Authorization: CLASSIFIED.{C.RESET}")
            player.flags["sector_d"] = True
        logger.flag_set("sector_d", True)

        slow_print(f'{C.CYAN}"I could use someone smart around. You in?"{C.RESET}')

        choices = [
            ("Join with Sammy", "join_sammy"),
            ("Decline politely", "decline"),
            ("Ask about the black suit man", "ask_suit"),
        ]
        c = choice_prompt(choices)

        if c == 0:
            if not player.companion:
                player.companion = "sammy"
                logger.flag_set("companion", "sammy")
                slow_print(f'\n{C.GREEN}Sammy joins your party!{C.RESET}')
                player.karma += 5
            else:
                slow_print("\nSammy gives you a sympathetic nod. \"Thanks anyway.\"")
        elif c == 2:
            slow_print(f'{C.CYAN}"The black suit? He shows up every midnight. Bypasses all biometric scanners."{C.RESET}')
            slow_print(f'{C.CYAN}"Goes straight to the overseer\'s office. I\'ve been tracking him."{C.RESET}')
            slow_print(f'{C.CYAN}"His name... well, I found this on a classified doc."{C.RESET}')
            if player.can_do("Perception", 5):
                slow_print(f'{C.YELLOW}You see the document corner: "Project Purity - Division 13 - Dr. Ingram"{C.RESET}')
                player.flags["ingram"] = True
            else:
                slow_print(f'{C.DIM}The name is redacted, but it feels important.{C.RESET}')

    elif roll <= 7:
        # Combat encounter
        slow_print("\nA figure steps from the shadows - a Steel Dawn raider, armed and dangerous.")
        slow_print(f'{C.RED}"This tunnel\'s under our control now. Drop your stuff and maybe I let you walk."{C.RESET}')

        choices = [
            ("Fight the raider", "fight"),
            ("Try to talk him down", "talk"),
            ("Run!", "run"),
        ]
        c = choice_prompt(choices)

        if c == 0:
            result = combat(player, "raider")
            if result == "dead":
                return "death"
            elif result == "fled":
                slow_print("\nYou scramble back through the tunnels, heart pounding.")
            else:
                slow_print(f"\n{C.GREEN}The raider falls!{C.RESET}")
                for drop in ENEMIES["raider"]["drops"]:
                    give_item(player, drop)
                if player.add_xp(ENEMIES["raider"]["xp"]):
                    print(f"\n{C.GREEN}{C.BOLD}*** LEVEL UP! You are now level {player.level}! ***{C.RESET}")
        elif c == 1:
            if player.can_do("Charisma", 7):
                slow_print('\n"You\'re one of us. The vault needs all the hands it can get."')
                slow_print(f'{C.YELLOW}The raider hesitates... then lowers his weapon.{C.RESET}')
                slow_print(f'{C.CYAN}"...Vault-Tec still hiring?"{C.RESET}')
                player.karma += 15
            else:
                slow_print("The raider doesn't care about your words.")
                slow_print(f'{C.RED}"Nice speech. Now shut up and comply."{C.RESET}')
                result = combat(player, "raider")
                if result == "dead":
                    return "death"
                elif result == "fled":
                    pass
                else:
                    for drop in ENEMIES["raider"]["drops"]:
                        give_item(player, drop)
                    if player.add_xp(ENEMIES["raider"]["xp"]):
                        print(f"\n{C.GREEN}{C.BOLD}*** LEVEL UP! You are now level {player.level}! ***{C.RESET}")
        else:
            if random.randint(1, 10) <= player.spec["Agility"]:
                slow_print("You sprint past him, lungs burning.")
            else:
                slow_print("He catches up fast.")
                result = combat(player, "raider")
                if result == "dead":
                    return "death"
                elif result == "fled":
                    pass
                else:
                    for drop in ENEMIES["raider"]["drops"]:
                        give_item(player, drop)
                    if player.add_xp(ENEMIES["raider"]["xp"]):
                        print(f"\n{C.GREEN}{C.BOLD}*** LEVEL UP! You are now level {player.level}! ***{C.RESET}")

    else:
        # Find Tinker Tom
        slow_print("\nYou find a makeshift workshop. Schematics cover every surface.")
        slow_print("An older man with grease-stained hands looks up from a workbench.")
        slow_print(f'{C.CYAN}"Another wanderer in the tunnels. I\'m Tinker Tom."{C.RESET}')
        slow_print(f'{C.CYAN}"This vault is a pressure cooker. They\'re overcrowding it on purpose."{C.RESET}')
        slow_print(f'{C.CYAN}"Watching how people react when the bombs fall and the door seals."{C.RESET}')

        choices = [
            ("Join with Tinker Tom", "join_tom"),
            ("Ask him to build you something", "build"),
            ("This sounds crazy - leave", "leave"),
        ]
        c = choice_prompt(choices)

        if c == 0:
            if not player.companion:
                player.companion = "tinker"
                slow_print(f'\n{C.GREEN}Tinker Tom joins your quest!{C.RESET}')
                player.karma += 5
                player.flags["tom_joined"] = True
            else:
                slow_print("\nTom gives you a nod. \"Good luck, friend.\"")
        elif c == 1:
            if player.caps >= 100:
                slow_print("\nTom grins and starts working. An hour later...")
                player.equipment["weapon"] = WEAPONS["10mm_pistol"]
                slow_print(f'{C.YELLOW}He hands you a modified 10mm pistol. "Won\'t break."{C.RESET}')
                player.caps -= 100
            else:
                slow_print(f'{C.CYAN}"I\'d love to, but I need materials. Come back when you\'ve got caps."{C.RESET}')
        else:
            slow_print(f'{C.CYAN}"Crazy? Wait until October. You\'ll see."{C.RESET}')

    pause()

# ============================================================
# SCENE: SURFACE
# ============================================================
def scene_surface():
    header("THE SURFACE - AUGUST 28, 2077")
    slow_print("You activate the manual override and the service elevator creaks upward.")
    slow_print("For a moment, you're suspended between the vault and the world above.")
    slow_print("The door opens to a hellscape.")

    slow_print("\nThe sky is orange with smoke. The ruins of a suburban neighborhood stretch")
    slow_print("in every direction. Burnt-out cars line cracked highways.")
    slow_print("A holographic news tower flickers: 'ROBECON: WATER RIGHTS CONFLICT...'")
    slow_print("'ROBECON UPDATE: Timeline to full-scale conflict: 57 days.'")
    slow_print("57 days. Then the bombs fall.")

    choices = [
        ("Search the ruined neighborhood", "search"),
        ("Investigate the RobCo facility across the road", "robco"),
        ("Head to the military checkpoint on the highway", "military"),
        ("Return to the vault immediately", "return"),
    ]
    c = choice_prompt(choices)

    if c == 0:
        slow_print("\nYou move through the rubble. A house has a working water purifier.")
        slow_print("Loot: You find supplies and a worn leather jacket.")
        give_item(player, "leather_jacket")
        player.caps += 75
        slow_print("+75 caps from scrap trading.")
        if player.can_do("Perception", 6):
            slow_print(f"\n{C.YELLOW}You notice: the water supply is contaminated. Chemical signatures.{C.RESET}")
            slow_print(f"{C.YELLOW}Someone has been poisoning the reservoir feeding into this area.{C.RESET}")
            player.flags["poison_water"] = True
        logger.flag_set("poison_water", True)

    elif c == 1:
        slow_print("\nRobCo Industries facility. Half the buildings are intact.")
        slow_print("Security bots patrol the perimeter.")
        choices2 = [
            ("Infiltrate and search for data", "infiltrate"),
            ("Steal weapons from the armory", "steal"),
            ("Retreat before the bots notice", "retreat"),
        ]
        c2 = choice_prompt(choices2)

        if c2 == 0:
            if player.can_do("Intelligence", 7):
                slow_print("\nYou bypass the security mainframe. The data is horrifying.")
                slow_print(f'{C.CYAN}"Vault-Tec Experiment 37: Social dynamics under extreme duress."{C.RESET}')
                slow_print(f'{C.CYAN}Variable: Resource scarcity. Control group: Sector F (deprived)."{C.RESET}')
                slow_print(f'{C.CYAN}Expected duration: 200 years. External intervention: NONE."{C.RESET}')
                slow_print(f'\n{C.RED}No intervention. Ever. They plan to abandon this vault forever.{C.RESET}')
                player.flags["experiment_truth"] = True
                player.karma += 20
            else:
                slow_print("The encryption is too complex. You find nothing usable.")
            slow_print("\nA security bot detects your presence!")
            result = combat(player, "robot_sec")
            if result == "dead":
                return "death"
            elif result == "fled":
                slow_print("You escape back to the vault, mind reeling.")
            else:
                for drop in ENEMIES["robot_sec"]["drops"]:
                    give_item(player, drop)
                if player.add_xp(ENEMIES["robot_sec"]["xp"]):
                    print(f"\n{C.GREEN}{C.BOLD}*** LEVEL UP! You are now level {player.level}! ***{C.RESET}")
        elif c2 == 1:
            slow_print("You risk it and find crates of military surplus.")
            give_item(player, "10mm_pistol")
            player.caps += 150
            slow_print("\nA bot spots you!")
            result = combat(player, "robot_sec")
            if result == "dead":
                return "death"
            elif result == "fled":
                slow_print("You barely make it out with the loot.")
            else:
                if player.add_xp(ENEMIES["robot_sec"]["xp"]):
                    print(f"\n{C.GREEN}{C.BOLD}*** LEVEL UP! You are now level {player.level}! ***{C.RESET}")
        else:
            slow_print("You slip back before triggering the alarm.")

    elif c == 2:
        slow_print("\nThe checkpoint is run by desperate soldiers in worn armor.")
        slow_print("Barbed wire, sandbags, nervous troops with rifles.")
        slow_print(f'{C.CYAN}"Vault dwellers? You people know something, don\'t you?{C.RESET}')
        slow_print(f'{C.CYAN}The generals won\'t say anything but the sky\'s full of missiles."{C.RESET}')

        choices2 = [
            ("Tell them the truth about the vault experiment", "truth"),
            ("Help them defend the checkpoint", "help"),
            ("Take their military surplus", "take"),
        ]
        c2 = choice_prompt(choices2)

        if c2 == 0:
            slow_print("The soldiers stare at you in disbelief.")
            slow_print(f'{C.CYAN}"You\'re telling me even the shelters are rigged?{C.RESET}')
            slow_print(f'{C.CYAN}Then there\'s no hope."{C.RESET}')
            slow_print("One soldier hands you his combat armor and walks away into the smoke.")
            give_item(player, "marines_combat_armor")
            player.karma += 25
            player.flags["soldier_warning"] = True
        elif c2 == 1:
            slow_print("You help fortify their position. Hours pass.")
            slow_print("Raiders attack from the hills!")
            slow_print("\nWave 1: Biker gang!")
            result = combat(player, "biker")
            if result == "dead":
                return "death"
            elif result == "fled":
                slow_print("The soldiers hold the line without you.")
            else:
                for drop in ENEMIES["biker"]["drops"]:
                    give_item(player, drop)
                if player.add_xp(ENEMIES["biker"]["xp"]):
                    print(f"\n{C.GREEN}{C.BOLD}*** LEVEL UP! You are now level {player.level}! ***{C.RESET}")
            slow_print("\nThe soldiers are grateful. They give you real armor.")
            give_item(player, "marines_combat_armor")
            player.karma += 20
        else:
            slow_print("You raid the checkpoint while the guards are distracted.")
            give_item(player, "marines_combat_armor")
            player.karma -= 30
            slow_print(f'{C.RED}The soldiers will remember this.{C.RESET}')

    else:
        slow_print("You return to the vault's surface entrance.")

    pause()

# ============================================================
# SCENE: SECTOR D
# ============================================================
def scene_sector_d():
    header("SECTOR D - THE SECRET")
    slow_print("Located behind a reinforced blast door with biometric locks:")
    slow_print("two hundred extra people, crammed into spaces designed for families.")
    slow_print("They don't know they're the experiment.")

    slow_print('\nA child presses against the door. "Are you going to let us out?"')
    slow_print("Her eyes hold something no child should carry: the weight of being lied to.")

    if not player.flags.get("sector_d") and not player.flags.get("knows_truth"):
        slow_print("\nYou don't have enough information to access this area.")
        slow_print("Something tells you it's locked for a reason.")
        pause()
        return
    player.flags["sector_d"] = True

    choices = [
        ("Hack the door and free them", "free"),
        ("Report this to Overseer Klein", "report"),
        ("Use them as leverage against Vault-Tec", "leverage"),
    ]
    c = choice_prompt(choices)

    if c == 0:
        slow_print("\nYour hands tremble as you input the override codes.")
        slow_print("The door hisses open. Light floods the cramped corridor.")
        if player.companion == "sammy":
            slow_print(f'{C.PURPLE}Sammy is crying. "I can\'t believe they did this."{C.RESET}')
        slow_print("\nPeople pour out - gaunt, tired, but alive.")
        slow_print("They look at you like you're something they haven't seen in months: hope.")
        slow_print("\nBut the alarm blares. Security is coming.")
        slow_print("\nVault Security Enforcer arrives with backup!")
        result = combat(player, "protector")
        if result == "dead":
            return "death"
        elif result == "fled":
            slow_print("The freed residents hide in the tunnels. Security doesn't find them.")
            player.karma += 30
        else:
            slow_print("\nWith the enforcer neutralized, the residents scatter to safety.")
            for drop in ENEMIES["protector"]["drops"]:
                give_item(player, drop)
            if player.add_xp(ENEMIES["protector"]["xp"]):
                print(f"\n{C.GREEN}{C.BOLD}*** LEVEL UP! You are now level {player.level}! ***{C.RESET}")
            player.karma += 40
            player.flags["freed_them"] = True

    elif c == 1:
        slow_print("\nKlein listens in silence. When he speaks, his voice is hollow.")
        slow_print(f'{C.CYAN}"I know. I\'ve known for months. But if we release them, they\'ll send more security."{C.RESET}')
        slow_print(f'{C.CYAN}The vault could be shut down. Everyone dies."{C.RESET}')
        slow_print(f'{C.CYAN}"Sometimes the smaller evil... is the only choice."{C.RESET}')
        player.karma -= 10
        player.flags["reported_sector_d"] = True

    else:
        slow_print("\nYou threaten to expose the experiment unless Vault-Tec gives you")
        slow_print("privileged access and resources. Klein's face is unreadable.")
        slow_print(f'{C.CYAN}"An interesting proposition, citizen. I\'ll consider it."{C.RESET}')
        player.karma -= 25
        player.caps += 500
        player.flags["blackmailed"] = True

    pause()

# ============================================================
# SCENE: INGRAM
# ============================================================
def scene_ingram():
    header("THE BLACK SUIT - DR. INGRAM")
    slow_print("You follow the man in the black suit through hidden passages.")
    slow_print("He leads you to a sub-level that doesn't exist on any blueprint.")
    slow_print("Here: prototype weapons, mutagenic formulas, and a terminal networked to the surface.")

    slow_print('\nA man turns around. Dr. Emil Ingram, mid-50s, glasses, tired eyes.')
    slow_print(f'{C.CYAN}"You\'re either very brave or very stupid, citizen. Probably both."{C.RESET}')
    slow_print(f'{C.CYAN}"I used to work on Project Purity - the water purifier."{C.RESET}')
    slow_print(f'{C.CYAN}"But the government weaponized it. Now they control the water."{C.RESET}')
    slow_print(f'{C.CYAN}And when the bombs fall, they fall on everyone who questions."{C.RESET}')

    if player.can_do("Intelligence", 8):
        slow_print(f'{C.YELLOW}[INTELLIGENCE] You recognize Project Purity - the same project the Institute would use decades later.{C.RESET}')
        slow_print(f'{C.YELLOW}To control Boston\'s water supply.{C.RESET}')
        player.flags["purity_foreknowledge"] = True

    choices = [
        ("Convince Ingram to help you expose everything", "convince"),
        ("Demand Ingram disarm the vault's weapon system", "demand"),
        ("Take what you need and leave", "take"),
    ]
    c = choice_prompt(choices)

    if c == 0:
        if player.can_do("Charisma", 6) or player.karma > 20:
            slow_print('\nIngram studies you. "You\'re one of the few who might stand a chance."')
            slow_print(f'{C.CYAN}"Here. I\'ve been working on a way to hijack the vault\'s communication array."{C.RESET}')
            slow_print(f'{C.CYAN}If it works, everyone will hear the truth."{C.RESET}')
            if not player.companion:
                player.companion = "tinker"
            player.flags["ingram_alliance"] = True
            player.karma += 15
            slow_print(f'{C.CYAN}"And this... just in case." Ingram hands you a Fat Man launcher.{C.RESET}')
            player.equipment["weapon"] = WEAPONS["Fat_Man"]
        else:
            slow_print('\nIngram shakes his head. "I can\'t trust you yet. Prove yourself first."')
            slow_print("He disappears into the lab.")
    elif c == 1:
        slow_print('\nIngram looks pained. "I can\'t. If I disarm it, Vault-Tec will know')
        slow_print("immediately. And they have ways of persuading.")
        slow_print(f'{C.CYAN}"But I\'ll give you this." He hands you a data drive.{C.RESET}')
        slow_print(f'{C.CYAN}"It contains the launch codes for this vault\'s defense system."{C.RESET}')
        player.flags["has_codes"] = True
        player.karma += 10
    else:
        slow_print("\nYou search the lab frantically, grabbing what you can.")
        slow_print("Ingram watches, shaking his head.")
        slow_print(f'{C.CYAN}"I suppose that\'s what I would do too. Good luck, citizen."{C.RESET}')
        player.caps += 300
        player.karma -= 15
        slow_print("\nA lab accident has created an early super mutant in the adjacent chamber!")
        result = combat(player, "super_mutant")
        if result == "dead":
            return "death"
        elif result == "fled":
            slow_print("The super mutant doesn't pursue. It just stands there, confused.")
        else:
            for drop in ENEMIES["super_mutant"]["drops"]:
                give_item(player, drop)
            if player.add_xp(ENEMIES["super_mutant"]["xp"]):
                print(f"\n{C.GREEN}{C.BOLD}*** LEVEL UP! You are now level {player.level}! ***{C.RESET}")

    pause()

# ============================================================
# SCENE: NIGHTFALL
# ============================================================
def scene_night():
    header("NIGHTFALL - AUGUST 29, 2077")
    slow_print("Night falls. The vault's artificial lighting mimics a dim sunset.")
    slow_print("Metal groaning. Alarms cycling in sectors that should be empty.")
    slow_print("And the distant, impossible sound of sirens from the surface.")

    slow_print("\nYour terminal alerts you: 'EMERGENCY BROADCAST - SURFACE'")
    slow_print("The voice on the other end is static-drenched:")
    slow_print(f'{C.CYAN}"...confirmed launch codes activated... ICBMs... all silos..."{C.RESET}')
    slow_print(f'{C.CYAN}estimated impact in 48 hours... get to your shelters..."{C.RESET}')
    slow_print(f'{C.CYAN}repeat... this is not a drill..."{C.RESET}')

    slow_print("\nThe bombs are coming. In 48 hours, everything changes.")

    if player.companion:
        cn = COMPANIONS[player.companion]["name"]
        slow_print(f'\n{C.PURPLE}{cn} looks at you. "It\'s time to make a decision, {player.name}."{C.RESET}')

    choices = [
        ("Find Overseer Klein and demand answers", "klein"),
        ("Gather supplies and prepare for the war", "prepare"),
        ("Infiltrate the overseer's office with the evidence", "infiltrate"),
    ]
    if player.flags.get("sector_d"):
        choices.append(("Go back for the hidden sector residents", "sector_d_again"))
    if player.flags.get("ingram_alliance") or player.flags.get("ingram"):
        choices.append(("Meet with Dr. Ingram one final time", "ingram_final"))

    c = choice_prompt(choices)

    if c == 0:
        slow_print("\nKlein is waiting in his office, a bottle of pre-war whiskey on his desk.")
        slow_print(f'{C.CYAN}"You heard it then. I\'m not going to pretend anymore."{C.RESET}')
        slow_print(f'{C.CYAN}"Vault 37 will seal on schedule. Some of you will survive.{C.RESET}')
        slow_print(f'{C.CYAN}Some won\'t. That\'s the experiment."{C.RESET}')
        slow_print(f'{C.CYAN}"But I have a way out. A single surface elevator that bypasses the lockdown protocol."{C.RESET}')
        slow_print(f'{C.CYAN}It can take... ten people. Maybe."{C.RESET}')

        choices2 = [
            ("Help him get more people out", "hero"),
            ("Take the spot for yourself", "coward"),
            ("Refuse - stay and fight for everyone", "fight"),
        ]
        c2 = choice_prompt(choices2)

        if c2 == 0:
            player.flags["escape_plan"] = True
            logger.flag_set("escape_plan", True)
            player.karma += 15
            logger.karma(15, "escape plan with Klein")
            slow_print("\nTogether, you plan to modify the elevator for maximum capacity.")
        elif c2 == 1:
            player.karma -= 20
            logger.karma(-20, "took spot for self")
            slow_print('\nKlein nods. "You\'re already in the list. Good luck."')
        else:
            player.karma += 30
            slow_print('\nKlein raises an eyebrow. "Fighting the system?"')
            slow_print('That\'s either courageous or suicidal."')
            player.flags["stay_and_fight"] = True
            logger.flag_set("stay_and_fight", True)
            logger.karma(30, "staying to fight")

    elif c == 1:
        slow_print("\nYou spend the night gathering supplies: stimpaks, ammunition, food.")
        player.hp = player.max_hp
        player.caps += 100
        slow_print("Your inventory is stocked. You're ready for whatever comes.")

    elif c == 2:
        if player.flags.get("experiment_truth") or player.flags.get("has_chip"):
            slow_print("\nWith the evidence you've gathered, you break into the overseer's office.")
            slow_print("You plug the data chip into the vault's broadcast system.")
            slow_print("\nNow every terminal in the vault displays the truth:")
            slow_print(f'{C.CYAN}VAULT 37 EXPERIMENT: SOCIALIZATION UNDER DURESS.{C.RESET}')
            slow_print(f'{C.CYAN}NO EXTERNAL RESCUE. DURATION: 200 YEARS. INTERVENTION: NONE.{C.RESET}')
            slow_print("\nChaos. But also... determination. People won't let this happen.")
            player.flags["truth_broadcast"] = True
            logger.flag_set("truth_broadcast", True)
            player.karma += 25
            logger.karma(25, "broadcasted truth")
        else:
            slow_print("Without evidence, your claims fall on deaf ears.")
            slow_print("But some people still believe you.")
    else:
        action = choices[c][1]
        if action == "sector_d_again":
            pass  # confirmed sector_d path
            slow_print("\nYou return to Sector D. The residents are already packed.")
            slow_print("Families huddle in the dark, praying you'll come back.")
            if player.flags.get("freed_them"):
                slow_print("\nThey're free. Now you need to get them out of the vault.")
                player.flags["ready_to_escape"] = True
                logger.flag_set("ready_to_escape", True)
            else:
                slow_print("\nYou open the door for good this time.")
                player.karma += 30
                logger.karma(30, "freed Sector D")
                logger.karma(30, "freed Sector D")
                player.flags["freed_them"] = True
                logger.flag_set("freed_them", True)
        elif action == "ingram_final":
            slow_print("\nYou find Ingram in his lab, packing samples into a duffel bag.")
            slow_print(f'{C.CYAN}"48 hours, {player.name}. I\'ve built something.{C.RESET}')
            slow_print(f'{C.CYAN}It\'s not much, but it might help you survive what comes."{C.RESET}')
            slow_print("\nHe hands you a prototype water purifier badge.")
            slow_print(f'{C.YELLOW}Project Purity Badge - Grants access to safe water stations post-war.{C.RESET}')
            player.flags["purity_badge"] = True
            logger.flag_set("purity_badge", True)

    pause()

# ============================================================
# SCENE: THE WAR
# ============================================================
def scene_the_war():
    header("OCTOBER 23, 2077 - THE GREAT WAR")
    slow_print("It takes only twelve seconds.")

    slow_print("\nThe first alert is a blip on a sensor. Then another. Then the sky")
    slow_print("splits open with the streaks of incoming warheads. The Vault's door")
    slow_print("slams shut with a sound like the end of the world.")

    slow_print("\nInside, you hear screams. Through the ventilation, the smell of burning.")
    slow_print("Outside, civilization turns to ash in minutes.")

    slow_print("\nThe vault's intercom crackles:")
    slow_print(f'{C.CYAN}"Attention Vault 37 residents. Welcome to your new permanent residence.{C.RESET}')
    slow_print(f'{C.CYAN}Vault-Tec wishes you a pleasant stay."{C.RESET}')

    slow_print("\nPermanent. They mean permanent.")

    pause()

# ============================================================
# SCENE: FINAL CHOICE
# ============================================================
def scene_final_choice():
    header("THE MORNING AFTER - OCTOBER 24, 2077")
    slow_print("Dawn, if you can call it that. The vault's artificial light cycles")
    slow_print("through a simulated sunrise. People are waking up to a new world.")
    slow_print("A dead world, above ground.")

    slow_print(f"\nYou stand at the crossroads, {player.name}. The vault is sealed.")
    slow_print("Inside: safety, but at what cost?")
    slow_print("Outside: radiation, ruin, but freedom.")

    slow_print("\nYour karma has shaped who you are. Your choices have consequences.")
    slow_print(f"\n{C.CYAN}Current Karma: {player.karma}{C.RESET}")

    if player.flags.get("truth_broadcast"):
        slow_print("\nThe vault residents know the truth. They're looking to you.")
    if player.flags.get("freed_them"):
        slow_print("\nThe Sector D residents huddle near you. They trust you with their lives.")
    if player.companion:
        cn = COMPANIONS[player.companion]["name"]
        slow_print(f"\n{cn} stands by your side.")

    c = choice_prompt([
        ("Take control of the vault - become the new leader", "leader"),
        ("Help the residents escape the vault on foot", "escape_vault"),
        ("Go to the surface alone", "surface"),
        ("Broadcast a signal to find other survivors", "signal"),
    ])
    return c

# ============================================================
# ENDINGS
# ============================================================
def ending(c):
    cls()

    if c == 0:
        header("ENDING: THE OVERSEER")
        slow_print("You step up. The vault needs leadership, not panic.")
        slow_print("With your experience and the alliances you forged, you organize")
        slow_print("the residents into a functioning community.")
        if player.flags.get("truth_broadcast"):
            slow_print("Armed with the truth about Vault-Tec's experiments, you")
            slow_print("overthrow the old guard. Klein watches from his office, silent.")
        if player.companion:
            cn = COMPANIONS[player.companion]["name"]
            slow_print(f'\n{C.PURPLE}{cn} becomes your second-in-command.{C.RESET}')
            slow_print("Together, you build something Vault-Tec never intended.")
        slow_print(f'\n\n{C.CYAN}{C.BOLD}THE OVERSEER{C.RESET}')
        slow_print("Years later, Vault 37 becomes a beacon in the wasteland.")
        slow_print("Their Overseer is spoken of in awe - the one who took control")
        slow_print("when the world ended and turned a prison into a home.")
        slow_print("When the vault finally opens, its people are ready.")
        slow_print(f'{C.YELLOW}Karma: {player.karma}  |  Level: {player.level}{C.RESET}')

    elif c == 1:
        header("ENDING: THE LIBERATOR")
        slow_print("You find the maintenance tunnel that leads outside.")
        slow_print("With your knowledge, you locate a forgotten exit.")
        if player.flags.get("freed_them") or player.flags.get("sector_d"):
            slow_print("The Sector D residents come with you. Your group of")
            slow_print("survivors forms a caravan into the unknown.")
        slow_print("\nThe radiation is intense, but the purifiers hold.")
        slow_print("Outside, the wasteland stretches in all directions.")
        slow_print(f'\n\n{C.GREEN}{C.BOLD}THE LIBERATOR{C.RESET}')
        slow_print("You chose freedom over safety. On the surface, your caravan")
        slow_print("becomes a legend - a traveling community that shares")
        slow_print("the truth about the old world and builds a new one.")
        slow_print("Raiders fear you. Survivors follow you.")
        slow_print(f'{C.YELLOW}Karma: {player.karma}  |  Level: {player.level}{C.RESET}')

    elif c == 2:
        header("ENDING: THE WANDERER")
        slow_print("You climb the service elevator one last time. The door opens")
        slow_print("to a world of fire and ash. You step out into the wasteland alone.")
        if player.equipment["weapon"]:
            slow_print(f"You grip your {player.equipment['weapon']['name']}.")
        if player.equipment["armor"]:
            slow_print(f"Your {player.equipment['armor']['name']} offers some protection.")
        slow_print(f'\n{C.CYAN}Gecko approaching. Water scarcity imminent.{C.RESET}')
        slow_print(f'\n\n{C.PURPLE}{C.BOLD}THE WANDERER{C.RESET}')
        slow_print("You became what the wasteland creates: a solitary survivor,")
        slow_print("hardened by loss, driven by purpose. You wander the ruins,")
        slow_print("helping when you can, surviving always.")
        slow_print("One day, you'll find a settlement. Or maybe you won't.")
        slow_print("But you'll keep walking. Because stopping means forgetting.")
        slow_print(f'{C.YELLOW}Karma: {player.karma}  |  Level: {player.level}{C.RESET}')

    else:
        header("ENDING: THE SIGNAL")
        slow_print("You rig the vault's communication array, redirecting all")
        slow_print("remaining power to the broadcast system. A signal pulses into the void:")
        slow_print(f'{C.CYAN}"This is Vault 37. If anyone can hear this, we are alive.{C.RESET}')
        slow_print(f'{C.CYAN}We have the truth about what happened. We have survivors.{C.RESET}')
        slow_print(f'{C.CYAN}Coordinates transmitted. Come find us. - 2077"{C.RESET}')
        slow_print("\nDays pass. Then, a response from somewhere in the ruins:")
        slow_print(f'{C.CYAN}"Vault 13 responding. We copy your transmission.{C.RESET}')
        slow_print(f'{C.CYAN}Hold on. We\'re coming."{C.RESET}')
        slow_print(f'\n\n{C.CYAN}{C.BOLD}THE SIGNAL{C.RESET}')
        slow_print("Your broadcast reaches other vaults, other survivors.")
        slow_print("Vault 13 answers the call. And slowly, a network forms -")
        slow_print("vaults and surface communities connecting in the aftermath.")
        slow_print("You planted the seed of a new civilization, built not on")
        slow_print("secrets and experiments, but on shared truth and cooperation.")
        slow_print(f'{C.YELLOW}Karma: {player.karma}  |  Level: {player.level}{C.RESET}')

# ============================================================
# DEATH
# ============================================================
def death_screen():
    cls()
    print(f"""{C.RED}{C.BOLD}
  YOU DIED

  The wasteland claims another soul.
  Your story ends here, {player.name}.

  Level: {player.level}  |  Karma: {player.karma}
{C.RESET}

{C.DIM}  "The Great War didn't kill you. Something else did."
{C.RESET}
    """)
    pause()

# ============================================================
# MAIN GAME LOOP
# ============================================================
def main():
    global player
    player = Player()
    title_screen()
    logger.event("init", "Game started")
    character_creation()
    logger.event("creation", f"Character: {player.name}")

    cls()
    header(f"YOUR QUEST BEGINS, {player.name.upper()}")
    slow_print("The world is about to end. What will you do before it does?")
    pause()

    scenes = [
        ("scene_wake_up",     scene_wake_up),
        ("scene_concourse",   scene_concourse),
        ("scene_encounter",   scene_encounter),
        ("scene_surface",     scene_surface),
        ("scene_sector_d",    scene_sector_d),
        ("scene_ingram",      scene_ingram),
        ("scene_night",       scene_night),
        ("scene_the_war",     scene_the_war),
    ]

    for scene_name, scene_func in scenes:
        cls()
        logger.scene_enter(scene_name)
        try:
            result = scene_func()
            logger.scene_exit(scene_name)
            if result == "death":
                logger.event("death", f"Player died in {scene_name}")
                logger.dump_snapshot(player)
                death_screen()
                try:
                    r = input(f"\n{C.BOLD}Try again? (y/n): {C.RESET}")
                except (EOFError, KeyboardInterrupt):
                    print(f"\n{C.DIM}Goodbye, {player.name}. The wasteland awaits...{C.RESET}\n")
                    return
                if r.lower() == "y":
                    main()
                    return
                else:
                    print(f"\n{C.DIM}Goodbye, {player.name}. The wasteland awaits...{C.RESET}\n")
                    return
        except KeyboardInterrupt:
            print(f"\n\n{C.RED}{C.BOLD}GAME INTERRUPTED{C.RESET}")
            logger.event("crash", f"KeyboardInterrupt in {scene_name}")
            logger.dump_snapshot(player, exc="KeyboardInterrupt")
            return
        except Exception as e:
            logger.event("crash", f"{type(e).__name__} in {scene_name}: {e}")
            logger.dump_snapshot(player, exc=e)
            exc_text = traceback.format_exc()
            print(f"\n{C.RED}{C.BOLD}CRASH in {scene_name}: {type(e).__name__}{C.RESET}")
            print(f"{C.RED}{e}{C.RESET}")
            print(f"\n{C.DIM}Full debug log written to ~/.local/share/fallout_prequel/{C.RESET}")
            print(f"{C.DIM}{exc_text}{C.RESET}")
            return

    # Final choice
    cls()
    logger.scene_enter("scene_final_choice")
    try:
        choice = scene_final_choice()
    except (KeyboardInterrupt, EOFError):
        logger.event("crash", "EOF/Interrupt at final choice")
        print(f"\n\n{C.RED}GAME INTERRUPTED{C.RESET}")
        logger.dump_snapshot(player)
        return

    logger.scene_exit("scene_final_choice")
    ending(choice)

    print(f"\n\n{C.DIM}{'='*50}{C.RESET}")
    print(f"{C.DIM}FINAL STATISTICS{C.RESET}")
    print(f"{C.DIM}{'='*50}{C.RESET}\n")
    print(f"  Name:     {player.name}")
    print(f"  Level:    {player.level}")
    print(f"  Karma:    {player.karma}")
    print(f"  XP:       {player.xp}")
    print(f"  Caps:     {player.caps}")
    print(f"  HP:       {player.hp}/{player.max_hp}")
    print(f"  Traits:   {', '.join(player.traits) if player.traits else 'None'}")
    if player.companion:
        print(f"  Companion: {COMPANIONS[player.companion]['name']}")
    print(f"\n  S.P.E.C.I.A.L.:")
    for stat, val in player.spec.items():
        print(f"    {stat:13s} {val}")
    print(f"\n{C.DIM}Thank you for playing FALLOUT: The Last Day Before{C.RESET}")
    print(f"{C.DIM}May you thrive in the wasteland.{C.RESET}\n")

if __name__ == "__main__":
    main()
