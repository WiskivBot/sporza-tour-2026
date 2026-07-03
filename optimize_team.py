#!/usr/bin/env python3
"""
Sporza Wielermanager Tour de France 2026 - Optimale Ploeg Samensteller
Gebruik: python3 optimize_team.py
"""

# === DATA ===
team_data = [
    ("Tadej POGACAR ★", "UAE Team Emirates XRG", 12.0, 1298, "Klassement/Klimmer",
     "Dé topfavoriet. 3x Tour-winnaar, beste klimmer ter wereld. Moet je gewoon hebben — levert punten in élke bergrit + GC. Duur maar onmisbaar."),
    ("Jonas VINGEGAARD", "Visma-Lease a Bike", 10.0, 624, "Klassement/Klimmer",
     "Pogacar's grootste rivaal. Wint ook tijdritten. Absolute must-have voor bergetappes en GC."),
    ("Jasper PHILIPSEN", "Alpecin-Premier Tech", 9.0, 613, "Sprinter",
     "Beste sprinter ter wereld. 7 vlakke ritten = 7 kansen op groene trui-punten. Dikke puntenmachine."),
    ("Remco EVENEPOEL", "Red Bull-BORA-Hansgrohe", 9.0, 596, "Klassement/Klimmer/Tijdrijder",
     "Top-3 GC-kandidaat. Wint tijdrit + bergritten. Combineert alles. Zeer stabiele puntenbron."),
    ("Paul SEIXAS", "Decathlon CMA CGM", 8.0, 575, "Klassement/Jong",
     "Grootste jonge talent. Strijdt om witte trui. Bergop sterk. Uitstekende value voor 8M."),
    ("Mads PEDERSEN", "Lidl-Trek", 8.0, 525, "Sprinter/Klassieker",
     "Top-sprinter die ook heuvels aankan. Scoort in vlakke + semi-bergritten. Groen trui-kandidaat."),
    ("Mathieu VAN DER POEL", "Alpecin-Premier Tech", 8.0, 466, "Allrounder/Klassieker",
     "Kan winnen op elk terrein. Superster. In vorm gevaarlijk voor ritwinsten. Multitool."),
    ("Isaac DEL TORO", "UAE Team Emirates XRG", 7.0, 459, "Klassement/Jong",
     "Mexicaans supertalent. Wordt uitgespeeld voor UAE. Wit trui-kandidaat + top-10 GC."),
    ("Arnaud DE LIE", "Lotto Intermarché", 4.0, 408, "Sprinter",
     "Beste value-renner van het spel! 4M voor 408 verwachte punten. Scoort in massasprints."),
    ("Biniam GIRMAY", "NSN Cycling Team", 5.0, 405, "Sprinter/Allrounder",
     "Top-sprinter die ook heuvels overleeft. Zeer constante punten. Goede prijs/kwaliteit."),
    ("Tom PIDCOCK", "Pinarello-Q36.5", 6.0, 400, "Allrounder/Klimmer",
     "Brits fenomeen. Wint bergritten + tijdritten. Nieuwe ploeg, extra motivatie."),
    ("Fernando GAVIRIA", "Caja Rural-Seguros RGA", 4.0, 348, "Sprinter",
     "Goedkope sprinter met veel overwinningsdrang. Scoort in vlakke ritten. Budgetvriendelijk."),
    ("Dorian GODON", "Netcompany INEOS", 4.0, 298, "Allrounder/Aanvaller",
     "Sterke Franse allrounder. Kan in vroege vluchten zitten. Consistent punten pakken."),
    ("Stefano OLDANI", "Caja Rural-Seguros RGA", 2.0, 0, "Aanvaller/Allrounder",
     "Goedkope busvuller. Kan verrassen uit vluchten. Lage kost, risico-spreiding."),
    ("Damien HOWSON", "Pinarello-Q36.5", 2.0, 0, "Knecht/Allrounder",
     "Ervaren Australiër. Lage kost, kan in vluchten rijden. Budgetbuffer."),
    ("Bert VAN LERBERGHE", "Soudal Quick-Step", 2.0, 0, "Knecht/Sprinter",
     "Goedkope Belg. Loodst Merlier in massasprints. Lage kost voor budgetruimte."),
]

alternatives = [
    ("Tim MERLIER", "Soudal Quick-Step", 9.0, 507, "Sprinter",
     "Top-sprinter, maar €9M is duur vs Philipsen. Kies hem i.p.v. Philipsen als je Belgisch wil gaan."),
    ("Olav KOOIJ", "Decathlon CMA CGM", 7.0, 329, "Sprinter",
     "Jonge Nederlandse sprinter. Iets duurder dan Gaviria maar meer potentieel."),
    ("Juan AYUSO", "Lidl-Trek", 7.0, 436, "Klassement/Jong",
     "Top-talent. In topvorm strijdt hij om top-5 GC. Vervanger voor Del Toro."),
    ("Egan BERNAL", "Netcompany INEOS", 5.0, 324, "Klassement/Klimmer",
     "Tour-winnaar 2019. Terug in vorm. Goedkoper alternatief voor Seixas."),
    ("Adam YATES", "UAE Team Emirates XRG", 5.0, 379, "Klimmer/Knecht",
     "Pogacar's superknecht. Scoort zelf ook in bergritten."),
    ("Brandon MCNULTY", "UAE Team Emirates XRG", 4.0, 183, "Tijdrijder/Allrounder",
     "Amerikaans kampioen tijdrijden. Kan winnen uit vluchten."),
    ("Kévin VAUQUELIN", "Netcompany INEOS", 6.0, 265, "Allrounder/Aanvaller",
     "Franse alleskunner. Wint uit aanvallen."),
    ("Cian UIJTDEBROEKS", "Movistar Team", 5.0, 168, "Klassement/Jong",
     "Belgisch talent. Budgetvriendelijk, jongerenpunten mogelijk."),
    ("Jasper STUYVEN", "Soudal Quick-Step", 4.0, 142, "Klassieker/Allrounder",
     "Ervaren Belg. Wint uit vluchten. Consistent."),
    ("Anthony TURGIS", "TotalEnergies", 3.0, 156, "Aanvaller/Allrounder",
     "Franse vechter. Wint graag uit ontsnappingen. Zeer goedkoop."),
]


def print_separator(title=""):
    print("=" * 70)
    if title:
        print(title)
        print("=" * 70)
    print()


def main():
    print_separator("SPORZA WIELERMANAGER TOUR DE FRANCE 2026")
    print("💰 Budget: €100M  |  👥 16 renners  |  📅 4-26 juli 2026")
    print()

    print_separator("🏆 OPTIMALE PLOEG — ~7015 verwachte punten")

    totaal_budget = 0
    totaal_punten = 0
    for i, (naam, ploeg, prijs, punten, _, _) in enumerate(team_data, 1):
        totaal_budget += prijs
        totaal_punten += punten
        kp = " ★KOPMAN" if i == 1 else ""
        print(f"  {i:2d}. {naam:<30s} | {ploeg:<28s} | €{prijs:>4.0f}M | ~{punten:>4d} pt{kp}")

    print("-" * 70)
    print(f"     TOTAAL{'':>52s} €{totaal_budget:.0f}M | ~{totaal_punten} pt")
    print(f"     RESTEREND BUDGET{'':>44s} €{100 - totaal_budget:.0f}M")

    print_separator("📋 ANALYSE PER RENNER")
    for i, (naam, ploeg, prijs, punten, profiel, analyse) in enumerate(team_data, 1):
        kp = " ★ KOPMAN" if i == 1 else ""
        print(f"  {i}. {naam} ({ploeg}) — €{prijs:.0f}M{kp}")
        print(f"     Profiel: {profiel}")
        print(f"     Verwacht: ~{punten} pt")
        print(f"     Waarom: {analyse}")
        print()

    print_separator("🔄 ALTERNATIEVE RENNERS")
    for i, (naam, ploeg, prijs, punten, profiel, analyse) in enumerate(alternatives, 1):
        print(f"  {i}. {naam:<25s} | {ploeg:<28s} | €{prijs:.0f}M | ~{punten:3d} pt")
        print(f"     {analyse}")
        print()

    print_separator("💡 STRATEGIE")
    print("""
  GC-dekking:    Pogačar + Vingegaard + Evenepoel (~2500 pt)
  Sprint:        Philipsen + Pedersen + De Lie + Girmay (~2000 pt)
  Allround:      Van der Poel + Pidcock + Godon (ritwinsten)
  Toekomst:      Seixas + Del Toro (witte trui)
  Bus:           Oldani + Howson + Van Lerberghe (budgetbuffer)

  Transferplan:
  • 3 gratis transfers — gebruik ze strategisch
  • Week 1: sprinters in de basis
  • Week 2 (Alpen): klimmers erbij
  • Week 3 (Alpe d'Huez): extra berggeiten
  • Hou €6-10M over voor noodtransfers

  Kopman: Kies Pogačar! 1298 verwachte punten × bonus.
  Alternatief: Vingegaard als underdog-keuze.
""")


if __name__ == "__main__":
    main()
