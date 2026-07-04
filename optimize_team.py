#!/usr/bin/env python3
"""
Sporza Wielermanager Tour de France 2026 — Echte data-driven analyse
Haalt rennersdata op van Pouletips, berekent value picks en optimaliseert de ploeg.
"""

import json
import re
import urllib.request
import urllib.error
import sys

# ===== FETCH DATA =====

def fetch_pouletips_data():
    """
    Haalt de rennersranglijst met prijzen en verwachte punten op van Pouletips.
    Slaat ruwe HTML op voor debugging.
    """
    url = "https://pouletips.nl/tour-de-france-2026/sporza/beste-renners/"
    print(f"📡 Ophalen data van {url}...", file=sys.stderr)

    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html',
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8')
    except Exception as e:
        print(f"❌ Fout bij ophalen: {e}", file=sys.stderr)
        print("⚠️  Fallback: gebruik lokale backup data", file=sys.stderr)
        return None

    # Save raw HTML for debugging
    with open("/tmp/pouletips_raw.html", "w") as f:
        f.write(html)

    return html


def parse_rider_data(html):
    """
    Parse de Pouletips HTML om renner data te extraheren.
    De pagina gebruikt een specifieke structuur:
    - list items met renner info
    - Format: "Rank Naam Team Prijs Punten"
    """
    if html is None:
        return []

    riders = []

    # Zoek naar de "Alle renners op verwachte punten" sectie
    # In de HTML zitten list-items met rennerinfo in divs/buttons
    # Patroon: Naam + ploeg + prijs(mln) + punten(getal)

    # Extract all text content between relevant markers
    sections = re.split(r'<h2[^>]*>', html)

    # Zoek de sectie "Alle renners op verwachte punten" of de hoofdlijst
    all_riders_section = ""
    for sec in sections:
        if "Alle renners" in sec or "optimale ploeg" in sec.lower():
            all_riders_section = sec
            break

    if not all_riders_section:
        # Fallback: hele HTML doorzoeken
        all_riders_section = html

    # Extract rider blocks - look for patterns like:
    # "Tadej Pogacar" followed by team code and price
    rider_blocks = re.findall(
        r'<li[^>]*>.*?'
        r'([A-Z][a-zéèëêëüöäàâç]+\s+(?:[A-Z][a-zéèëêëüöäàâç]*\.?\s*)*?)'  # Naam (bv. "Tadej Pogacar", "Van der Poel")
        r'.*?'
        r'([A-Z]{2,4}|[A-Z][a-z]+)'  # Team code (bv. UAD, TVL, APT)
        r'.*?'
        r'(\d+[.,]\d*)\s*mln'  # Prijs (bv. "12,0 mln")
        r'.*?',
        all_riders_section,
        re.DOTALL | re.IGNORECASE
    )

    # Alternative simpler approach: parse line by line
    lines = html.split('\n')
    current_name = None
    current_team = None
    current_price = None
    current_points = None
    current_jersey = None

    # Find the list of riders - look for the numbered list
    in_list = False
    for i, line in enumerate(lines):
        line_stripped = line.strip()

        # Check for rider start (number followed by name)
        name_match = re.match(r'^\s*(\d+)\s*$', line_stripped)
        if name_match:
            # Next lines should contain the name
            in_list = True
            continue

        if not in_list:
            continue

        # Look for rider name in the HTML
        name_tag = re.search(r'<a[^>]*>([^<]+)</a>', line_stripped)
        if name_tag and current_name is None:
            candidate = name_tag.group(1).strip()
            if len(candidate) > 3 and not candidate.startswith('http'):
                current_name = candidate
                continue

        # Look for team abbreviation (3-4 uppercase letters + full name)
        team_match = re.search(r'([A-Z]{2,4})([A-Z][a-z])', line_stripped)
        # This is getting complex. Let me try a different approach.

    # Much simpler: parse the JSON-like data embedded in the page
    # Look for each list item that has a price in millions
    print(f"📄 Pagina grootte: {len(html)} chars", file=sys.stderr)

    # Find rider cards by looking at the pattern:
    # Each rider appears in a <li> containing their name, price (X,X mln), and points (number)
    # The structure from the Aks tree showed: Name + Team + Price + Points

    # Regex approach: find all occurrences of prices and the context around them
    price_pattern = re.compile(
        r'([A-Z][a-zéèëêüöäàâç]+(?:[- ]+[A-Z][a-zéèëêüöäàâç.]+)*)'  # Name
        r'(?:.*?)'
        r'([A-Z]{3,4})'  # Team code
        r'(?:.*?)'
        r'(\d[.,]\d)\s*mln',  # Price
        re.DOTALL
    )

    # Try to extract from the JSON-style data blocks or script tags
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    for script in scripts:
        if 'riders' in script.lower() or 'data' in script.lower() or 'window' in script.lower():
            # Might contain JSON data
            pass

    print("⚠️  Geautomatiseerde parse gedeeltelijk — gebruik data-table extractie", file=sys.stderr)
    return None  # Will trigger fallback


def get_riders_from_table_data(html):
    """
    Extract rider data from the Pouletips page by finding list items
    that contain rider info in a structured format.
    """
    if html is None:
        return None

    riders = []

    # Find all list items (<li>) that contain a price in millions
    li_pattern = re.compile(r'<li[^>]*>(.*?)</li>', re.DOTALL)
    for li_match in li_pattern.finditer(html):
        li_content = li_match.group(1)

        # Check if this li contains a price (X,X mln)
        price_match = re.search(r'(\d+)[.,](\d)\s*mln', li_content)
        if not price_match:
            continue

        price = float(f"{price_match.group(1)}.{price_match.group(2)}")

        # Extract name - look for anchor tags with name
        name_match = re.search(r'<a[^>]*>([^<]+)</a>', li_content)
        if not name_match:
            continue
        name = name_match.group(1).strip()

        # Extract team code (3-4 uppercase letters)
        team_match = re.search(r'([A-Z]{3,4})\s*<', li_content)
        if not team_match:
            # Try to find team in text before another tag
            team_match = re.search(r'([A-Z]{3,4})\s', li_content)
        team = team_match.group(1) if team_match else "???"

        # Extract expected points (large number)
        points_match = re.search(r'>(\d{3,4})<', li_content)
        points = int(points_match.group(1)) if points_match else 0

        riders.append({
            'name': name,
            'team': team,
            'price': price,
            'expected_points': points
        })

    return riders


# ===== FALLBACK DATA =====
# Gebaseerd op pouletips.nl scrape van vandaag (laatst bijgewerkt: 2026-07-03)

FALLBACK_RIDERS = [
    {"name": "Tadej Pogacar", "team": "UAD", "price": 12.0, "expected_points": 1298, "type": "gc_climber", "jersey": "yellow_polka"},
    {"name": "Jonas Vingegaard", "team": "TVL", "price": 10.0, "expected_points": 624, "type": "gc_climber", "jersey": "yellow_polka"},
    {"name": "Jasper Philipsen", "team": "APT", "price": 9.0, "expected_points": 613, "type": "sprinter", "jersey": "green"},
    {"name": "Remco Evenepoel", "team": "RBH", "price": 9.0, "expected_points": 596, "type": "gc_climber", "jersey": "yellow_polka"},
    {"name": "Paul Seixas", "team": "DEC", "price": 8.0, "expected_points": 575, "type": "gc_young", "jersey": "white"},
    {"name": "Mads Pedersen", "team": "LTK", "price": 8.0, "expected_points": 525, "type": "sprinter", "jersey": "green"},
    {"name": "Tim Merlier", "team": "SOQ", "price": 9.0, "expected_points": 507, "type": "sprinter", "jersey": "green"},
    {"name": "Mathieu van der Poel", "team": "APT", "price": 8.0, "expected_points": 466, "type": "allrounder", "jersey": "green"},
    {"name": "Isaac Del Toro", "team": "UAD", "price": 7.0, "expected_points": 459, "type": "gc_young", "jersey": "white"},
    {"name": "Florian Lipowitz", "team": "RBH", "price": 8.0, "expected_points": 453, "type": "gc_young", "jersey": "white"},
    {"name": "Juan Ayuso", "team": "LTK", "price": 7.0, "expected_points": 436, "type": "gc_young", "jersey": "white"},
    {"name": "Arnaud De Lie", "team": "LTO", "price": 4.0, "expected_points": 408, "type": "sprinter", "jersey": "green"},
    {"name": "Biniam Girmay", "team": "NSN", "price": 5.0, "expected_points": 405, "type": "sprinter", "jersey": "green"},
    {"name": "Tom Pidcock", "team": "TQ3", "price": 6.0, "expected_points": 400, "type": "allrounder", "jersey": ""},
    {"name": "Adam Yates", "team": "UAD", "price": 5.0, "expected_points": 379, "type": "climber", "jersey": ""},
    {"name": "Fernando Gaviria", "team": "CJR", "price": 4.0, "expected_points": 348, "type": "sprinter", "jersey": ""},
    {"name": "Olav Kooij", "team": "DEC", "price": 7.0, "expected_points": 329, "type": "sprinter", "jersey": "green"},
    {"name": "Egan Bernal", "team": "IGD", "price": 5.0, "expected_points": 324, "type": "gc_climber", "jersey": ""},
    {"name": "Richard Carapaz", "team": "EFE", "price": 5.0, "expected_points": 324, "type": "gc_climber", "jersey": "polka"},
    {"name": "Dorian Godon", "team": "IGD", "price": 4.0, "expected_points": 298, "type": "allrounder", "jersey": ""},
    {"name": "Matteo Jorgenson", "team": "TVL", "price": 6.0, "expected_points": 290, "type": "allrounder", "jersey": ""},
    {"name": "Damiano Caruso", "team": "TBV", "price": 4.0, "expected_points": 272, "type": "climber", "jersey": ""},
    {"name": "Thymen Arensman", "team": "IGD", "price": 5.0, "expected_points": 268, "type": "gc_young", "jersey": ""},
    {"name": "Kevin Vauquelin", "team": "IGD", "price": 6.0, "expected_points": 265, "type": "allrounder", "jersey": ""},
    {"name": "Sepp Kuss", "team": "TVL", "price": 5.0, "expected_points": 260, "type": "climber", "jersey": ""},
    {"name": "Mattias Skjelmose", "team": "LTK", "price": 5.0, "expected_points": 250, "type": "gc_young", "jersey": ""},
    {"name": "Ben O'Connor", "team": "JAY", "price": 5.0, "expected_points": 238, "type": "gc_climber", "jersey": ""},
    {"name": "Jai Hindley", "team": "RBH", "price": 6.0, "expected_points": 232, "type": "gc_climber", "jersey": ""},
    {"name": "Antonio Tiberi", "team": "TBV", "price": 5.0, "expected_points": 221, "type": "gc_young", "jersey": ""},
    {"name": "Arvid de Kleijn", "team": "TUD", "price": 4.0, "expected_points": 202, "type": "sprinter", "jersey": ""},
    {"name": "Phil Bauhaus", "team": "TBV", "price": 4.0, "expected_points": 200, "type": "sprinter", "jersey": ""},
    {"name": "Milan Fretin", "team": "COF", "price": 4.0, "expected_points": 199, "type": "sprinter", "jersey": ""},
    {"name": "Brandon McNulty", "team": "UAD", "price": 4.0, "expected_points": 183, "type": "allrounder", "jersey": ""},
    {"name": "Pascal Ackermann", "team": "JAY", "price": 4.0, "expected_points": 178, "type": "sprinter", "jersey": ""},
    {"name": "Max Kanter", "team": "XAT", "price": 4.0, "expected_points": 177, "type": "sprinter", "jersey": ""},
    {"name": "Felix Grossschartner", "team": "UAD", "price": 3.0, "expected_points": 174, "type": "climber", "jersey": ""},
    {"name": "Cian Uijtdebroeks", "team": "MOV", "price": 5.0, "expected_points": 168, "type": "gc_young", "jersey": ""},
    {"name": "Tobias Johannessen", "team": "UXM", "price": 6.0, "expected_points": 161, "type": "gc_young", "jersey": ""},
    {"name": "Guillaume Martin", "team": "GFC", "price": 4.0, "expected_points": 159, "type": "climber", "jersey": ""},
    {"name": "Anthony Turgis", "team": "TEN", "price": 3.0, "expected_points": 156, "type": "allrounder", "jersey": ""},
    {"name": "Pavel Bittner", "team": "PIC", "price": 4.0, "expected_points": 156, "type": "sprinter", "jersey": ""},
    {"name": "Marc Hirschi", "team": "TUD", "price": 4.0, "expected_points": 153, "type": "allrounder", "jersey": ""},
    {"name": "George Bennett", "team": "NSN", "price": 3.0, "expected_points": 150, "type": "climber", "jersey": ""},
    {"name": "Lennert Van Eetvelt", "team": "LTO", "price": 4.0, "expected_points": 147, "type": "gc_young", "jersey": ""},
    {"name": "Lenny Martinez", "team": "TBV", "price": 5.0, "expected_points": 145, "type": "gc_young", "jersey": "polka"},
    {"name": "Jasper Stuyven", "team": "SOQ", "price": 4.0, "expected_points": 142, "type": "allrounder", "jersey": ""},
    {"name": "Nils Politt", "team": "UAD", "price": 3.0, "expected_points": 137, "type": "allrounder", "jersey": ""},
    {"name": "Romain Gregoire", "team": "GFC", "price": 5.0, "expected_points": 134, "type": "allrounder", "jersey": ""},
    {"name": "Cees Bol", "team": "DEC", "price": 3.0, "expected_points": 131, "type": "sprinter", "jersey": ""},
    {"name": "Michael Matthews", "team": "JAY", "price": 4.0, "expected_points": 129, "type": "sprinter", "jersey": ""},
    # Budget fillers (€2M)
    {"name": "Stefano Oldani", "team": "CJR", "price": 2.0, "expected_points": 0, "type": "filler", "jersey": ""},
    {"name": "Damien Howson", "team": "TQ3", "price": 2.0, "expected_points": 0, "type": "filler", "jersey": ""},
    {"name": "Bert Van Lerberghe", "team": "SOQ", "price": 2.0, "expected_points": 0, "type": "filler", "jersey": ""},
]

BUDGET = 100.0  # €100M
TEAM_SIZE = 16


# ===== OPTIMIZATION =====

def optimize_team(riders, budget=BUDGET, team_size=TEAM_SIZE):
    """
    Vind de optimale ploeg van team_size renners binnen budget.
    Gebruikt een variant op het knapzak-probleem met discrete prijzen.

    Omdat 16 uit ~50 renners kiezen met een budget constraint een
    NP-hard probleem is, gebruiken we een greedy benadering met
    value-for-money scoring die in de praktijk de optimale of
    zeer nabije-optimale oplossing vindt.
    """
    # Filter renners met prijs > 0
    candidates = [r for r in riders if r['price'] > 0]

    # Bereken value score per renner
    for r in candidates:
        if r['expected_points'] > 0 and r['price'] > 0:
            r['value_score'] = r['expected_points'] / r['price']
        else:
            r['value_score'] = 0

    # Sorteer op value_score (dalend)
    sorted_riders = sorted(candidates, key=lambda r: (-r['value_score'], -r['expected_points']))

    print(f"📊 Top 10 value picks (punten per €M):", file=sys.stderr)
    for r in sorted_riders[:10]:
        print(f"   {r['name']:<25s} €{r['price']:.0f}M ~{r['expected_points']:>4d}pt = {r['value_score']:.0f} pt/M€", file=sys.stderr)

    # === GREEDY OPTIMIZATION ===
    # Fase 1: Pak de beste value picks tot budget op is
    team = []
    remaining_budget = budget
    remaining_slots = team_size

    for r in sorted_riders:
        if remaining_slots <= 0:
            break
        if r['price'] <= remaining_budget:
            team.append(r)
            remaining_budget -= r['price']
            remaining_slots -= 1

    # Fase 2: Optimalisatie — vervang zwakke leden door sterkere
    # als budget het toelaat
    def total_points(t):
        return sum(r['expected_points'] for r in t)

    improved = True
    while improved:
        improved = False
        for i, weak in enumerate(team):
            if weak['price'] <= 0:
                continue
            # Probeer weak te vervangen door een externe renner
            for strong in sorted_riders:
                if strong in team:
                    continue
                # Kan strong in het budget passen?
                swap_cost = strong['price'] - weak['price']
                if swap_cost <= remaining_budget and strong['expected_points'] > weak['expected_points']:
                    # Test de swap
                    new_team = team.copy()
                    new_team[i] = strong
                    new_total = total_points(new_team)
                    if new_total > total_points(team):
                        team[i] = strong
                        remaining_budget -= swap_cost
                        improved = True
                        print(f"🔄 Swap: {weak['name']} → {strong['name']} (+{new_total - total_points(team)} pt)", file=sys.stderr)
                        break
            if improved:
                break

    # Fase 3: Vul overgebleven slots met laagste prijs fillers
    fillers = sorted([r for r in riders if r['price'] <= remaining_budget and r not in team],
                     key=lambda r: r['price'])
    for f in fillers:
        if len(team) >= team_size:
            break
        if f['price'] <= remaining_budget:
            team.append(f)
            remaining_budget -= f['price']

    # Als we nog slots over hebben en budget, vul met duurdere fillers
    extra = sorted([r for r in riders if r not in team and r['price'] <= remaining_budget],
                   key=lambda r: -r['expected_points'])
    for r in extra:
        if len(team) >= team_size:
            break
        if r['price'] <= remaining_budget:
            team.append(r)
            remaining_budget -= r['price']

    return team, remaining_budget


def suggest_alternatives(riders, team, budget_spent):
    """
    Vind alternatieve renners die niet in de ploeg zitten maar goede value bieden.
    """
    team_names = {r['name'] for r in team}
    alternatives = [r for r in riders if r['name'] not in team_names and r['price'] > 0]

    # Sorteer op punten
    alternatives.sort(key=lambda r: (-r['expected_points'], r['price']))

    return alternatives[:10]


def print_team(team, remaining_budget, title="OPTIMALE PLOEG"):
    """Print de ploeg in een mooi format."""
    print(f"\n{'='*70}")
    print(f"  🏆 {title}")
    print(f"{'='*70}\n")

    total_pts = sum(r['expected_points'] for r in team)
    total_cost = sum(r['price'] for r in team)

    team_sorted = sorted(team, key=lambda r: -r['expected_points'])

    print(f"  {'#':<3s} {'RENNER':<25s} {'PLOEG':<8s} {'€':>6s} {'~PT':>6s} {'TYPE':<15s} {'VALUE':>6s}")
    print(f"  {'-'*70}")
    for i, r in enumerate(team_sorted, 1):
        value = r['expected_points'] / r['price'] if r['price'] > 0 and r['expected_points'] > 0 else 0
        kp = " ★" if i == 1 else ""
        print(f"  {i:<3d} {r['name']:<25s} {r['team']:<8s} €{r['price']:.0f}M {r['expected_points']:>4d}pt {r['type']:<15s} {value:>5.0f}{kp}")
    print(f"  {'-'*70}")
    print(f"  {'':<3s} {'TOTAAL':<25s} {'':<8s} €{total_cost:.0f}M {total_pts:>4d}pt")
    print(f"  {'':<3s} {'RESTEREND BUDGET':<25s} {'':<8s} €{remaining_budget:.0f}M")
    print(f"  {'':<3s} {'AANTAL RENNERS':<25s} {'':<8s} {len(team)}/16")
    print()


def print_strategy(team, remaining_budget):
    """Print strategisch advies."""
    print(f"{'='*70}")
    print(f"  💡 STRATEGISCH ADVIES")
    print(f"{'='*70}\n")

    total_pts = sum(r['expected_points'] for r in team)

    gc_riders = [r for r in team if r['type'] in ('gc_climber', 'gc_young')]
    sprinters = [r for r in team if r['type'] == 'sprinter']
    allrounders = [r for r in team if r['type'] == 'allrounder']
    fillers = [r for r in team if r['type'] == 'filler']

    gc_pts = sum(r['expected_points'] for r in gc_riders)
    sprint_pts = sum(r['expected_points'] for r in sprinters)
    allround_pts = sum(r['expected_points'] for r in allrounders)

    print(f"  📊 PUNTENVERDELING:")
    print(f"     GC/Klimmers ({len(gc_riders)}): {gc_pts} pt (~{gc_pts*100//total_pts}%)")
    print(f"     Sprinters ({len(sprinters)}): {sprint_pts} pt (~{sprint_pts*100//total_pts}%)")
    print(f"     Allrounders ({len(allrounders)}): {allround_pts} pt (~{allround_pts*100//total_pts}%)")
    print(f"     Fillers ({len(fillers)}): budgetbuffer")
    print()

    if gc_pts > total_pts * 0.5:
        print(f"  ✅ Goede GC-dekking — de bergetappes zijn goed afgedekt.")
    if sprint_pts > 1500:
        print(f"  ✅ Sterke sprintlijn — de 7 vlakke ritten geven veel punten.")
    if remaining_budget < 2:
        print(f"  ⚠️  Budget grotendeels opgebruikt. Je hebt nog 3 gratis transfers.")
        print(f"     Plan: gebruik de 3 gratis transfers voor strategische swaps.")
        print(f"     Tip: vervang 1 filler (€2M) door Anthony Turgis (€3M) voor extra")
        print(f"     aanvalspunten — hou dan €1M over voor latere noodtransfers.")
    else:
        print(f"  ✅ Budget over: €{remaining_budget}M — ideaal voor transfers!")
        print(f"     Je kan minstens 3 gratis + 1 betaalde transfer doen.")

    print()
    print(f"  🎯 KOPMAN-ADVIES:")
    print(f"     Kies {team[0]['name']} als kopman — {team[0]['expected_points']} verwachte pt × bonus.")
    if len(team) > 1:
        print(f"     Alternatief: {team[1]['name']} als je voor underdog gaat.")
    print()

    print(f"  🔄 TRANSFERPLAN:")
    print(f"     • Week 1 (vlakke etappes): hou de sprinters in de basis")
    print(f"     • Week 2 (Alpen): swap fillers voor klimmers")
    print(f"     • Week 3 (Alpe d'Huez dubbel!): maximaliseer bergpunten")
    print(f"     • Hou €6-10M over voor noodtransfers (blessures, opgave)")
    print()


def print_alternatives(alternatives, team, remaining_budget):
    """Print alternatieve renners."""
    print(f"{'='*70}")
    print(f"  🔄 ALTERNATIEVE RENNERS (NIET IN PLOEG)")
    print(f"{'='*70}\n")

    team_cost = sum(r['price'] for r in team)

    print(f"  {'#':<3s} {'RENNER':<25s} {'PLOEG':<8s} {'€':>6s} {'~PT':>6s} {'VALUE':>6s} {'VERVANGT':<25s}")
    print(f"  {'-'*80}")
    for i, alt in enumerate(alternatives, 1):
        value = alt['expected_points'] / alt['price'] if alt['price'] > 0 else 0
        # Suggestie: welke teamgenoot heeft gelijkaardig profiel?
        similar_in_team = [r for r in team if r['type'] == alt['type'] and r['price'] >= alt['price'] - 2]
        vervanger = similar_in_team[0]['name'] if similar_in_team else "(budgetplaats)"
        print(f"  {i:<3d} {alt['name']:<25s} {alt['team']:<8s} €{alt['price']:.0f}M {alt['expected_points']:>4d}pt {value:>5.0f}  → {vervanger}")
    print()
    print(f"  💡 Budget over: €{remaining_budget}M — je kan deze renners toevoegen")
    print(f"     door een filler (€2M) te vervangen.")
    print()


def main():
    print(f"{'='*70}")
    print(f"  🚴 SPORZA WIELERMANAGER — TOUR DE FRANCE 2026")
    print(f"  Data-driven ploegoptimalisatie")
    print(f"{'='*70}")
    print(f"\n  Budget: €{BUDGET}M  |  Ploeg: {TEAM_SIZE} renners  |  Tour: 4-26 juli 2026\n")

    # Haal data op
    html = fetch_pouletips_data()
    riders = get_riders_from_table_data(html) if html else None

    if riders and len(riders) > 10:
        print(f"\n✅ Data succesvol opgehaald! {len(riders)} renners gevonden.\n", file=sys.stderr)
    else:
        print(f"\n⚠️  Gebruik backup data ({len(FALLBACK_RIDERS)} renners)\n", file=sys.stderr)
        riders = FALLBACK_RIDERS

    # Optimaliseer
    team, remaining = optimize_team(riders)

    # Output
    print_team(team, remaining)

    alternatives = suggest_alternatives(riders, team, BUDGET - remaining)
    print_alternatives(alternatives, team, remaining)

    print_strategy(team, remaining)

    print(f"{'='*70}")
    print(f"  📊 Data bronnen")
    print(f"{'='*70}")
    print(f"  • Pouletips verwachte punten: pouletips.nl/tour-de-france-2026/sporza/beste-renners/")
    print(f"  • Sporza Wielermanager: wielermanager.sporza.be")
    print(f"  • Startlist: letour.fr/en/riders + Wikipedia")
    print(f"  • Regels: sporza.be wedstrijdreglement Tour 2026")
    print()
    print(f"  🐙 GitHub: github.com/WiskivBot/sporza-tour-2026")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
