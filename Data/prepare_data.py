import pandas as pd

# 1. CSV-Datei einlesen – hier wird angenommen, dass das CSV mit Semikolon getrennt ist.
df = pd.read_csv("dataset.csv", sep=";", encoding="utf-8")

# 2. Allgemeine Spalten umbenennen
rename_dict = {
    "abstimmungsnummer": "Vote_ID",
    "abstimmungsdatum": "Vote_Date",
    "titel_off_d": "Vote_Title",
    "stichwort": "Keywords",
    "annahme": "Vote_Result",       # 0 = Ablehnung, 1 = Annahme
    "volkja": "Yes_Votes",
    "volknein": "No_Votes",
    "volkja-proz": "Yes_Percentage",
    "bet": "Turnout_Percentage",
    "br-pos": "Bundesrat_Position",
    "nr-pos": "Nationalrat_Position",
    "sr-pos": "Ständerat_Position",
    "legisjahr": "Legislaturjahr"
}

# 2a. Mapping der kantonalen Abkürzungen zu lesbaren Namen
canton_mapping = {
    "zh": "Zürich",
    "be": "Bern",
    "lu": "Luzern",
    "ur": "Uri",
    "sz": "Schwyz",
    "ow": "Obwalden",
    "nw": "Nidwalden",
    "gl": "Glarus",
    "zg": "Zug",
    "fr": "Freiburg",
    "so": "Solothurn",
    "bs": "Basel-Stadt",
    "bl": "Basel-Land",
    "sh": "Schaffhausen",
    "ar": "Appenzell Ausserrhoden",
    "ai": "Appenzell Innerrhoden",
    "sg": "St. Gallen",
    "gr": "Graubünden",
    "ag": "Aargau",
    "tg": "Thurgau",
    "ti": "Tessin",
    "vd": "Waadt",
    "vs": "Wallis",
    "vso": "Oberwallis",
    "vsr": "Valais Romand",
    "ne": "Neuenburg",
    "ge": "Genf",
    "ju": "Jura"
}

# 2b. Für jeden Kanton sollen drei Spalten (Ja, Nein, Ja-Prozent) umbenannt werden.
cantons = list(canton_mapping.keys())

for kanton in cantons:
    # Ursprüngliche Spaltennamen: z. B. "zh-ja", "zh-nein", "zh-japroz"
    original_yes = f"{kanton}-ja"
    original_no = f"{kanton}-nein"
    original_yesperc = f"{kanton}-japroz"
    
    # Neue Spaltennamen: z. B. "Zürich_Yes", "Zürich_No", "Zürich_Yes_Percentage"
    full_name = canton_mapping[kanton]
    new_yes = f"{full_name}_Yes"
    new_no = f"{full_name}_No"
    new_yesperc = f"{full_name}_Yes_Percentage"
    
    rename_dict[original_yes] = new_yes
    rename_dict[original_no] = new_no
    rename_dict[original_yesperc] = new_yesperc

# Wendet die Umbenennung auf den gesamten DataFrame an.
df.rename(columns=rename_dict, inplace=True)

# 3. Liste aller irrelevanter Spalten, die für eure Fragestellung (Wandel Frauenstimmrecht, kantonale Unterschiede, politische und gesellschaftliche Einflüsse) nicht benötigt werden.
irrelevant_columns = [
    # Alternative Titelvarianten, Zusatzinfos
    "titel_kurz_d", "titel_kurz_f", "titel_kurz_e", "titel_off_f", "rechtsform", "init_formul",
    "kurzbetitel", "beschreibung", "anneepolitique", "bkchrono-de", "bkchrono-fr",
    
    # Prozess- und Datumsfelder, die nicht zur inhaltlichen Analyse beitragen
    "dat-message", "dat-parl", "dat-force", "dauer_bv", "dauer_abst", "i-dauer_tot",
    
    # Unterschriftensammlung und Urheberangaben (relevant nur für Initiativen)
    "urheber", "urheber-fr", "dat-preexam", "dat-start", "dat-limit", "sammelfrist",
    "unter-quorum", "dat-submit", "dat-success", "i-dauer_samm", "i-dauer_br", 
    "fr-dauer_samm", "fr-dauer_tot", "unter_g", "unter_u", "sammeltempo", "sparedays",
    
    # Abstimmungskampf, Online-Informationen und Videolinks
    "info_br-de", "info_br-fr", "info_br-en", "info_dep-de", "info_dep-fr", "info_dep-en",
    "info_amt-de", "info_amt-fr", "info_amt-en", "easyvideo_de", "easyvideo_fr",
    
    # Kampagnenwebseiten, Parteiparolen und ähnliche Informationen
    "web-yes-1-de", "web-yes-1-fr", "web-no-3-de", "web-no-3-fr",
    "p-fdp", "p-sps", "p-svp", "p-mitte", "p-others_yes", "p-others_yes-fr",
    "p-others_no", "p-others_no-fr", "p-others_free", "p-others_free-fr",
    "p-others_counterp", "p-others_counterp-fr", "p-others_init", "p-others_init-fr",
    "pdev-bdp_AG", "pdev-bdp_AI", "pdev-csp_FR", "pdev-cvp_AG",
    
    # Medienkampagnen und Inserate
    "inserate-total", "inserate-je-ausgabe", "inserate-ja", "inserate-nein", "inserate-neutral",
    "mediares-tot", "mediares-d", "mediares-f",
    "mediaton-tot", "mediaton-d", "mediaton-f",
    "finanz-link-de", "finanz-link-fr", "finanz-ja-tot", "finanz-nein-tot",
    "finanz-ja-gr-de", "finanz-ja-gr-fr", "finanz-nein-gr-de", "finanz-nein-gr-fr",
    "poster_ja_mfg", "poster_nein_mfg", "poster_ja_sa", "poster_nein_sa", "poster_ja_bs", "poster_nein_bs",
    
    # Detaillierte Stände- und kantonale Beteiligungsdaten
    "volk", "städemehr", 
    "zh-berecht", "be-berecht", "lu-berecht", "ur-berecht", "sz-berecht", "ow-berecht", "nw-berecht", 
    "gl-berecht", "zg-berecht", "fr-berecht", "so-berecht", "bs-berecht", "bl-berecht", "sh-berecht", 
    "ar-berecht", "ai-berecht", "sg-berecht", "gr-berecht", "ag-berecht", "tg-berecht", "ti-berecht", 
    "vd-berecht", "vs-berecht", "vso-berecht", "vsr-berecht", "ne-berecht", "ge-berecht", "ju-berecht",
    "zh-bet", "be-bet", "lu-bet", "ur-bet", "sz-bet", "ow-bet", "nw-bet", "gl-bet", "zg-bet", "fr-bet", 
    "so-bet", "bs-bet", "bl-bet", "sh-bet", "ar-bet", "ai-bet", "sg-bet", "gr-bet", "ag-bet", "tg-bet", 
    "ti-bet", "vd-bet", "vs-bet", "vso-bet", "vsr-bet", "ne-bet", "ge-bet", "ju-bet",
    "zh-gultig", "be-gultig", "lu-gultig", "ur-gultig", "sz-gultig", "ow-gultig", "nw-gultig", 
    "gl-gultig", "zg-gultig", "fr-gultig", "so-gultig", "bs-gultig", "bl-gultig", "sh-gultig", 
    "ar-gultig", "ai-gultig", "sg-gultig", "gr-gultig", "ag-gultig", "tg-gultig", "ti-gultig", 
    "vd-gultig", "vs-gultig", "vso-gultig", "vsr-gultig", "ne-gultig", "ge-gultig", "ju-gultig",
    "kt-ja", "kt-nein", "ktjaproz"
]

# Lösche alle in der Liste vorhandenen irrelevanten Spalten
for col in irrelevant_columns:
    if col in df.columns:
        df.drop(columns=[col], inplace=True)

# 4. Spalten mit zu wenigen Werten entfernen
# Wir löschen alle Spalten, bei denen weniger als 20 % der Werte vorhanden sind.
threshold = 0.2 * len(df)
df = df.dropna(axis=1, thresh=threshold)

# 5. Das bereinigte Dataset in einer neuen CSV-Datei speichern
output_filename = "dataset_renamed.csv"
df.to_csv(output_filename, index=False, encoding="utf-8")

print(f"Die CSV wurde erfolgreich überarbeitet und als '{output_filename}' gespeichert.")