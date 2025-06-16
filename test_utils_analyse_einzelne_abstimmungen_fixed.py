"""
Unit Tests für die Utilities der Abstimmungsanalyse.

Diese Datei enthält Unit Tests für alle Funktionen in utils_analyse_einzelne-abstimmungen.py.
"""

import unittest
import pandas as pd
import numpy as np
import sys
import importlib.util
from unittest.mock import patch, MagicMock

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
    # Lade das Modul mit Bindestrichen im Namen
    spec = importlib.util.spec_from_file_location(
        "utils_analyse_einzelne_abstimmungen", 
        "utils_analyse_einzelne-abstimmungen.py"
    )
    utils_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(utils_module)
    
    # Importiere die Funktionen
    create_canton_mapping = utils_module.create_canton_mapping
    search_voting_by_title = utils_module.search_voting_by_title
    create_color_scheme = utils_module.create_color_scheme
    
    # Importiere nur bei verfügbarem geopandas
    if HAS_GEOPANDAS:
        load_voting_data = utils_module.load_voting_data
        filter_for_abstimmung = utils_module.filter_for_abstimmung
        merge_data_to_plot = utils_module.merge_data_to_plot
        print_voting_statistics = utils_module.print_voting_statistics
        plot_abstimmungen_schweiz = utils_module.plot_abstimmungen_schweiz
except ImportError as e:
    print(f"⚠️ Import-Fehler: {e}")
    HAS_GEOPANDAS = False


class TestUtilsAbstimmungenAnalyse(unittest.TestCase):
    """Test-Klasse für die Utilities der Abstimmungsanalyse."""
    
    def setUp(self):
        """Initialisiert Test-Daten für jeden Test."""
        self.test_data = pd.DataFrame({
            'titel_kurz_d': ['Test Abstimmung 1', 'Test Abstimmung 2'],
            'annahme': [True, False],
            'zh-japroz': [55.5, 45.2],
            'be-japroz': [60.1, 40.8],
            'lu-japroz': [52.3, 48.7]
        })
        
        if HAS_GEOPANDAS:
            # Erstelle eine einfache Test-Geodatenstruktur
            self.test_geodata = gpd.GeoDataFrame({
                'NAME': ['Zürich', 'Bern', 'Luzern'],
                'geometry': [
                    Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                    Polygon([(1, 0), (2, 0), (2, 1), (1, 1)]),
                    Polygon([(2, 0), (3, 0), (3, 1), (2, 1)])
                ]
            })
    
    def test_create_canton_mapping(self):
        """Testet die Erstellung der Kantonsabbildung."""
        mapping = create_canton_mapping()
        
        # Prüfe, ob es ein Dictionary ist
        self.assertIsInstance(mapping, dict)
        
        # Prüfe, ob bekannte Kantone enthalten sind (korrekte Schlüssel ohne -japroz)
        self.assertIn('zh', mapping)
        self.assertIn('be', mapping)
        self.assertEqual(mapping['zh'], 'Zürich')
        self.assertEqual(mapping['be'], 'Bern')
    
    def test_search_voting_by_title(self):
        """Testet die Suchfunktion für Abstimmungen."""
        result = search_voting_by_title(self.test_data, 'Test Abstimmung 1')
        
        # Sollte eine Zeile zurückgeben
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['titel_kurz_d'], 'Test Abstimmung 1')
        
        # Test mit nicht existierendem Titel
        result_empty = search_voting_by_title(self.test_data, 'Nicht existierend')
        self.assertEqual(len(result_empty), 0)
    
    def test_create_color_scheme(self):
        """Testet die Erstellung des Farbschemas."""
        # Test mit echten Datenwerten (pandas Series)
        test_values = pd.Series([30.0, 50.0, 70.0])
        normalizer, scalar_mappable = create_color_scheme(test_values)
        
        self.assertIsNotNone(normalizer)
        self.assertIsNotNone(scalar_mappable)
        
        # Test mit leeren Werten
        empty_values = pd.Series([])
        normalizer_empty, scalar_mappable_empty = create_color_scheme(empty_values)
        self.assertIsNotNone(normalizer_empty)
        self.assertIsNotNone(scalar_mappable_empty)
    
    @unittest.skipUnless(HAS_GEOPANDAS, "geopandas nicht verfügbar")
    def test_load_voting_data(self):
        """Testet das Laden der Abstimmungsdaten."""
        # Mock für das Laden der CSV-Datei
        with patch('pandas.read_csv', return_value=self.test_data):
            data = load_voting_data('dummy_path.csv')
            self.assertIsInstance(data, pd.DataFrame)
            self.assertEqual(len(data), 2)
    
    @unittest.skipUnless(HAS_GEOPANDAS, "geopandas nicht verfügbar")
    def test_filter_for_abstimmung(self):
        """Testet die Filterung nach einer spezifischen Abstimmung."""
        with patch('builtins.print'):  # Unterdrückt Print-Ausgaben während Tests
            filtered_data = filter_for_abstimmung(self.test_data, 'Test Abstimmung 1')
            
            # filter_for_abstimmung gibt nur Kantonsspalten zurück
            self.assertEqual(len(filtered_data), 1)
            # Prüfe, dass es Kantonsspalten enthält
            self.assertIn('zh-japroz', filtered_data.columns)
            self.assertIn('be-japroz', filtered_data.columns)
    
    @unittest.skipUnless(HAS_GEOPANDAS, "geopandas nicht verfügbar")
    def test_merge_data_to_plot(self):
        """Testet das Mergen der Daten für Plots."""
        # Erstelle Test-Geodaten mit passenden Namen
        geo_data = gpd.GeoDataFrame({
            'NAME': ['Zürich', 'Bern', 'Luzern'],
            'geometry': [
                Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                Polygon([(1, 0), (2, 0), (2, 1), (1, 1)]),
                Polygon([(2, 0), (3, 0), (3, 1), (2, 1)])
            ]
        })
        
        # Erstelle bereits gefilterte Kantonsdaten (wie von filter_for_abstimmung zurückgegeben)
        voting_data = pd.DataFrame({
            'zh-japroz': [55.5],
            'be-japroz': [60.1],
            'lu-japroz': [52.3]
        })
        
        merged_data = merge_data_to_plot(geo_data, voting_data)
        
        # Prüfe, ob das Merging funktioniert hat
        self.assertIsInstance(merged_data, gpd.GeoDataFrame)
        self.assertIn('ja_prozent', merged_data.columns)
        self.assertEqual(len(merged_data), 3)
    
    @unittest.skipUnless(HAS_GEOPANDAS, "geopandas nicht verfügbar")
    def test_print_voting_statistics(self):
        """Testet die Ausgabe der Abstimmungsstatistiken."""
        with patch('builtins.print') as mock_print:
            # print_voting_statistics erwartet 2 Parameter: data und abstimmung
            print_voting_statistics(self.test_data, 'Test Abstimmung 1')
            
            # Prüfe, ob Print-Statements aufgerufen wurden
            self.assertTrue(mock_print.called)
    
    @unittest.skipUnless(HAS_GEOPANDAS, "geopandas nicht verfügbar")
    def test_plot_abstimmungen_schweiz(self):
        """Testet die Hauptplot-Funktion."""
        test_passed = True
        try:
            with patch('matplotlib.pyplot.show'), \
                 patch('geopandas.read_file', return_value=self.test_geodata), \
                 patch('builtins.print'):
                
                # plot_abstimmungen_schweiz erwartet: data, search_term, map_path
                plot_abstimmungen_schweiz(
                    self.test_data,
                    'Test Abstimmung 1',  # Suchbegriff, nicht Map-Pfad
                    'data/maps/swissboundaries.shp/swissBOUNDARIES3D_1_5_TLM_HOHEITSGEBIET.shp'
                )
        except Exception as e:
            test_passed = False
            print(f"Test fehlgeschlagen: {e}")
        
        self.assertTrue(test_passed)


if __name__ == '__main__':
    # Führe Tests aus
    unittest.main(verbosity=2)
