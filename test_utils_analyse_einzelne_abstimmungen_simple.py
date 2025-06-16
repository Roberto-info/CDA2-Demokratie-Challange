"""
Vereinfachte Unit Tests für utils_analyse_einzelne-abstimmungen.py

Diese Tests konzentrieren sich auf die wichtigsten Funktionen und vermeiden
komplexe Mock-Strukturen, die zu Fehlern führen können.
"""

import unittest
import pandas as pd
import numpy as np
import sys
import importlib.util

# Prüfe ob geopandas verfügbar ist
try:
    import geopandas as gpd
    from shapely.geometry import Polygon
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False

# Importiere die zu testenden Funktionen
try:
    spec = importlib.util.spec_from_file_location(
        "utils_module", 
        "utils_analyse_einzelne-abstimmungen.py"
    )
    utils = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(utils)
    print("✅ Modul erfolgreich geladen")
except Exception as e:
    print(f"❌ Modul-Import fehlgeschlagen: {e}")
    sys.exit(1)


class TestBasicUtilityFunctions(unittest.TestCase):
    """Einfache Tests für die grundlegenden Utility-Funktionen."""
    
    def setUp(self):
        """Initialisiert Test-Daten."""
        self.test_data = pd.DataFrame({
            'titel_kurz_d': ['Test Abstimmung 1', 'Test Abstimmung 2'],
            'annahme': [True, False],
            'zh-japroz': [55.5, 45.2],
            'be-japroz': [60.1, 40.8],
            'lu-japroz': [52.3, 48.7]
        })
    
    def test_create_canton_mapping(self):
        """Testet die Kantonsabbildung."""
        mapping = utils.create_canton_mapping()
        
        self.assertIsInstance(mapping, dict)
        self.assertIn('zh', mapping)
        self.assertEqual(mapping['zh'], 'Zürich')
        print("✅ create_canton_mapping funktioniert")
    
    def test_search_voting_by_title(self):
        """Testet die Suchfunktion."""
        result = utils.search_voting_by_title(self.test_data, 'Test Abstimmung 1')
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['titel_kurz_d'], 'Test Abstimmung 1')
        
        # Test mit nicht existierendem Titel
        result_empty = utils.search_voting_by_title(self.test_data, 'Nicht existierend')
        self.assertEqual(len(result_empty), 0)
        print("✅ search_voting_by_title funktioniert")
    
    def test_create_color_scheme(self):
        """Testet das Farbschema."""
        test_values = pd.Series([30.0, 50.0, 70.0])
        
        normalizer, scalar_mappable = utils.create_color_scheme(test_values)
        self.assertIsNotNone(normalizer)
        self.assertIsNotNone(scalar_mappable)
        print("✅ create_color_scheme funktioniert")
    
    @unittest.skipUnless(HAS_GEOPANDAS, "geopandas nicht verfügbar")
    def test_filter_for_abstimmung(self):
        """Testet die Filterung."""
        # Unterdrücke Print-Ausgaben
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            filtered_data = utils.filter_for_abstimmung(self.test_data, 'Test Abstimmung 1')
        
        # filter_for_abstimmung gibt nur Kantonsspalten zurück
        self.assertEqual(len(filtered_data), 1)
        self.assertIn('zh-japroz', filtered_data.columns)
        print("✅ filter_for_abstimmung funktioniert")


class TestIntegrationWithRealData(unittest.TestCase):
    """Tests mit echten Daten aus der CSV."""
    
    @unittest.skipUnless(HAS_GEOPANDAS, "geopandas nicht verfügbar")
    def test_real_data_workflow(self):
        """Testet einen kompletten Workflow mit echten Daten."""
        try:
            # Lade echte Daten
            data = utils.load_voting_data('data/dataset.csv')
            self.assertIsInstance(data, pd.DataFrame)
            self.assertGreater(len(data), 100)  # Sollte viele Abstimmungen haben
            
            # Teste Suche nach bekannter Abstimmung
            search_result = utils.search_voting_by_title(data, 'Frauenstimmrecht')
            self.assertGreater(len(search_result), 0)
            
            print("✅ Workflow mit echten Daten funktioniert")
            
        except FileNotFoundError:
            self.skipTest("CSV-Datei nicht gefunden")
        except Exception as e:
            self.fail(f"Workflow mit echten Daten fehlgeschlagen: {e}")


if __name__ == '__main__':
    print("🔍 Starte vereinfachte Unit Tests für utils_analyse_einzelne-abstimmungen...")
    
    # Führe Tests aus
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBasicUtilityFunctions)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIntegrationWithRealData))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n🎉 Alle Tests erfolgreich!")
    else:
        print(f"\n❌ {len(result.failures)} Fehler, {len(result.errors)} Exceptions")
        sys.exit(1)
