"""
Utilities für das detaillierte EDA der gesellschaftsorientierten Abstimmungen.

Diese Datei enthält spezialisierte Funktionen für die detaillierte Analyse
gesellschaftsorientierter Abstimmungen in der Schweiz.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


def load_society_data(file_path: str) -> pd.DataFrame:
    """
    Lädt den Datensatz der gesellschaftsorientierten Abstimmungen.
    
    Args:
        file_path (str): Pfad zur CSV-Datei
        
    Returns:
        pd.DataFrame: Geladener und vorbereiteter Datensatz
        
    Raises:
        FileNotFoundError: Wenn die Datei nicht gefunden wird
    """
    try:
        df = pd.read_csv(file_path, sep=';', low_memory=False)
        
        # Standardisiere das Datum
        if 'datum' in df.columns:
            df['datum'] = pd.to_datetime(df['datum'], errors='coerce')
            df['year'] = df['datum'].dt.year
            
        return df
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Datei {file_path} wurde nicht gefunden.")


def define_social_keywords() -> Tuple[List[str], List[str]]:
    """
    Definiert Schlüsselwörter für gesellschaftsorientierte und ausschliessende Begriffe.
    
    Returns:
        Tuple[List[str], List[str]]: (Positive Keywords, Negative Keywords)
    """
    social_keywords = [
        # Soziales & Wohlfahrt
        'sozialhilfe', 'fürsorge', 'mieterschutz', 'mietrecht', 'mieter', 
        'sozialversicherung', 'sozialversicherungen', 'pflegefinanzierung', 'pflegeversicherung',
        
        # Familie & Generationen
        'alters', 'rentenalters', 'familienzulagen', 'elternurlaub', 'eltern', 'elternschaft', 
        'familienpolitik', 'generationen', 'jugend', 'jugendschutz', 'kinder',
        
        # Gesundheit & Pflege
        'krankenversicherung', 'gesundheitswesen', 'spitalfinanzierung', 
        'mutterschaftsversicherung', 'mutterschaftsurlaub',
        
        # Gleichstellung & Rechte
        'frau', 'gleichstellung', 'menschenrechte', 'bürgerrechte', 'zivilstand',
        
        # Integration & Migration
        'asylgesetz', 'migrationsfragen', 'einbürgerung', 'integrationsgesetz', 'sprachförderung',
        
        # Bildung & Kultur
        'bildung', 'schulgesetz',
        
        # Partizipation & Demokratie
        'volksrechte', 'zusammenleben',
        
        # Arbeitswelt & soziale Sicherung
        'arbeitnehmende', 'hinterlassenenversicherung', 'betreuungsgutschriften'
    ]
    
    non_social_keywords = [
        # Steuern & Finanzen
        'finanzordnung', 'mehrwertsteuer', 'besteuerung', 'steuerharmonisierung', 
        'mwst', 'gewinnsteuer', 'einkommensteuer', 'bundesfinanzen', 'bundeshaushalt',
        
        # Verkehr & Infrastruktur
        'nationalstrassen', 'strassenbau', 'verkehrsinfrastruktur', 'strassentransit', 
        'bahnverkehr', 'verkehr', 'ausbau',
        
        # Energie & Telekommunikation
        'energiepolitik', 'elektrizitätsversorgung', 'stromversorgung', 'telekommunikation',
        
        # Wirtschaft & Handel
        'wirtschaftsartikel', 'wirtschaftspolitik', 'finanzmarkt', 'zollgesetz', 
        'gewinn', 'aktiengesellschaften', 'import', 'export', 'zölle', 'bankengesetz',
        
        # Militär & Sicherheit
        'militärgesetz', 'militärdienst', 'militärorganisation',
        
        # Landwirtschaft & Subventionen
        'landwirtschaftsgesetz', 'agrarpolitik', 'landwirtschaftspolitik', 'subventionierung'
    ]
    
    return social_keywords, non_social_keywords


def classify_society_votes(df: pd.DataFrame, 
                         social_keywords: List[str] = None,
                         non_social_keywords: List[str] = None) -> pd.DataFrame:
    """
    Klassifiziert Abstimmungen als gesellschaftsorientiert basierend auf erweiterten Kriterien.
    
    Args:
        df (pd.DataFrame): Abstimmungsdatensatz
        social_keywords (List[str], optional): Positive Schlüsselwörter
        non_social_keywords (List[str], optional): Ausschliessende Schlüsselwörter
        
    Returns:
        pd.DataFrame: Datensatz mit 'society_oriented' Spalte
    """
    if social_keywords is None or non_social_keywords is None:
        social_keywords, non_social_keywords = define_social_keywords()
    
    def is_society_oriented(row):
        """Klassifiziert eine einzelne Abstimmung."""
        # Kombiniere relevante Textspalten
        text_fields = []
        for field in ['titel_kurz_d', 'titel_off_d', 'text_d']:
            if field in row.index:
                text_fields.append(str(row.get(field, '')).lower())
        
        combined_text = ' '.join(text_fields)
        
        # Prüfe positive Keywords
        has_social_keyword = any(keyword in combined_text for keyword in social_keywords)
        
        if has_social_keyword:
            # Prüfe ausschliessende Keywords
            has_non_social_keyword = any(keyword in combined_text for keyword in non_social_keywords)
            return not has_non_social_keyword
        
        return False
    
    df_copy = df.copy()
    df_copy['society_oriented'] = df_copy.apply(is_society_oriented, axis=1)
    
    return df_copy


def extract_canton_columns(df: pd.DataFrame) -> List[str]:
    """
    Extrahiert alle Kantonsspalten aus dem Datensatz.
    
    Args:
        df (pd.DataFrame): Abstimmungsdatensatz
        
    Returns:
        List[str]: Liste der Kantonsspalten
    """
    return [col for col in df.columns if col.endswith('-japroz')]


def calculate_canton_liberality_ranking(df: pd.DataFrame) -> pd.DataFrame:
    """
    Berechnet ein Ranking der Kantone nach Liberalität bei gesellschaftsorientierten Abstimmungen.
    
    Args:
        df (pd.DataFrame): Abstimmungsdatensatz mit society_oriented Spalte
        
    Returns:
        pd.DataFrame: Ranking mit Kanton und durchschnittlicher Ja-Quote
    """
    # Filtere gesellschaftsorientierte Abstimmungen
    society_votes = df[df['society_oriented'] == True].copy()
    
    # Extrahiere Kantonsspalten
    canton_cols = extract_canton_columns(society_votes)
    cantons = [col.split('-')[0] for col in canton_cols]
    
    # Konvertiere zu numerischen Werten
    for col in canton_cols:
        society_votes[col] = pd.to_numeric(society_votes[col], errors='coerce')
    
    # Berechne Durchschnitte
    canton_means = {}
    for canton, col in zip(cantons, canton_cols):
        mean_value = society_votes[col].mean()
        if not pd.isna(mean_value):
            canton_means[canton] = mean_value
    
    # Erstelle Ranking DataFrame
    ranking_df = pd.DataFrame({
        'Kanton': list(canton_means.keys()),
        'Durchschnittliche_Ja_Prozente': list(canton_means.values())
    })
    
    # Sortiere nach Liberalität (höhere Ja-Prozente = liberaler)
    ranking_df = ranking_df.sort_values('Durchschnittliche_Ja_Prozente', ascending=False)
    ranking_df['Rang'] = range(1, len(ranking_df) + 1)
    
    return ranking_df


def plot_canton_liberality_ranking(ranking_df: pd.DataFrame, 
                                 figsize: Tuple[int, int] = (12, 8)) -> None:
    """
    Visualisiert das Kantons-Liberalitäts-Ranking.
    
    Args:
        ranking_df (pd.DataFrame): Ranking-Datensatz
        figsize (Tuple[int, int]): Grösse der Grafik
    """
    plt.figure(figsize=figsize)
    
    # Erstelle Farbcodierung basierend auf Liberalität
    colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(ranking_df)))
    
    bars = plt.bar(ranking_df['Kanton'], ranking_df['Durchschnittliche_Ja_Prozente'], 
                   color=colors, edgecolor='black', linewidth=0.5)
    
    plt.title('Ranking der Kantone nach Liberalität\nbei gesellschaftsorientierten Abstimmungen', 
              fontsize=16, pad=20)
    plt.xlabel('Kanton', fontsize=12)
    plt.ylabel('Durchschnittliche Ja-Prozente (%)', fontsize=12)
    plt.axhline(y=50, color='red', linestyle='--', alpha=0.7, label='50%-Schwelle')
    
    # Füge Werte auf den Balken hinzu
    for bar, value in zip(bars, ranking_df['Durchschnittliche_Ja_Prozente']):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{value:.1f}%', ha='center', va='bottom', fontsize=9)
    
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.show()


def analyze_temporal_patterns(df: pd.DataFrame, 
                            period_column: str = 'year') -> Dict[str, any]:
    """
    Analysiert zeitliche Muster in gesellschaftsorientierten Abstimmungen.
    
    Args:
        df (pd.DataFrame): Abstimmungsdatensatz
        period_column (str): Spalte für Zeitangabe
        
    Returns:
        Dict[str, any]: Analyseergebnisse
    """
    society_votes = df[df['society_oriented'] == True].copy()
    
    if len(society_votes) < 2:
        return {"error": "Nicht genügend Daten für Zeitanalyse"}
    
    results = {}
    
    # Grundstatistiken
    results['total_votes'] = len(society_votes)
    results['time_span'] = (society_votes[period_column].max() - 
                           society_votes[period_column].min())
    results['mean_acceptance'] = society_votes['volkja-proz'].mean()
    results['median_acceptance'] = society_votes['volkja-proz'].median()
    
    # Trend-Analyse
    if period_column in society_votes.columns:
        from scipy.stats import pearsonr, linregress
        
        # Entferne NaN-Werte für Korrelation
        clean_data = society_votes[[period_column, 'volkja-proz']].dropna()
        
        if len(clean_data) >= 2:
            correlation, p_value = pearsonr(clean_data[period_column], 
                                          clean_data['volkja-proz'])
            
            # Lineare Regression für Trend
            slope, intercept, r_value, p_val_reg, std_err = linregress(
                clean_data[period_column], clean_data['volkja-proz'])
            
            results['correlation'] = correlation
            results['correlation_p_value'] = p_value
            results['trend_slope'] = slope
            results['trend_per_decade'] = slope * 10
            results['r_squared'] = r_value ** 2
    
    return results


def create_temporal_visualization(df: pd.DataFrame, 
                                figsize: Tuple[int, int] = (14, 10)) -> None:
    """
    Erstellt umfassende zeitliche Visualisierungen.
    
    Args:
        df (pd.DataFrame): Abstimmungsdatensatz
        figsize (Tuple[int, int]): Grösse der Grafik
    """
    society_votes = df[df['society_oriented'] == True].copy()
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle('Zeitliche Entwicklung gesellschaftsorientierter Abstimmungen', 
                fontsize=16, y=0.98)
    
    # 1. Scatter Plot mit Trendlinie
    axes[0, 0].scatter(society_votes['year'], society_votes['volkja-proz'], 
                      alpha=0.6, color='blue', s=50)
    
    # Trendlinie
    if len(society_votes) > 1:
        z = np.polyfit(society_votes['year'].dropna(), 
                      society_votes['volkja-proz'].dropna(), 1)
        p = np.poly1d(z)
        axes[0, 0].plot(society_votes['year'], p(society_votes['year']), 
                       "r--", alpha=0.8, linewidth=2)
    
    axes[0, 0].axhline(y=50, color='gray', linestyle=':', alpha=0.7)
    axes[0, 0].set_title('Annahmequoten im Zeitverlauf')
    axes[0, 0].set_xlabel('Jahr')
    axes[0, 0].set_ylabel('Ja-Prozente (%)')
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Histogramm der Annahmequoten
    axes[0, 1].hist(society_votes['volkja-proz'].dropna(), bins=20, 
                   color='green', alpha=0.7, edgecolor='black')
    axes[0, 1].axvline(x=50, color='red', linestyle='--', alpha=0.7)
    axes[0, 1].set_title('Verteilung der Annahmequoten')
    axes[0, 1].set_xlabel('Ja-Prozente (%)')
    axes[0, 1].set_ylabel('Häufigkeit')
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Abstimmungen pro Jahrzehnt
    if 'year' in society_votes.columns:
        society_votes['decade'] = (society_votes['year'] // 10) * 10
        decade_counts = society_votes['decade'].value_counts().sort_index()
        
        axes[1, 0].bar(decade_counts.index, decade_counts.values, 
                      width=8, color='orange', alpha=0.7, edgecolor='black')
        axes[1, 0].set_title('Anzahl Abstimmungen pro Jahrzehnt')
        axes[1, 0].set_xlabel('Jahrzehnt')
        axes[1, 0].set_ylabel('Anzahl Abstimmungen')
        axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    # 4. Gleitender Durchschnitt
    if len(society_votes) > 5:
        # Sortiere nach Jahr
        sorted_votes = society_votes.sort_values('year')
        
        # Berechne gleitenden Durchschnitt (5-Jahres-Fenster)
        rolling_mean = sorted_votes.set_index('year')['volkja-proz'].rolling(
            window=5, min_periods=3).mean()
        
        axes[1, 1].plot(rolling_mean.index, rolling_mean.values, 
                       color='purple', linewidth=2, label='5-Jahre Durchschnitt')
        axes[1, 1].axhline(y=50, color='gray', linestyle=':', alpha=0.7)
        axes[1, 1].set_title('Gleitender Durchschnitt der Annahmequoten')
        axes[1, 1].set_xlabel('Jahr')
        axes[1, 1].set_ylabel('Ja-Prozente (%)')
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].legend()
    
    plt.tight_layout()
    plt.show()


def validate_classification_sample(df: pd.DataFrame, 
                                 sample_size: int = 20) -> pd.DataFrame:
    """
    Validiert die automatische Klassifikation durch Stichprobe.
    
    Args:
        df (pd.DataFrame): Abstimmungsdatensatz
        sample_size (int): Grösse der Stichprobe
        
    Returns:
        pd.DataFrame: Stichprobe zur manuellen Überprüfung
    """
    # Stratifizierte Stichprobe
    society_sample = df[df['society_oriented'] == True].sample(
        min(sample_size // 2, len(df[df['society_oriented'] == True])))
    
    non_society_sample = df[df['society_oriented'] == False].sample(
        min(sample_size // 2, len(df[df['society_oriented'] == False])))
    
    validation_sample = pd.concat([society_sample, non_society_sample])
    
    # Relevante Spalten für Validierung
    validation_columns = ['anr', 'datum', 'titel_kurz_d', 'titel_off_d', 
                         'society_oriented', 'volkja-proz']
    
    available_columns = [col for col in validation_columns if col in validation_sample.columns]
    
    return validation_sample[available_columns].reset_index(drop=True)


def generate_summary_statistics(df: pd.DataFrame) -> Dict[str, any]:
    """
    Generiert umfassende Zusammenfassungsstatistiken.
    
    Args:
        df (pd.DataFrame): Abstimmungsdatensatz
        
    Returns:
        Dict[str, any]: Zusammenfassungsstatistiken
    """
    stats = {}
    
    # Grundlegende Zahlen
    stats['total_votes'] = len(df)
    stats['society_votes'] = df['society_oriented'].sum()
    stats['society_percentage'] = (stats['society_votes'] / stats['total_votes']) * 100
    
    # Annahmequoten
    society_data = df[df['society_oriented'] == True]['volkja-proz']
    other_data = df[df['society_oriented'] == False]['volkja-proz']
    
    stats['society_mean_acceptance'] = society_data.mean()
    stats['society_median_acceptance'] = society_data.median()
    stats['society_std_acceptance'] = society_data.std()
    
    stats['other_mean_acceptance'] = other_data.mean()
    stats['other_median_acceptance'] = other_data.median()
    stats['other_std_acceptance'] = other_data.std()
    
    # Zeitraum
    if 'year' in df.columns:
        stats['time_span_start'] = df['year'].min()
        stats['time_span_end'] = df['year'].max()
        stats['time_span_years'] = stats['time_span_end'] - stats['time_span_start']
    
    # Datenqualität
    stats['missing_dates'] = df['datum'].isna().sum()
    stats['missing_titles'] = df['titel_kurz_d'].isna().sum()
    stats['missing_results'] = df['volkja-proz'].isna().sum()
    
    return stats
