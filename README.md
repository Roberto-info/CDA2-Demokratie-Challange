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
├── Data/                                    # Datensätze
│   ├── dataset.csv                         # Hauptdatensatz
│   ├── gesellschaftliche_abstimmungen.csv  # Gefilterte gesellschaftliche Abstimmungen
│   └── maps/                               # Schweizer Kantonsgrenzen (Shapefiles)
├── grobes_eda.ipynb                        # Grosse explorative Datenanalyse
├── detailliertes_eda.ipynb                 # Detaillierte Analyse gesellschaftlicher Abstimmungen
├── Analyse_Einzelner_Abstimmungen.ipynb    # Kartographische Einzelanalysen
├── utils_grobes_eda.py                     # Utility-Funktionen für grobes EDA
├── utils_detailliertes_eda.py              # Utility-Funktionen für detailliertes EDA
├── utils_abstimmungen_analyse.py           # Utility-Funktionen für Abstimmungsanalyse
├── test_utils_*.py                         # Unit Tests (53 Tests)
├── PROJEKT_ZUSAMMENFASSUNG.md              # Technische Dokumentation
└── pyproject.toml                          # Poetry-Konfiguration
```

## 📊 Analysewerkzeuge

### 1. Grobes EDA (`grobes_eda.ipynb`)
**Fokus:** Übergreifende Trends und Muster in allen Schweizer Abstimmungen

**Hauptfunktionen:**
- Zeitraumanalyse (1893-2025 in 5 Epochen)
- Identifikation gesellschaftsorientierter Abstimmungen
- Kantonale Unterschiede und Korrelationsanalysen
- Trend-Visualisierungen mit statistischer Validierung

**Utility-Modul:** `utils_grobes_eda.py` (10+ Funktionen)

### 2. Detailliertes EDA (`detailliertes_eda.ipynb`)
**Fokus:** Spezialisierte Analyse gesellschaftsorientierter Abstimmungen

**Erweiterte Features:**
- Intelligente Keyword-Klassifikation mit Ausschlusskriterien
- Liberalitäts-Ranking der Kantone
- Zeitreihenanalyse mit gleitenden Durchschnitten
- Validierungsstichproben für Qualitätskontrolle

**Utility-Modul:** `utils_detailliertes_eda.py` (12+ Funktionen)

### 3. Abstimmungsanalyse (`Analyse_Einzelner_Abstimmungen.ipynb`)
**Fokus:** Kartographische Einzelanalysen mit SwissBOUNDARIES3D

**Professionelle Features:**
- Intelligente Suchfunktionen (RegEx-Unterstützung)
- Hochaufgelöste Schweizer Kantonsgrenzen
- Interaktive Vergleichsanalysen (bis zu 6 Abstimmungen)
- Korrelationsmatrizen und Statistik-Overlays

**Utility-Modul:** `utils_abstimmungen_analyse.py` (15+ Funktionen)

## 🔬 Wissenschaftliche Standards

### Qualitätssicherung
- **53 Unit Tests** mit 100% Erfolgsquote
- Automatisierte Validierung aller Kernfunktionen
- Robuste Fehlerbehandlung und Edge-Case-Tests
- Type Hints und umfassende Dokumentation

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
- **Interaktive Vergleiche:** Simultane Analyse multipler Abstimmungen
- **Statistische Validierung:** Korrelationsanalysen und Signifikanztests

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
poetry run pytest test_utils_grobes_eda.py -v
poetry run pytest test_utils_detailliertes_eda.py -v
poetry run pytest test_utils_abstimmungen_analyse.py -v
```

### Datenanalyse-Workflow
1. **Beginn:** `grobes_eda.ipynb` für allgemeine Trends
2. **Vertiefung:** `detailliertes_eda.ipynb` für gesellschaftliche Abstimmungen
3. **Spezifisch:** `Analyse_Einzelner_Abstimmungen.ipynb` für einzelne Vorlagen

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

- **Schweizer Schreibweise:** Durchgängig korrekte Terminologie
- **Professionelle Farbschemata:** RdYlGn für Ja/Nein-Visualisierungen
- **Konsistente Layouts:** Standardisierte Achsenbeschriftungen und Titel
- **Interaktive Elemente:** Anpassbare Parameter für verschiedene Analyseperspektiven

## 📝 Weiterführende Dokumentation

- **Technische Details:** Siehe `PROJEKT_ZUSAMMENFASSUNG.md`
- **Code-Dokumentation:** Inline-Docstrings in allen Utility-Modulen
- **Methodologie:** Wissenschaftliche Grundlagen in den Notebooks dokumentiert

## 🤝 Beitrag und Entwicklung

Dieses Projekt folgt wissenschaftlichen Entwicklungsstandards:
- Modulare Architektur für Erweiterbarkeit
- Umfassende Tests für Stabilität
- Dokumentierte APIs für Nachvollziehbarkeit
- Reproduzierbare Analysen für Validierung

---

**Entwickelt für die CDA2 Demokratie Challenge**  
*Professionelle Analyseplattform für Schweizer Abstimmungsdaten*
