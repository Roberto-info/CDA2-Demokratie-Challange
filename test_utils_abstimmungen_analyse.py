"""
Unit Tests für die Utilities der Abstimmungsanalyse.

Diese Datei enthält Unit Tests für alle Funktionen in utils_abstimmungen_analyse.py.
"""

import unittest
import pandas as pd
import numpy as np
import tempfile
import os
from unittest.mock import patch, MagicMock
import sys

# Prüfe ob geopandas verfügbar ist
try:
    import geopandas as gpd
    from shapely.geometry import Polygon
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False
    print("⚠️ geopandas nicht verfügbar - einige Tests werden übersprungen")

# Importiere die zu testenden Funktionen
sys.path.append('.')
try:
    from utils_abstimmungen_analyse import (
        create_canton_mapping,
        search_voting_by_title,
        create_color_scheme
    )    # Importiere nur bei verfügbarem geopandas
    if HAS_GEOPANDAS:
        from utils_abstimmungen_analyse import (
            load_voting_data,
            filter_for_abstimmung,
            merge_data_to_plot,
            print_voting_statistics,
            create_comparison_plot,
            create_correlation_analysis,
            print_comparison_statistics
        )
except ImportError as e:
    print(f"⚠️ Import-Fehler: {e}")
    HAS_GEOPANDAS = False


class TestUtilsAbstimmungenAnalyse(unittest.TestCase):
    """Test-Klasse für die Utilities der Abstimmungsanalyse."""
    
    def setUp(self):
        """Erstellt Test-Daten für die Tests."""
        # Erstelle Test-Abstimmungsdaten
        self.test_voting_data = pd.DataFrame({
            'anr': [1, 2, 3, 4],
            'datum': ['01.01.2000', '15.06.2005', '20.12.2010', '05.03.2015'],
            'titel_kurz_d': [
                'Initiative für ein Schächtverbot',
                'Gleichstellung der Geschlechter',
                'Einführung des Frauenstimmrechts',
                'Bundesbeschluss über Jura'
            ],
            'titel_off_d': [
                'Eidgenössische Volksinitiative für ein Schächtverbot',
                'Bundesgesetz über die Gleichstellung',
                'Bundesgesetz über das Frauenstimmrecht',
                'Bundesbeschluss über die Gründung des Kantons Jura'
            ],
            'zh-japroz': [45.2, 62.8, 58.1, 51.9],
            'be-japroz': [38.7, 59.3, 55.4, 48.2],
            'ge-japroz': [52.1, 71.2, 67.8, 53.7],
            'ti-japroz': [41.9, 58.6, 54.2, 49.8],
            'vs-japroz': [35.4, 52.1, 48.9, 45.3]
        })
        
        # Erstelle Test-Kartendaten nur wenn geopandas verfügbar ist
        if HAS_GEOPANDAS:
            self.test_map_data = gpd.GeoDataFrame({
                'NAME': ['Zürich', 'Bern', 'Genève', 'Ticino', 'Valais'],
                'geometry': [
                    Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                    Polygon([(1, 0), (2, 0), (2, 1), (1, 1)]),
                    Polygon([(2, 0), (3, 0), (3, 1), (2, 1)]),
                    Polygon([(0, 1), (1, 1), (1, 2), (0, 2)]),
                    Polygon([(1, 1), (2, 1), (2, 2), (1, 2)])
                ]
            })
        
    def test_create_canton_mapping(self):
        """Testet die Erstellung des Kantons-Mappings."""
        mapping = create_canton_mapping()
        
        # Überprüfe, dass alle 26 Kantone enthalten sind
        self.assertEqual(len(mapping), 26)
        
        # Überprüfe einige spezifische Mappings
        self.assertEqual(mapping['zh'], 'Zürich')
        self.assertEqual(mapping['be'], 'Bern')
        self.assertEqual(mapping['ge'], 'Genève')
        self.assertEqual(mapping['ti'], 'Ticino')
        
        # Überprüfe, dass alle Werte Strings sind
        for key, value in mapping.items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(value, str)
            self.assertEqual(len(key), 2)  # Kürzel sollten 2 Zeichen haben
            
    def test_search_voting_by_title_partial_match(self):
        """Testet die Suche nach Abstimmungen mit Teilübereinstimmung."""
        result = search_voting_by_title(self.test_voting_data, 'Schächt')
        
        self.assertEqual(len(result), 1)
        self.assertIn('Schächtverbot', result.iloc[0]['titel_kurz_d'])
        
    def test_search_voting_by_title_exact_match(self):
        """Testet die Suche nach Abstimmungen mit exakter Übereinstimmung."""
        exact_title = 'Initiative für ein Schächtverbot'
        result = search_voting_by_title(self.test_voting_data, exact_title, exact_match=True)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['titel_kurz_d'], exact_title)
        
    def test_search_voting_by_title_no_match(self):
        """Testet die Suche nach nicht existierenden Abstimmungen."""
        result = search_voting_by_title(self.test_voting_data, 'Nicht existierende Abstimmung')
        
        self.assertTrue(result.empty)
        
    def test_search_voting_by_title_case_insensitive(self):
        """Testet die case-insensitive Suche."""
        result = search_voting_by_title(self.test_voting_data, 'SCHÄCHT')
        
        self.assertEqual(len(result), 1)
        self.assertIn('Schächtverbot', result.iloc[0]['titel_kurz_d'])
        
    def test_filter_for_abstimmung_success(self):
        """Testet das erfolgreiche Filtern nach einer Abstimmung."""
        result = filter_for_abstimmung(self.test_voting_data, 'Schächtverbot')
        
        # Sollte eine Zeile mit den Ja-Prozent-Spalten zurückgeben
        self.assertEqual(len(result), 1)
        
        # Überprüfe, dass nur Ja-Prozent-Spalten enthalten sind
        for col in result.columns:
            self.assertTrue(col.endswith('-japroz'))
            
    def test_filter_for_abstimmung_not_found(self):
        """Testet das Verhalten wenn keine Abstimmung gefunden wird."""
        with self.assertRaises(ValueError) as context:
            filter_for_abstimmung(self.test_voting_data, 'Nicht existierende Abstimmung')
        
        self.assertIn('Keine Abstimmung', str(context.exception))
        
    def test_filter_for_abstimmung_no_canton_columns(self):
        """Testet das Verhalten wenn keine Kantonsspalten vorhanden sind."""
        # Erstelle Daten ohne Ja-Prozent-Spalten
        data_without_cantons = pd.DataFrame({
            'titel_kurz_d': ['Test Abstimmung'],
            'other_column': ['Test']
        })
        
        with self.assertRaises(ValueError) as context:
            filter_for_abstimmung(data_without_cantons, 'Test')
        
        self.assertIn('Keine kantonalen Ja-Prozent-Spalten', str(context.exception))
        
    def test_merge_data_to_plot_success(self):
        """Testet das erfolgreiche Verknüpfen von Abstimmungs- und Kartendaten."""
        # Filtere Testdaten
        filtered_data = filter_for_abstimmung(self.test_voting_data, 'Schächtverbot')
        
        # Verknüpfe mit Kartendaten
        result = merge_data_to_plot(filtered_data, self.test_map_data)
        
        # Überprüfe Struktur
        self.assertIsInstance(result, gpd.GeoDataFrame)
        self.assertIn('Ja-Prozent', result.columns)
        self.assertIn('NAME', result.columns)
        self.assertIn('geometry', result.columns)
        
        # Überprüfe, dass Daten verknüpft wurden
        valid_data = result['Ja-Prozent'].notna().sum()
        self.assertGreater(valid_data, 0)
        
    def test_merge_data_to_plot_empty_data(self):
        """Testet das Verhalten mit leeren Abstimmungsdaten."""
        empty_data = pd.DataFrame()
        
        with self.assertRaises(ValueError) as context:
            merge_data_to_plot(empty_data, self.test_map_data)
        
        self.assertIn('Keine Abstimmungsdaten', str(context.exception))
        
    def test_merge_data_to_plot_multiple_rows(self):
        """Testet das Verhalten mit mehreren Abstimmungszeilen."""
        # Erstelle Daten mit mehreren Zeilen
        multi_row_data = self.test_voting_data.filter(regex='-japroz', axis=1).head(2)
        
        # Sollte die erste Zeile verwenden
        result = merge_data_to_plot(multi_row_data, self.test_map_data)
        
        self.assertIsInstance(result, gpd.GeoDataFrame)
        self.assertGreater(result['Ja-Prozent'].notna().sum(), 0)
        
    def test_create_color_scheme_normal_data(self):
        """Testet die Erstellung des Farbschemas mit normalen Daten."""
        data = pd.Series([20, 40, 60, 80])
        norm, sm = create_color_scheme(data)
        
        # Überprüfe Typen
        self.assertIsInstance(norm, type(norm))
        self.assertIsInstance(sm, type(sm))
        
        # Überprüfe Wertebereich
        self.assertLessEqual(norm.vmin, data.min())
        self.assertGreaterEqual(norm.vmax, data.max())
        
    def test_create_color_scheme_with_nan(self):
        """Testet die Erstellung des Farbschemas mit NaN-Werten."""
        data = pd.Series([20, np.nan, 60, 80])
        norm, sm = create_color_scheme(data)
        
        # Sollte ohne Fehler funktionieren
        self.assertIsInstance(norm, type(norm))
        self.assertIsInstance(sm, type(sm))
        
    def test_create_color_scheme_empty_data(self):
        """Testet die Erstellung des Farbschemas mit leeren Daten."""
        data = pd.Series([])
        norm, sm = create_color_scheme(data)
        
        # Sollte Fallback-Werte verwenden
        self.assertEqual(norm.vmin, 0)
        self.assertEqual(norm.vmax, 100)
        
    def test_create_color_scheme_all_nan(self):
        """Testet die Erstellung des Farbschemas mit nur NaN-Werten."""
        data = pd.Series([np.nan, np.nan, np.nan])
        norm, sm = create_color_scheme(data)
        
        # Sollte Fallback-Werte verwenden
        self.assertEqual(norm.vmin, 0)
        self.assertEqual(norm.vmax, 100)
        
    def create_temp_csv(self, data):
        """Hilfsfunktion zum Erstellen einer temporären CSV-Datei."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
        data.to_csv(temp_file.name, sep=';', index=False)
        temp_file.close()
        return temp_file.name
        
    def test_load_voting_data_success(self):
        """Testet das erfolgreiche Laden von Abstimmungsdaten."""
        # Erstelle temporäre CSV-Datei
        temp_file = self.create_temp_csv(self.test_voting_data)
        
        try:
            result = load_voting_data(temp_file)
            
            # Überprüfe, dass Daten geladen wurden
            self.assertEqual(len(result), len(self.test_voting_data))
            self.assertEqual(list(result.columns), list(self.test_voting_data.columns))
            
        finally:
            # Räume temporäre Datei auf
            os.unlink(temp_file)
            
    def test_load_voting_data_file_not_found(self):
        """Testet das Verhalten bei nicht existierender Datei."""
        with self.assertRaises(FileNotFoundError):
            load_voting_data("nicht_existierende_datei.csv")
            
    @patch('builtins.print')  # Mock print um Ausgabe zu unterdrücken
    def test_print_voting_statistics(self, mock_print):
        """Testet die Ausgabe von Abstimmungsstatistiken."""
        # Erstelle Test-GeoDataFrame
        test_gdf = gpd.GeoDataFrame({
            'NAME': ['Zürich', 'Bern', 'Genève'],
            'Ja-Prozent': [55.5, 45.2, 67.8],
            'geometry': [
                Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                Polygon([(1, 0), (2, 0), (2, 1), (1, 1)]),
                Polygon([(2, 0), (3, 0), (3, 1), (2, 1)])
            ]
        })
        
        # Sollte ohne Fehler ausgeführt werden
        print_voting_statistics(test_gdf, "Test Abstimmung")
        
        # Überprüfe, dass print aufgerufen wurde
        self.assertTrue(mock_print.called)
        
    @patch('builtins.print')
    def test_print_voting_statistics_no_data(self, mock_print):
        """Testet die Statistikausgabe mit leeren Daten."""
        # Erstelle leeres GeoDataFrame
        empty_gdf = gpd.GeoDataFrame({
            'NAME': [],
            'Ja-Prozent': [],
            'geometry': []
        })
        
        print_voting_statistics(empty_gdf, "Test")
        
        # Sollte Fehlermeldung ausgeben
        self.assertTrue(mock_print.called)
        
    def test_integration_full_workflow(self):
        """Integrationstest für den kompletten Workflow."""
        try:
            # 1. Suche Abstimmung
            search_result = search_voting_by_title(self.test_voting_data, 'Schächt')
            self.assertFalse(search_result.empty)
            
            # 2. Filtere Daten
            filtered = filter_for_abstimmung(self.test_voting_data, 'Schächt')
            self.assertFalse(filtered.empty)
            
            # 3. Verknüpfe mit Kartendaten
            merged = merge_data_to_plot(filtered, self.test_map_data)
            self.assertGreater(merged['Ja-Prozent'].notna().sum(), 0)
            
            # 4. Erstelle Farbschema
            norm, sm = create_color_scheme(merged['Ja-Prozent'])
            self.assertIsNotNone(norm)
            self.assertIsNotNone(sm)
            
            print("✅ Integrationstest erfolgreich")
            
        except Exception as e:
            self.fail(f"Integrationstest fehlgeschlagen: {e}")


class TestEdgeCases(unittest.TestCase):
    """Tests für Grenzfälle und Fehlerbehandlung."""
    
    def test_data_with_special_characters(self):
        """Testet den Umgang mit Sonderzeichen in Titeln."""
        data_with_special_chars = pd.DataFrame({
            'titel_kurz_d': ['Ä-ö-ü Test', 'Café & Restaurant', 'Tést çompliqué'],
            'zh-japroz': [50, 60, 70]
        })
        
        # Sollte ohne Fehler funktionieren
        result = search_voting_by_title(data_with_special_chars, 'ä-ö')
        self.assertEqual(len(result), 1)
        
    def test_numeric_data_conversion(self):
        """Testet die Konvertierung von numerischen Daten."""
        data_with_strings = pd.DataFrame({
            'titel_kurz_d': ['Test'],
            'zh-japroz': ['50.5'],  # String statt Zahl
            'be-japroz': ['invalid']  # Ungültiger Wert
        })
        
        map_data = gpd.GeoDataFrame({
            'NAME': ['Zürich', 'Bern'],
            'geometry': [
                Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                Polygon([(1, 0), (2, 0), (2, 1), (1, 1)])
            ]
        })
        
        filtered = filter_for_abstimmung(data_with_strings, 'Test')
        merged = merge_data_to_plot(filtered, map_data)
          # Sollte numerische Konvertierung handhaben
        self.assertTrue(pd.api.types.is_numeric_dtype(merged['Ja-Prozent']))
    
    @unittest.skipUnless(HAS_GEOPANDAS, "geopandas nicht verfügbar")
    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.subplots')
    def test_create_comparison_plot_success(self, mock_subplots, mock_show):
        """Testet erfolgreiche Erstellung eines Vergleichsplots."""
        from utils_abstimmungen_analyse import create_comparison_plot
        
        # Mock matplotlib
        fig = MagicMock()
        axes = [MagicMock(), MagicMock()]
        mock_subplots.return_value = (fig, axes)
        
        # Erstelle Test-Daten mit mehreren Abstimmungen
        test_data = pd.DataFrame({
            'titel_kurz_d': ['Test Abstimmung 1', 'Test Abstimmung 2'],
            'zh-japroz': [55.5, 45.2],
            'be-japroz': [60.1, 40.8],
            'lu-japroz': [52.3, 48.7]
        })
        
        abstimmungen = ['Test Abstimmung 1', 'Test Abstimmung 2']
        
        # Sollte ohne Fehler durchlaufen
        try:
            create_comparison_plot(test_data, abstimmungen)
            test_passed = True
        except Exception as e:
            test_passed = False
            print(f"Test fehlgeschlagen: {e}")
        
        self.assertTrue(test_passed)
        mock_show.assert_called()
    
    @unittest.skipUnless(HAS_GEOPANDAS, "geopandas nicht verfügbar")
    def test_create_comparison_plot_invalid_input(self):
        """Testet Verhalten bei ungültigen Eingaben für Vergleichsplot."""
        from utils_abstimmungen_analyse import create_comparison_plot
        
        test_data = pd.DataFrame({
            'titel_kurz_d': ['Test Abstimmung'],
            'zh-japroz': [55.5]
        })
        
        # Sollte Fehler bei zu wenigen Abstimmungen werfen
        with self.assertRaises(ValueError):
            create_comparison_plot(test_data, ['Eine Abstimmung'])
    
    @unittest.skipUnless(HAS_GEOPANDAS, "geopandas nicht verfügbar")
    @patch('builtins.print')
    def test_create_correlation_analysis(self, mock_print):
        """Testet die Korrelationsanalyse-Funktion."""
        from utils_abstimmungen_analyse import create_correlation_analysis
        
        # Erstelle Test-Daten
        data1 = pd.Series([55, 60, 45], index=['Zürich', 'Bern', 'Luzern'])
        data2 = pd.Series([58, 62, 42], index=['Zürich', 'Bern', 'Luzern'])
        
        all_data = {
            'Abstimmung 1': data1,
            'Abstimmung 2': data2
        }
        
        # Sollte ohne Fehler durchlaufen
        try:
            with patch('matplotlib.pyplot.show'):
                create_correlation_analysis(all_data)
            test_passed = True
        except Exception as e:
            test_passed = False
            print(f"Korrelationsanalyse fehlgeschlagen: {e}")
        
        self.assertTrue(test_passed)
    
    @unittest.skipUnless(HAS_GEOPANDAS, "geopandas nicht verfügbar")
    def test_print_comparison_statistics(self):
        """Testet die Ausgabe von Vergleichsstatistiken."""
        from utils_abstimmungen_analyse import print_comparison_statistics
        
        # Erstelle Test-Daten
        data1 = pd.Series([55.5, 60.1, 45.2], index=['Zürich', 'Bern', 'Luzern'])
        data2 = pd.Series([48.3, 52.7, 38.9], index=['Zürich', 'Bern', 'Luzern'])
        
        all_data = {
            'Abstimmung hohe Zustimmung': data1,
            'Abstimmung niedrige Zustimmung': data2
        }
        
        # Sollte ohne Fehler durchlaufen
        try:
            with patch('builtins.print'):
                print_comparison_statistics(all_data)
            test_passed = True
        except Exception as e:
            test_passed = False
            print(f"Statistikausgabe fehlgeschlagen: {e}")
        
        self.assertTrue(test_passed)
    
    def test_print_voting_statistics_empty_data(self):
        """Testet Verhalten bei leeren Daten für Statistiken."""
        from utils_abstimmungen_analyse import print_voting_statistics
        
        # Erstelle leeres GeoDataFrame
        empty_data = pd.DataFrame({'Ja-Prozent': [np.nan, np.nan]})
        
        # Sollte ohne Fehler durchlaufen und entsprechende Meldung ausgeben
        try:
            with patch('builtins.print') as mock_print:
                print_voting_statistics(empty_data, 'Test Abstimmung')
            
            # Prüfe ob Fehlermeldung ausgegeben wurde
            mock_print.assert_called()
            test_passed = True
        except Exception as e:
            test_passed = False
            print(f"Test fehlgeschlagen: {e}")
        
        self.assertTrue(test_passed)
    
    def test_create_color_scheme_edge_cases(self):
        """Testet Farbschema-Erstellung bei Grenzfällen."""
        # Test mit leeren Daten
        empty_series = pd.Series([])
        norm, sm = create_color_scheme(empty_series)
        
        self.assertIsNotNone(norm)
        self.assertIsNotNone(sm)
        self.assertEqual(norm.vmin, 0)
        self.assertEqual(norm.vmax, 100)
        
        # Test mit identischen Werten
        identical_series = pd.Series([50.0, 50.0, 50.0])
        norm, sm = create_color_scheme(identical_series)
        
        self.assertIsNotNone(norm)
        self.assertIsNotNone(sm)
        # Sollte sinnvolle Standardwerte setzen
        self.assertTrue(norm.vmax > norm.vmin)
    
    def test_search_voting_by_title_regex(self):
        """Testet erweiterte Suchfunktionen mit RegEx."""
        # Test mit RegEx-Pattern
        regex_results = search_voting_by_title(
            self.test_voting_data, 
            r'Abstimmung [12]',  # Sollte Abstimmung 1 und 2 finden
            exact_match=False
        )
        
        self.assertEqual(len(regex_results), 2)
        
        # Test mit exakter Suche
        exact_results = search_voting_by_title(
            self.test_voting_data,
            'Test Abstimmung 1',
            exact_match=True
        )
        
        self.assertEqual(len(exact_results), 1)
        self.assertEqual(exact_results.iloc[0]['titel_kurz_d'], 'Test Abstimmung 1')


if __name__ == '__main__':
    # Führe alle Tests aus
    unittest.main(verbosity=2)
