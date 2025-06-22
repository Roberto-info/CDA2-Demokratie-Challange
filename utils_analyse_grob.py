"""
Utilities für das grobe EDA der Schweizer Abstimmungsdaten.

Diese Datei enthält Hilfsfunktionen für die explorative Datenanalyse
der Schweizer Abstimmungsdaten, insbesondere für gesellschaftsorientierte
Abstimmungen.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from fontTools.misc.textTools import tostr
from scipy import stats
from typing import List, Dict, Tuple, Optional


def load_and_prepare_data(file_path: str) -> pd.DataFrame:
    """
    Lädt den Abstimmungsdatensatz und bereitet ihn für die Analyse vor.
    
    Args:
        file_path (str): Pfad zur CSV-Datei
        
    Returns:
        pd.DataFrame: Vorbereiteter Datensatz mit Datums- und Zeitraumspalten
        
    Raises:
        FileNotFoundError: Wenn die Datei nicht gefunden wird
        pd.errors.EmptyDataError: Wenn die Datei leer ist
    """
    try:
        df = pd.read_csv(file_path, sep=';', low_memory=False)
        
        # Konvertiere Datumsspalte
        df['datum'] = pd.to_datetime(df['datum'], format='%d.%m.%Y', errors='coerce')
        df['year'] = df['datum'].dt.year
        
        # Erstelle Zeitraumspalte
        df['period'] = df['year'].apply(assign_period)
        
        return df
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Datei {file_path} wurde nicht gefunden.")
    except pd.errors.EmptyDataError:
        raise pd.errors.EmptyDataError("Die Datei ist leer.")


def load_and_prepare_data_with_spec_period(file_path: str, years: int) -> pd.DataFrame:
    """
    Lädt den Abstimmungsdatensatz und bereitet ihn für die Analyse vor.

    Args:
        file_path (str): Pfad zur CSV-Datei
        years (int): zeitraum

    Returns:
        pd.DataFrame: Vorbereiteter Datensatz mit Datums- und Zeitraumspalten

    Raises:
        FileNotFoundError: Wenn die Datei nicht gefunden wird
        pd.errors.EmptyDataError: Wenn die Datei leer ist
    """
    try:
        df = pd.read_csv(file_path, sep=';', low_memory=False)

        # Konvertiere 'datum' sauber
        df['datum'] = pd.to_datetime(df['datum'], errors='coerce')
        df['year'] = df['datum'].dt.year

        # Zeitraum-Spalte mit robuster Funktion
        df['period'] = df['year'].apply(lambda y: assign_specific_period(y, years))

        return df

    except FileNotFoundError:
        raise FileNotFoundError(f"Datei {file_path} wurde nicht gefunden.")
    except pd.errors.EmptyDataError:
        raise pd.errors.EmptyDataError("Die Datei ist leer.")


def assign_period(year: float) -> str:
    """
    Weist einem Jahr einen Zeitraum zu.

    Args:
        year (float): Jahr als Zahl

    Returns:
        str: Zeitraum als String
    """
    if pd.isna(year):
        return "Unbekannt"
    elif year < 1920:
        return "1893-1919"
    elif year < 1950:
        return "1920-1949"
    elif year < 1980:
        return "1950-1979"
    elif year < 2010:
        return "1980-2009"
    else:
        return "2010-2025"


def assign_specific_period(year, years):
    if pd.isna(year):
        return "Unbekannt"

    start = int((year // years) * years)
    end = start + years - 1
    return f"{start}–{end}"

def extract_mid_year(period_str):
    try:
        start, end = map(int, period_str.split('–'))
        return (start + end) // 2
    except:
        return None


def identify_society_oriented_votes(df: pd.DataFrame, 
                                  social_keywords: List[str] = None) -> pd.DataFrame:
    """
    Identifiziert gesellschaftsorientierte Abstimmungen basierend auf Schlüsselwörtern.
    
    Args:
        df (pd.DataFrame): Abstimmungsdatensatz
        social_keywords (List[str], optional): Liste der Schlüsselwörter
        
    Returns:
        pd.DataFrame: Datensatz mit zusätzlicher Spalte 'society_oriented'
    """
    if social_keywords is None:
        social_keywords = [
            'gesellschaft', 'sozial', 'frauen', 'ehe', 'familie', 
            'bildung', 'gesundheit', 'migration', 'ausländer', 
            'gleichstellung', 'religion', 'kultur'        ]
    
    def is_society_oriented(row):
        """Hilfsfunktion zur Identifikation gesellschaftsorientierter Abstimmungen."""
        title = str(row['titel_kurz_d']).lower() + ' ' + str(row['titel_off_d']).lower()
        return any(keyword in title for keyword in social_keywords)
    
    df_copy = df.copy()
    
    # Prüfung auf leeren DataFrame
    if df_copy.empty:
        df_copy['society_oriented'] = pd.Series(dtype=bool)
        return df_copy
    
    df_copy['society_oriented'] = df_copy.apply(is_society_oriented, axis=1)
    
    return df_copy


def calculate_period_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Berechnet Statistiken für Abstimmungsergebnisse nach Zeitraum.
    
    Args:
        df (pd.DataFrame): Abstimmungsdatensatz
        
    Returns:
        pd.DataFrame: Statistiken nach Zeitraum
    """
    period_stats = df.groupby('period')['volkja-proz'].agg(['mean', 'median', 'count']).reset_index()
    period_stats.columns = ['Zeitraum', 'Durchschnitt', 'Median', 'Anzahl']
    
    return period_stats


def plot_acceptance_trend(df: pd.DataFrame, figsize: Tuple[int, int] = (12, 6)) -> None:
    """
    Erstellt ein Liniendiagramm des Trends der Annahmequoten im Zeitverlauf.
    
    Args:
        df (pd.DataFrame): Abstimmungsdatensatz
        figsize (Tuple[int, int]): Grösse der Grafik
    """
    plt.figure(figsize=figsize)
    sns.lineplot(data=df, x='year', y='volkja-proz', estimator='mean', ci=95)
    plt.title('Durchschnittliche Annahmequote im Zeitverlauf (1893-2025)')
    plt.xlabel('Jahr')
    plt.ylabel('Annahmequote (%)')
    plt.axhline(y=50, color='r', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()


def compare_society_vs_other_votes(df: pd.DataFrame, 
                                 figsize: Tuple[int, int] = (12, 6)) -> None:
    """
    Vergleicht Annahmequoten zwischen gesellschaftsorientierten und anderen Abstimmungen.
    
    Args:
        df (pd.DataFrame): Abstimmungsdatensatz mit 'society_oriented' Spalte
        figsize (Tuple[int, int]): Grösse der Grafik
    """
    society_vs_other = df.groupby(['period', 'society_oriented'])['volkja-proz'].mean().reset_index()
    society_vs_other_pivot = society_vs_other.pivot(
        index='period', 
        columns='society_oriented', 
        values='volkja-proz'
    )
    society_vs_other_pivot.columns = ['Andere Abstimmungen', 'Gesellschaftsorientierte Abstimmungen']

    plt.figure(figsize=figsize)
    society_vs_other_pivot.plot(kind='bar', figsize=figsize)
    plt.title('Annahmequoten: Gesellschaftsorientierte vs. Andere Abstimmungen')
    plt.xlabel('Zeitraum')
    plt.ylabel('Durchschnittliche Annahmequote (%)')
    plt.axhline(y=50, color='r', linestyle='--', alpha=0.7)
    plt.legend(title='Abstimmungstyp')
    plt.tight_layout()
    plt.show()


def analyze_cantonal_differences(df: pd.DataFrame, 
                               cantons: List[str] = None,
                               figsize: Tuple[int, int] = (14, 8)) -> None:
    """
    Analysiert kantonale Unterschiede bei gesellschaftsorientierten Abstimmungen.
    
    Args:
        df (pd.DataFrame): Abstimmungsdatensatz
        cantons (List[str], optional): Liste der zu analysierenden Kantone
        figsize (Tuple[int, int]): Grösse der Grafik
    """
    if cantons is None:
        cantons = ['zh', 'be', 'ge', 'ti', 'vs']
    
    # Filtere nur gesellschaftsorientierte Abstimmungen
    society_votes = df[df['society_oriented'] == True]
    
    canton_cols = [f'{canton}-japroz' for canton in cantons]
    canton_data = society_votes[['year'] + canton_cols].copy()

    # Konvertiere zu numerischen Werten
    for col in canton_cols:
        canton_data[col] = pd.to_numeric(canton_data[col], errors='coerce')

    # Entferne Zeilen mit fehlenden Werten
    canton_data = canton_data.dropna()

    if len(canton_data) > 0:
        plt.figure(figsize=figsize)
        for canton in cantons:
            sns.regplot(
                data=canton_data, 
                x='year', 
                y=f'{canton}-japroz', 
                label=canton.upper(), 
                scatter=False, 
                line_kws={"alpha": 0.7}
            )
        
        plt.title('Kantonale Unterschiede bei gesellschaftsorientierten Abstimmungen')
        plt.xlabel('Jahr')
        plt.ylabel('Annahmequote (%)')
        plt.axhline(y=50, color='r', linestyle='--', alpha=0.7)
        plt.legend(title='Kanton')
        plt.tight_layout()
        plt.show()
    else:
        print("Keine ausreichenden Daten für kantonale Vergleiche vorhanden.")


def calculate_correlation_time_acceptance(df: pd.DataFrame) -> Tuple[float, float, str]:
    """
    Berechnet die Korrelation zwischen Zeit und Annahmequote für gesellschaftsorientierte Abstimmungen.
    
    Args:
        df (pd.DataFrame): Abstimmungsdatensatz
        
    Returns:
        Tuple[float, float, str]: Korrelation, p-Wert und Interpretation
    """
    society_votes = df[df['society_oriented'] == True]
    
    if len(society_votes) < 2:
        return 0.0, 1.0, "Nicht genügend Daten für Korrelationsanalyse."
    
    correlation, p_value = stats.pearsonr(society_votes['year'], society_votes['volkja-proz'])
    
    # Interpretation
    if p_value < 0.05:
        if correlation > 0:
            interpretation = ("Es gibt eine statistisch signifikante positive Korrelation. "
                            "Liberales Abstimmungsverhalten hat im Laufe der Zeit zugenommen.")
        else:
            interpretation = ("Es gibt eine statistisch signifikante negative Korrelation. "
                            "Liberales Abstimmungsverhalten hat im Laufe der Zeit abgenommen.")
    else:
        interpretation = ("Es gibt keine statistisch signifikante Korrelation. "
                        "Die Daten liefern keine starken Belege für einen Trend.")
    
    return correlation, p_value, interpretation

def analyze_party_support(df: pd.DataFrame, 
                        liberal_parties: List[str] = None,
                        conservative_parties: List[str] = None,
                        figsize: Tuple[int, int] = (12, 6)) -> None:
    """
    Analysiert die Parteiunterstützung für gesellschaftsorientierte Abstimmungen.
    
    Die Unterstützung wird als prozentualer Anteil der Ja-Parolen
    innerhalb des liberalen und konservativen Lagers für jede Abstimmung berechnet.
    
    Args:
        df (pd.DataFrame): Abstimmungsdatensatz
        liberal_parties (List[str], optional): Liste liberaler Parteien
        conservative_parties (List[str], optional): Liste konservativer Parteien
        figsize (Tuple[int, int]): Grösse der Grafik
    """
    if liberal_parties is None:
        liberal_parties = ['p-fdp', 'p-glp', 'p-gps', 'p-sps']
    
    if conservative_parties is None:
        conservative_parties = ['p-svp', 'p-cvp', 'p-mitte', 'p-edu']
    
    society_votes = df[df['society_oriented'] == True].copy()
    
    # Erstelle ein temporäres DataFrame für die Berechnung
    support_df = pd.DataFrame(index=society_votes.index)

    # Konvertiere Parolen in einen Unterstützungswert (1 für Ja, 0 für Nein, NaN für andere)
    for party in liberal_parties + conservative_parties:
        if party in society_votes.columns:
            # 1 -> 1 (Ja)
            # 2 -> 0 (Nein)
            # 3 -> NaN (Stimmfreigabe)
            # 9999 -> NaN (Keine)
            support_df[party] = pd.to_numeric(society_votes[party], errors='coerce').replace({1: 1, 2: 0, 3: np.nan, 9999: np.nan})

    # Berechne durchschnittliche Unterstützung als Prozentsatz
    available_liberal_parties = [p for p in liberal_parties if p in support_df.columns]
    available_conservative_parties = [p for p in conservative_parties if p in support_df.columns]

    if available_liberal_parties:
        # mean() ignoriert NaNs standardmässig, was korrekt ist.
        society_votes['liberal_support'] = support_df[available_liberal_parties].mean(axis=1) * 100
    
    if available_conservative_parties:
        society_votes['conservative_support'] = support_df[available_conservative_parties].mean(axis=1) * 100

    # Plotte den Trend
    if 'liberal_support' in society_votes.columns and 'conservative_support' in society_votes.columns:
        plt.figure(figsize=figsize)
        
        # Filtere Zeilen, in denen beide Support-Werte NaN sind, um leere Plots zu vermeiden
        plot_data = society_votes.dropna(subset=['liberal_support', 'conservative_support'], how='all')

        if not plot_data.empty:
            sns.regplot(
                data=plot_data, 
                x='year', 
                y='liberal_support', 
                label='Liberale Parteien', 
                scatter=True, 
                scatter_kws={'alpha':0.3},
                line_kws={"color": "blue"}
            )
            sns.regplot(
                data=plot_data, 
                x='year', 
                y='conservative_support', 
                label='Konservative Parteien', 
                scatter=True, 
                scatter_kws={'alpha':0.3},
                line_kws={"color": "red"}
            )
            plt.title('Parteiunterstützung für gesellschaftsorientierte Abstimmungen')
            plt.xlabel('Jahr')
            plt.ylabel('Anteil Ja-Parolen im Lager (%)')
            plt.legend()
            plt.tight_layout()
            plt.show()
        else:
            print("Nicht genügend Daten für Parteiunterstützungsanalyse vorhanden.")
    else:
        print("Nicht genügend Daten für Parteiunterstützungsanalyse vorhanden.")