"""
Utilities für die Analyse und Visualisierung einzelner Abstimmungen.

Diese Datei enthält Funktionen für die kartographische Darstellung
und Analyse spezifischer Schweizer Abstimmungen.
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import warnings
warnings.filterwarnings('ignore')


def create_canton_mapping() -> Dict[str, str]:
    """
    Erstellt das Mapping zwischen Kantonskürzel und vollständigen Namen.
    
    Returns:
        Dict[str, str]: Mapping von Kürzel zu vollständigen Kantonsnamen
    """
    return {
        'zh': 'Zürich', 'be': 'Bern', 'lu': 'Luzern', 'ur': 'Uri', 'sz': 'Schwyz',
        'ow': 'Obwalden', 'nw': 'Nidwalden', 'gl': 'Glarus', 'zg': 'Zug',
        'fr': 'Fribourg', 'so': 'Solothurn', 'bs': 'Basel-Stadt',
        'bl': 'Basel-Landschaft', 'sh': 'Schaffhausen', 'ar': 'Appenzell Ausserrhoden',
        'ai': 'Appenzell Innerrhoden', 'sg': 'St. Gallen', 'gr': 'Graubünden',
        'ag': 'Aargau', 'tg': 'Thurgau', 'ti': 'Ticino', 'vd': 'Vaud',
        'vs': 'Valais', 'ne': 'Neuchâtel', 'ge': 'Genève', 'ju': 'Jura'
    }


def load_voting_data(data_path: str) -> pd.DataFrame:
    """
    Lädt den Abstimmungsdatensatz.
    
    Args:
        data_path (str): Pfad zur CSV-Datei
        
    Returns:
        pd.DataFrame: Abstimmungsdatensatz
        
    Raises:
        FileNotFoundError: Wenn die Datei nicht gefunden wird
    """
    try:
        df = pd.read_csv(data_path, sep=";")
        print(f"✅ Abstimmungsdaten erfolgreich geladen: {len(df):,} Abstimmungen")
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"Datei {data_path} wurde nicht gefunden.")
    except Exception as e:
        raise Exception(f"Fehler beim Laden der Daten: {e}")


def load_map_data(map_path: str) -> gpd.GeoDataFrame:
    """
    Lädt die Schweizer Kantonsgeometrien.
    
    Args:
        map_path (str): Pfad zur Shapefile
        
    Returns:
        gpd.GeoDataFrame: Kantonsgeometrien
        
    Raises:
        FileNotFoundError: Wenn die Datei nicht gefunden wird
    """
    try:
        gdf = gpd.read_file(map_path)
        print(f"✅ Kartendaten erfolgreich geladen: {len(gdf)} Kantone")
        return gdf
    except FileNotFoundError:
        raise FileNotFoundError(f"Shapefile {map_path} wurde nicht gefunden.")
    except Exception as e:
        raise Exception(f"Fehler beim Laden der Kartendaten: {e}")


def search_voting_by_title(df: pd.DataFrame, search_term: str, 
                          exact_match: bool = False) -> pd.DataFrame:
    """
    Sucht Abstimmungen basierend auf dem Titel.
    
    Args:
        df (pd.DataFrame): Abstimmungsdatensatz
        search_term (str): Suchbegriff
        exact_match (bool): Ob nach exakter Übereinstimmung gesucht werden soll
        
    Returns:
        pd.DataFrame: Gefilterte Abstimmungen
    """
    if exact_match:
        mask = df['titel_kurz_d'].str.strip().str.lower() == search_term.strip().lower()
    else:
        mask = df['titel_kurz_d'].str.contains(search_term, case=False, regex=True, na=False)
    
    result = df[mask]
    print(f"🔍 Suche nach '{search_term}': {len(result)} Treffer gefunden")
    
    if len(result) > 0:
        print("📋 Gefundene Abstimmungen:")
        for idx, row in result.iterrows():
            date_str = row.get('datum', 'Unbekannt')
            print(f"   • {date_str}: {row['titel_kurz_d']}")
    
    return result


def filter_for_abstimmung(df: pd.DataFrame, abstimmung: str) -> pd.DataFrame:
    """
    Filtert den Datensatz nach einer spezifischen Abstimmung.
    
    Args:
        df (pd.DataFrame): Abstimmungsdatensatz
        abstimmung (str): Suchbegriff für die Abstimmung
        
    Returns:
        pd.DataFrame: Gefilterte Daten mit nur den Ja-Prozent-Spalten
        
    Raises:
        ValueError: Wenn keine passende Abstimmung gefunden wird
    """
    # Suche nach passenden Abstimmungen
    row_filter = df['titel_kurz_d'].str.contains(abstimmung, case=False, regex=True, na=False)
    
    if not row_filter.any():
        # Versuche auch in anderen Titelspalten zu suchen
        if 'titel_off_d' in df.columns:
            row_filter = df['titel_off_d'].str.contains(abstimmung, case=False, regex=True, na=False)
    
    if not row_filter.any():
        available_titles = df['titel_kurz_d'].dropna().head(10).tolist()
        raise ValueError(f"Keine Abstimmung mit dem Begriff '{abstimmung}' gefunden.\n"
                        f"Verfügbare Titel (Auswahl): {available_titles}")
    
    # Filtere Ja-Prozent-Spalten
    col_filter = df.filter(regex='-japroz', axis=1).columns
    
    if len(col_filter) == 0:
        raise ValueError("Keine kantonalen Ja-Prozent-Spalten im Datensatz gefunden.")
    
    # Zeige gefundene Abstimmungen
    found_titles = df.loc[row_filter, 'titel_kurz_d'].tolist()
    print(f"🎯 Gefundene Abstimmung(en): {found_titles}")
    
    return df.loc[row_filter, col_filter]


def merge_data_to_plot(df_filtered_abstimmungen: pd.DataFrame, 
                      df_schweizer_karte: gpd.GeoDataFrame,
                      kanton_map: Dict[str, str] = None) -> gpd.GeoDataFrame:
    """
    Verknüpft Abstimmungsdaten mit Kartendaten für die Visualisierung.
    
    Args:
        df_filtered_abstimmungen (pd.DataFrame): Gefilterte Abstimmungsdaten
        df_schweizer_karte (gpd.GeoDataFrame): Kantonsgeometrien
        kanton_map (Dict[str, str], optional): Mapping von Kürzeln zu Namen
        
    Returns:
        gpd.GeoDataFrame: Verknüpfte Daten für die Kartenvisualisierung
        
    Raises:
        ValueError: Wenn keine Abstimmungsdaten vorhanden sind
    """
    if df_filtered_abstimmungen.empty:
        raise ValueError("Keine Abstimmungsdaten zum Verknüpfen vorhanden!")
    
    if kanton_map is None:
        kanton_map = create_canton_mapping()
    
    # Falls mehrere Zeilen vorhanden sind, nimm die erste
    if len(df_filtered_abstimmungen) > 1:
        print(f"⚠️ Mehrere Abstimmungen gefunden, verwende die erste.")
    
    erste_zeile = df_filtered_abstimmungen.iloc[0]
    
    # Entferne das '-japroz' Suffix von den Spaltenbezeichnungen
    ja_stimmen = erste_zeile.rename(lambda x: x.replace('-japroz', ''))
    
    # Erstelle DataFrame mit Kantonsdaten
    ja_df = pd.DataFrame({
        'Kürzel': ja_stimmen.index,
        'Ja-Prozent': ja_stimmen.values
    })
    
    # Konvertiere zu numerischen Werten
    ja_df['Ja-Prozent'] = pd.to_numeric(ja_df['Ja-Prozent'], errors='coerce')
    
    # Mappe Kürzel zu vollständigen Namen
    ja_df['NAME'] = ja_df['Kürzel'].map(kanton_map)
    
    # Entferne Zeilen ohne gültiges Mapping
    ja_df = ja_df.dropna(subset=['NAME'])
    
    # Verknüpfe mit Kartendaten
    merged = df_schweizer_karte.merge(ja_df, on='NAME', how='left')
    
    # Statistiken ausgeben
    valid_data = merged['Ja-Prozent'].notna().sum()
    total_cantons = len(merged)
    
    print(f"📊 Datenverknüpfung: {valid_data}/{total_cantons} Kantone mit gültigen Daten")
    
    if valid_data == 0:
        raise ValueError("Keine gültigen Kantonsdaten nach der Verknüpfung vorhanden!")
    
    return merged


def create_color_scheme(data_values: pd.Series, 
                       color_map: str = 'RdYlGn') -> Tuple[mcolors.Normalize, cm.ScalarMappable]:
    """
    Erstellt ein Farbschema für die Kartenvisualisierung.
    
    Args:
        data_values (pd.Series): Datenwerte für die Farbcodierung
        color_map (str): Name der Colormap
        
    Returns:
        Tuple[mcolors.Normalize, cm.ScalarMappable]: Normalizer und ScalarMappable
    """
    # Entferne NaN-Werte für Min/Max-Berechnung
    clean_values = data_values.dropna()
    
    if len(clean_values) == 0:
        # Fallback für leere Daten
        vmin, vmax = 0, 100
    else:
        # Verwende den Datenbereich mit kleinem Puffer
        vmin = max(0, clean_values.min() - 5)
        vmax = min(100, clean_values.max() + 5)
    
    # Stelle sicher, dass der Bereich sinnvoll ist
    if vmax <= vmin:
        vmin, vmax = 0, 100
    
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    cmap = cm.get_cmap(color_map)
    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    sm._A = []  # Dummy für ScalarMappable
    
    return norm, sm


def plot_abstimmungen_schweiz(df_abstimmungen: pd.DataFrame,
                            schweizer_karte: gpd.GeoDataFrame,
                            abstimmung: str,
                            figsize: Tuple[int, int] = (14, 10),
                            color_map: str = 'RdYlGn',
                            show_statistics: bool = True) -> None:
    """
    Erstellt eine Karte der Schweiz mit Abstimmungsergebnissen.
    
    Args:
        df_abstimmungen (pd.DataFrame): Abstimmungsdatensatz
        schweizer_karte (gpd.GeoDataFrame): Kantonsgeometrien
        abstimmung (str): Suchbegriff für die Abstimmung
        figsize (Tuple[int, int]): Grösse der Grafik
        color_map (str): Colormap für die Darstellung
        show_statistics (bool): Ob Statistiken angezeigt werden sollen
    """
    try:
        # Filtere Abstimmungsdaten
        filtered_abstimmungen = filter_for_abstimmung(df_abstimmungen, abstimmung)
        
        # Verknüpfe mit Kartendaten
        data_to_plot = merge_data_to_plot(filtered_abstimmungen, schweizer_karte)
        
        # Erstelle Farbschema
        norm, sm = create_color_scheme(data_to_plot['Ja-Prozent'], color_map)
        
        # Erstelle die Karte
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plotte die Kantone
        data_to_plot.plot(
            column='Ja-Prozent',
            cmap=color_map,
            linewidth=0.8,
            edgecolor='black',
            ax=ax,
            legend=False,
            missing_kwds={'color': 'lightgrey', 'alpha': 0.5}
        )
          # Füge Colorbar hinzu
        cbar = fig.colorbar(sm, ax=ax, shrink=0.6, pad=0.02)
        cbar.set_label("Ja-Stimmen (%)", fontsize=12)
        
        # Titel und Layout
        full_title = filtered_abstimmungen.index[0] if not filtered_abstimmungen.empty else abstimmung
        ax.set_title(f"Abstimmungsergebnisse nach Kanton\n{abstimmung}", 
                    fontsize=16, pad=20, weight='bold')
        ax.axis("off")
        
        # Füge Kantonsbezeichnungen hinzu (optional)
        for idx, row in data_to_plot.iterrows():
            if pd.notna(row['Ja-Prozent']):
                # Berechne Zentroid für Textplatzierung
                centroid = row.geometry.centroid
                ax.text(centroid.x, centroid.y, f"{row['Ja-Prozent']:.0f}%", 
                       ha='center', va='center', fontsize=8, weight='bold',
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))

        # Statistiken anzeigen
        if show_statistics:
            valid_data = data_to_plot['Ja-Prozent'].dropna()
            if len(valid_data) > 0:
                stats_text = (
                    f"Durchschnitt: {valid_data.mean():.1f}%\n"
                    f"Median: {valid_data.median():.1f}%\n"
                    f"Min: {valid_data.min():.1f}% | Max: {valid_data.max():.1f}%\n"
                    f"Kantone mit Daten: {len(valid_data)}/26"
                )
                ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                       fontsize=10, verticalalignment='top',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
          # Layout optimieren
        fig.subplots_adjust(right=0.85)
        plt.tight_layout()
        plt.show()
        
        # Zusätzliche Auswertung ausgeben
        if show_statistics:
            print_voting_statistics(data_to_plot, abstimmung)
            
    except Exception as e:
        print(f"❌ Fehler bei der Kartenvisualisierung: {e}")
        raise


def print_voting_statistics(data: gpd.GeoDataFrame, abstimmung: str) -> None:
    """
    Gibt detaillierte Statistiken zu einer Abstimmung aus.
    
    Args:
        data (gpd.GeoDataFrame): Verknüpfte Abstimmungs- und Kartendaten
        abstimmung (str): Name der Abstimmung
    """
    valid_data = data['Ja-Prozent'].dropna()
    
    if len(valid_data) == 0:
        print("❌ Keine gültigen Daten für Statistikausgabe")
        return
    
    print(f"\n📊 DETAILLIERTE STATISTIKEN: {abstimmung}")
    print("=" * 60)
    
    # Grundstatistiken
    print(f"Durchschnitt: {valid_data.mean():.2f}%")
    print(f"Median: {valid_data.median():.2f}%")
    print(f"Standardabweichung: {valid_data.std():.2f}%")
    print(f"Spannweite: {valid_data.max() - valid_data.min():.1f}%")
    
    # Extremwerte
    max_idx = valid_data.idxmax()
    min_idx = valid_data.idxmin()
    
    max_canton = data.loc[max_idx, 'NAME'] if 'NAME' in data.columns else 'Unbekannt'
    min_canton = data.loc[min_idx, 'NAME'] if 'NAME' in data.columns else 'Unbekannt'
    
    print(f"\nHöchste Zustimmung: {max_canton} ({valid_data.max():.1f}%)")
    print(f"Niedrigste Zustimmung: {min_canton} ({valid_data.min():.1f}%)")
    
    # Annahme-/Ablehnungsverteilung
    angenommen = (valid_data >= 50).sum()
    abgelehnt = (valid_data < 50).sum()
    
    print(f"\nKantonale Verteilung:")
    print(f"Angenommen: {angenommen} Kantone ({angenommen/len(valid_data)*100:.1f}%)")
    print(f"Abgelehnt: {abgelehnt} Kantone ({abgelehnt/len(valid_data)*100:.1f}%)")
    
    # Kategorisierung
    sehr_hoch = (valid_data >= 70).sum()
    hoch = ((valid_data >= 60) & (valid_data < 70)).sum()
    mittel = ((valid_data >= 40) & (valid_data < 60)).sum()
    niedrig = (valid_data < 40).sum()
    
    print(f"\nZustimmungskategorien:")
    print(f"Sehr hoch (≥70%): {sehr_hoch} Kantone")
    print(f"Hoch (60-69%): {hoch} Kantone")
    print(f"Mittel (40-59%): {mittel} Kantone")
    print(f"Niedrig (<40%): {niedrig} Kantone")
    
    print("=" * 60)


def create_comparison_plot(df_abstimmungen: pd.DataFrame,
                          abstimmungen: List[str],
                          figsize: Tuple[int, int] = (15, 10)) -> None:
    """
    Erstellt einen Vergleich mehrerer Abstimmungen.
    
    Args:
        df_abstimmungen (pd.DataFrame): Abstimmungsdatensatz
        abstimmungen (List[str]): Liste der zu vergleichenden Abstimmungen
        figsize (Tuple[int, int]): Grösse der Grafik
        
    Raises:
        ValueError: Wenn weniger als 2 Abstimmungen für Vergleich übergeben werden
    """
    if len(abstimmungen) < 2:
        raise ValueError("Mindestens 2 Abstimmungen sind für einen Vergleich erforderlich!")
    
    if len(abstimmungen) > 6:
        print("⚠️ Mehr als 6 Abstimmungen können unübersichtlich werden. Zeige nur die ersten 6.")
        abstimmungen = abstimmungen[:6]
    
    # Sammle Daten für alle Abstimmungen
    all_data = {}
    kanton_map = create_canton_mapping()
    
    for abstimmung in abstimmungen:
        try:
            # Filtere Daten für diese Abstimmung
            filtered = filter_for_abstimmung(df_abstimmungen, abstimmung)
            
            if filtered.empty:
                print(f"⚠️ Keine Daten für '{abstimmung}' gefunden, überspringe...")
                continue
            
            # Extrahiere Ja-Prozent-Werte
            erste_zeile = filtered.iloc[0]
            ja_stimmen = erste_zeile.rename(lambda x: x.replace('-japroz', ''))
            
            # Konvertiere zu DataFrame
            ja_df = pd.DataFrame({
                'Kürzel': ja_stimmen.index,
                'Ja-Prozent': pd.to_numeric(ja_stimmen.values, errors='coerce')
            })
            
            # Mappe zu Kantonsnamen
            ja_df['Kanton'] = ja_df['Kürzel'].map(kanton_map)
            ja_df = ja_df.dropna(subset=['Kanton', 'Ja-Prozent'])
            
            # Speichere Daten
            all_data[abstimmung] = ja_df.set_index('Kanton')['Ja-Prozent']
            
        except Exception as e:
            print(f"❌ Fehler bei Abstimmung '{abstimmung}': {e}")
            continue
    
    if len(all_data) < 2:
        raise ValueError("Nicht genügend gültige Abstimmungen für Vergleich gefunden!")
    
    # Erstelle Subplots
    n_plots = len(all_data)
    cols = min(3, n_plots)
    rows = (n_plots + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=figsize)
    
    # Behandle den Fall eines einzelnen Subplots
    if n_plots == 1:
        axes = [axes]
    elif rows == 1:
        axes = axes if isinstance(axes, np.ndarray) else [axes]
    else:
        axes = axes.flatten()
    
    # Erstelle Balkendiagramme für jede Abstimmung
    colors = plt.cm.Set3(np.linspace(0, 1, n_plots))
    
    for idx, (abstimmung, data) in enumerate(all_data.items()):
        ax = axes[idx]
        
        # Sortiere Kantone nach Ja-Stimmen-Anteil
        sorted_data = data.sort_values(ascending=True)
        
        # Erstelle Balkendiagramm
        bars = ax.barh(range(len(sorted_data)), sorted_data.values, 
                      color=colors[idx], alpha=0.7, edgecolor='black', linewidth=0.5)
        
        # Gestalte das Diagramm
        ax.set_yticks(range(len(sorted_data)))
        ax.set_yticklabels(sorted_data.index, fontsize=8)
        ax.set_xlabel('Ja-Stimmen (%)', fontsize=10)
        ax.set_title(f"{abstimmung[:40]}{'...' if len(abstimmung) > 40 else ''}", 
                    fontsize=11, weight='bold', pad=10)
        
        # Füge 50%-Linie hinzu
        ax.axvline(x=50, color='red', linestyle='--', alpha=0.8, linewidth=1.5)
        
        # Setze x-Achsen-Limits
        ax.set_xlim(0, 100)
        
        # Füge Gitter hinzu
        ax.grid(axis='x', alpha=0.3)
        
        # Statistiken hinzufügen
        mean_val = sorted_data.mean()
        ax.text(0.02, 0.98, f'⌀ {mean_val:.1f}%', transform=ax.transAxes,
                fontsize=9, verticalalignment='top', weight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        # Färbe Balken je nach Annahme/Ablehnung
        for bar, value in zip(bars, sorted_data.values):
            if value >= 50:
                bar.set_color('green')
                bar.set_alpha(0.6)
            else:
                bar.set_color('red')
                bar.set_alpha(0.6)
    
    # Verstecke leere Subplots
    for idx in range(n_plots, len(axes)):
        axes[idx].set_visible(False)
    
    # Layout optimieren
    plt.tight_layout(pad=2.0)
    plt.suptitle('Kantonaler Vergleich der Abstimmungsergebnisse', 
                fontsize=16, weight='bold', y=0.98)
    plt.subplots_adjust(top=0.93)
    plt.show()
    
    # Korrelationsanalyse erstellen
    create_correlation_analysis(all_data)
    
    # Zusammenfassungsstatistiken ausgeben
    print_comparison_statistics(all_data)


def create_correlation_analysis(all_data: Dict[str, pd.Series]) -> None:
    """
    Erstellt eine Korrelationsanalyse zwischen verschiedenen Abstimmungen.
    
    Args:
        all_data (Dict[str, pd.Series]): Abstimmungsdaten nach Namen
    """
    if len(all_data) < 2:
        return
    
    # Erstelle DataFrame mit allen Abstimmungen
    correlation_df = pd.DataFrame(all_data)
    
    # Berechne Korrelationsmatrix
    correlation_matrix = correlation_df.corr()
    
    # Visualisiere Korrelationsmatrix
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Heatmap erstellen
    im = ax.imshow(correlation_matrix.values, cmap='RdYlBu_r', aspect='auto', vmin=-1, vmax=1)
    
    # Achsenbeschriftungen
    ax.set_xticks(range(len(correlation_matrix.columns)))
    ax.set_yticks(range(len(correlation_matrix.index)))
    ax.set_xticklabels([col[:30] + '...' if len(col) > 30 else col 
                       for col in correlation_matrix.columns], rotation=45, ha='right')
    ax.set_yticklabels([idx[:30] + '...' if len(idx) > 30 else idx 
                       for idx in correlation_matrix.index])
    
    # Korrelationswerte in Zellen einfügen
    for i in range(len(correlation_matrix.index)):
        for j in range(len(correlation_matrix.columns)):
            value = correlation_matrix.iloc[i, j]
            if not np.isnan(value):
                color = 'white' if abs(value) > 0.5 else 'black'
                ax.text(j, i, f'{value:.2f}', ha='center', va='center', 
                       color=color, weight='bold', fontsize=10)
    
    # Colorbar hinzufügen
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Korrelationskoeffizient', fontsize=12)
    
    # Titel und Layout
    ax.set_title('Korrelationsmatrix der Abstimmungsergebnisse', 
                fontsize=14, weight='bold', pad=20)
    
    plt.tight_layout()
    plt.show()
    
    # Stärkste Korrelationen ausgeben
    print("\n🔗 KORRELATIONSANALYSE")
    print("=" * 50)
    
    # Finde stärkste positive und negative Korrelationen
    mask = np.triu(np.ones_like(correlation_matrix, dtype=bool), k=1)
    correlations = correlation_matrix.where(mask).stack().sort_values(key=abs, ascending=False)
    
    print("Stärkste Korrelationen:")
    for (var1, var2), corr in correlations.head(5).items():
        if not np.isnan(corr):
            correlation_strength = "sehr stark" if abs(corr) > 0.8 else "stark" if abs(corr) > 0.6 else "mittel"
            direction = "positive" if corr > 0 else "negative"
            print(f"• {var1[:25]}... ↔ {var2[:25]}...: {corr:.3f} ({direction}, {correlation_strength})")


def print_comparison_statistics(all_data: Dict[str, pd.Series]) -> None:
    """
    Gibt Vergleichsstatistiken für mehrere Abstimmungen aus.
    
    Args:
        all_data (Dict[str, pd.Series]): Abstimmungsdaten nach Namen
    """
    print("\n📊 VERGLEICHSSTATISTIKEN")
    print("=" * 60)
    
    # Gesamtstatistiken
    for name, data in all_data.items():
        valid_data = data.dropna()
        if len(valid_data) > 0:
            angenommen = (valid_data >= 50).sum()
            total = len(valid_data)
            print(f"\n{name[:40]}{'...' if len(name) > 40 else ''}:")
            print(f"  Durchschnitt: {valid_data.mean():.1f}%")
            print(f"  Annahme: {angenommen}/{total} Kantone ({angenommen/total*100:.1f}%)")
            print(f"  Spannweite: {valid_data.min():.1f}% - {valid_data.max():.1f}%")
    
    # Vergleichende Analyse
    all_means = [data.dropna().mean() for data in all_data.values() if len(data.dropna()) > 0]
    all_acceptances = [(data.dropna() >= 50).sum() / len(data.dropna()) * 100 
                      for data in all_data.values() if len(data.dropna()) > 0]
    
    if all_means:
        print(f"\n🎯 ÜBERGEORDNETE TRENDS:")
        print(f"Durchschnittliche Zustimmung über alle Abstimmungen: {np.mean(all_means):.1f}%")
        print(f"Durchschnittliche Annahmequote: {np.mean(all_acceptances):.1f}%")
        print(f"Variabilität zwischen Abstimmungen: {np.std(all_means):.1f}%")
    
    print("=" * 60)
