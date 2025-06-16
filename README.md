# CDA2 Demokratie Challenge - Schweizer Abstimmungsanalyse

Dieses Repository enthält eine umfassende Analyseplattform zur Visualisierung und Dokumentation von Schweizer Abstimmungsdaten. Das Projekt wurde vollständig professionalisiert und modularisiert, um wissenschaftlichen Standards zu entsprechen.

## 🎯 Projektziele

- Explorative Datenanalyse (EDA) der Schweizer Abstimmungsdaten von 1893-2025
- Spezialisierte Analyse gesellschaftsorientierter Abstimmungen
- Kartographische Visualisierung einzelner Abstimmungen
- Interaktive Vergleichsanalysen zwischen verschiedenen Kantonen und Zeiträumen
- Wissenschaftlich fundierte Erkenntnisse über Trends in der Schweizer Demokratie

## 🛠️ Installation und Setup

### Voraussetzungen

- Python 3.8+
- Poetry (Dependency Management)

### Poetry Installation

```bash
# Via pip
pip install poetry

# Via Homebrew (macOS)
brew install poetry

# Via curl (Unix/Linux)
curl -sSL https://install.python-poetry.org | python3 -
```

### Projekt-Setup

```bash
# Repository klonen
git clone <repository-url>
cd CDA2-Demokratie-Challange

# Virtuelle Umgebung konfigurieren
poetry config virtualenvs.in-project true

# Dependencies installieren
poetry install

# Jupyter Kernel für Poetry hinzufügen
poetry run python -m ipykernel install --user --name=poetry-env --display-name "Python (Poetry)"
```

## 📁 Projektstruktur

```
├── data/                                       # Datensätze
│   ├── dataset.csv                            # Hauptdatensatz (696 Abstimmungen, 1893-2025)
│   ├── gesellschaftliche_abstimmungen.csv    # Gefilterte gesellschaftliche Abstimmungen
│   ├── gesellschaftliche_abstimmungen_annotiert.csv  # Annotierte Klassifikationen
│   ├── gesellschaftliche_abstimmungen_detailliert.csv # Detailanalyse-Ergebnisse
│   ├── kantons_liberalitaets_ranking.csv      # Kantonale Liberalitäts-Rankings
│   └── maps/                                  # Schweizer Kantonsgrenzen (SwissBOUNDARIES3D)
│       └── swissboundaries.shp/               # Hochauflösende Shapefiles
├── analyse_grob.ipynb                         # Grosse explorative Datenanalyse
├── analyse_detailliert.ipynb                 # Detaillierte Analyse gesellschaftlicher Abstimmungen
├── analyse_einzelne-abstimmungen.ipynb       # Kartographische Einzelanalysen
├── utils_analyse_grob.py                     # Utility-Funktionen für grobes EDA
├── utils_analyse_detailliert.py              # Utility-Funktionen für detailliertes EDA
├── utils_analyse_einzelne-abstimmungen.py    # Utility-Funktionen für Einzelanalysen
├── test_utils_*.py                           # Unit Tests (29 Tests, 100% Erfolgsquote)
├── docs/                                     # Dokumentation
│   ├── CODEBOOK.pdf                          # Datensatz-Dokumentation
│   └── Demokratie_Challenge_Liberalismus-Entwicklung.docx
└── pyproject.toml                            # Poetry-Konfiguration
```

## 📊 Analysewerkzeuge

### 1. Grobes EDA (`analyse_grob.ipynb`)

**Fokus:** Übergreifende Trends und Muster in allen Schweizer Abstimmungen

**Hauptfunktionen:**

- Zeitraumanalyse (1893-2025 in 5 Epochen)
- Identifikation gesellschaftsorientierter Abstimmungen
- Kantonale Unterschiede und Korrelationsanalysen
- Trend-Visualisierungen mit statistischer Validierung

**Utility-Modul:** `utils_analyse_grob.py` (11 Funktionen)

### 2. Detailliertes EDA (`analyse_detailliert.ipynb`)

**Fokus:** Spezialisierte Analyse gesellschaftsorientierter Abstimmungen

**Erweiterte Features:**

- Intelligente Keyword-Klassifikation mit Ausschlusskriterien
- Liberalitäts-Ranking der Kantone
- Zeitreihenanalyse mit gleitenden Durchschnitten
- Validierungsstichproben für Qualitätskontrolle

**Utility-Modul:** `utils_analyse_detailliert.py` (13 Funktionen)

### 3. Einzelabstimmungsanalyse (`analyse_einzelne_abstimmungen.ipynb`)

**Fokus:** Kartographische Einzelanalysen mit SwissBOUNDARIES3D

**Professionelle Features:**

- Intelligente Suchfunktionen mit flexibler Titel-Suche
- Hochaufgelöste Schweizer Kantonsgrenzen (SwissBOUNDARIES3D)
- Kartographische Visualisierung mit anpassbaren Farbschemata
- Statistische Auswertungen pro Abstimmung
- Modularisierte Plot-Funktionen für konsistente Darstellung

**Utility-Modul:** `utils_analyse_einzelne_abstimmungen.py` (12 Funktionen)

## 🔬 Wissenschaftliche Standards

### Qualitätssicherung

- **29 Unit Tests** mit 100% Erfolgsquote
- Automatisierte Validierung aller Kernfunktionen
- Robuste Fehlerbehandlung und Edge-Case-Tests
- Type Hints und umfassende Dokumentation
- Modularer Import-Mechanismus für Dateien mit Sonderzeichen

### Reproduzierbarkeit

- Modularisierte Funktionen in separaten Utility-Modulen
- Standardisierte Datenverarbeitung
- Konsistente Visualisierungsparameter
- Wissenschaftliche Methodenvalidierung

## 📈 Haupterkenntnisse

### Gesellschaftliche Abstimmungen

- **Klassifikationsalgorithmus:** 35+ Schlüsselwörter mit Ausschlusskriterien
- **Kantonale Liberalität:** Quantitative Rankings basierend auf Ja-Stimmen-Anteilen
- **Zeitliche Trends:** Signifikante Veränderungen in verschiedenen Epochen

### Kartographische Analysen

- **SwissBOUNDARIES3D Integration:** Hochpräzise Kantonsgrenzen
- **Modularisierte Visualisierung:** Konsistente Farbschemata und Layouts
- **Intelligente Suchfunktionen:** Flexible Titel-Suche mit Fehlertoleranz

### Technische Validierung

- **Umfassende Tests:** Alle Kernfunktionen automatisiert getestet
- **Robuste Datenverarbeitung:** Fehlerbehandlung für Edge Cases
- **Reproduzierbare Analysen:** Standardisierte Workflows und Parameter

## Aktuelle Projektstatistiken

### Datenumfang

- **696 Abstimmungen** von 1893-2025
- **874 Datenspalten** pro Abstimmung
- **26 Schweizer Kantone** mit vollständigen Geodaten

### Code-Qualität

- **29 Unit Tests** mit 100% Erfolgsquote
- **3 spezialisierte Utility-Module** mit 36+ Funktionen
- **Modularer Import-Mechanismus** für robuste Funktionalität

### Analysebereiche

- **10 Test-Kategorien** für grobes EDA
- **14 Test-Kategorien** für detailliertes EDA
- **5 Test-Kategorien** für Einzelabstimmungsanalysen

## 🚀 Verwendung

### Jupyter Notebooks starten

```bash
# Poetry-Umgebung aktivieren
poetry shell

# Jupyter Lab starten
jupyter lab

# Oder Jupyter Notebook
jupyter notebook
```

### Tests ausführen

```bash
# Alle Tests
poetry run pytest test_utils_*.py -v

# Spezifische Module  
poetry run pytest test_utils_analyse_grob.py -v
poetry run pytest test_utils_analyse_detailliert.py -v
poetry run pytest test_utils_analyse_einzelne_abstimmungen.py -v

# Kurzer Überblick (nur Ergebnisse)
poetry run pytest test_utils_*.py --tb=no -q
```

### Datenanalyse-Workflow

1. **Beginn:** `analyse_grob.ipynb` für allgemeine Trends
2. **Vertiefung:** `analyse_detailliert.ipynb` für gesellschaftliche Abstimmungen
3. **Spezifisch:** `analyse_einzelne-abstimmungen.ipynb` für einzelne Vorlagen

## 📋 Abhängigkeiten

### Kernbibliotheken

- `pandas >= 1.5.0` - Datenverarbeitung
- `numpy >= 1.20.0` - Numerische Berechnungen
- `matplotlib >= 3.5.0` - Basis-Visualisierungen
- `seaborn >= 0.11.0` - Statistische Plots

### Spezialisiert

- `geopandas >= 0.12.0` - Geospatiale Datenverarbeitung
- `shapely >= 1.8.0` - Geometrische Operationen
- `scipy >= 1.8.0` - Statistische Tests und Korrelationen

### Entwicklung

- `pytest >= 7.0.0` - Unit Testing Framework
- `jupyter >= 1.0.0` - Notebook-Umgebung

## 🎨 Visualisierungsstandards

- **Professionelle Farbschemata:** RdYlGn für Ja/Nein-Visualisierungen
- **Konsistente Layouts:** Standardisierte Achsenbeschriftungen und Titel
- **SwissBOUNDARIES3D Integration:** Hochauflösende Kantonsgrenzen
- **Modulare Plot-Funktionen:** Wiederverwendbare Visualisierungskomponenten

## 🔧 Technische Features

### Moderne Python-Entwicklung

- **Type Hints:** Vollständige Typisierung für bessere Code-Qualität
- **Modularer Import:** Robuste Behandlung von Dateien mit Sonderzeichen
- **Error Handling:** Umfassende Fehlerbehandlung und Validierung

### Geospatiale Verarbeitung

- **GeoPandas Integration:** Professionelle Kartenverarbeitung
- **Shapely Geometrien:** Präzise geometrische Operationen
- **Koordinatensystem-Management:** Korrekte Projektion für Schweizer Daten

## 📝 Weiterführende Dokumentation

- **Code-Dokumentation:** Inline-Docstrings in allen Utility-Modulen
- **Methodologie:** Wissenschaftliche Grundlagen in den Notebooks dokumentiert

## 🤝 Beitrag und Entwicklung

Dieses Projekt folgt wissenschaftlichen Entwicklungsstandards:

- Modulare Architektur für Erweiterbarkeit
- Umfassende Tests für Stabilität
- Dokumentierte APIs für Nachvollziehbarkeit
- Reproduzierbare Analysen für Validierung
