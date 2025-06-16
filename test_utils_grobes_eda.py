"""
Unit Tests für die Utilities des groben EDA.

Diese Datei enthält Unit Tests für alle Funktionen in utils_grobes_eda.py.
"""

import unittest
import pandas as pd
import numpy as np
import tempfile
import os
from unittest.mock import patch, MagicMock
import sys

# Importiere die zu testenden Funktionen
sys.path.append('.')
from utils_grobes_eda import (
    load_and_prepare_data,
    assign_period,
    identify_society_oriented_votes,
    calculate_period_statistics,
    calculate_correlation_time_acceptance
)


class TestUtilsGrobesEDA(unittest.TestCase):
    """Test-Klasse für die Utilities des groben EDA."""
    
    def setUp(self):
        """Erstellt Test-Daten für die Tests."""
        # Erstelle einen temporären Test-Datensatz
        self.test_data = pd.DataFrame({
            'anr': [1, 2, 3, 4, 5],
            'datum': ['01.01.1900', '15.06.1950', '20.12.1980', '05.03.2000', '10.11.2020'],
            'titel_kurz_d': [
                'Gesellschaftliche Reform',
                'Wirtschaftsgesetz',
                'Bildungsreform',
                'Steuergesetz',
                'Gleichstellungsinitiative'
            ],
            'titel_off_d': [
                'Gesetz über gesellschaftliche Reformen',
                'Bundesgesetz über Wirtschaft',
                'Reform des Bildungswesens',
                'Revision der Steuergesetze',
                'Initiative für Gleichstellung'
            ],
            'volkja-proz': [45.5, 62.3, 38.9, 55.1, 67.8],
            'annahme': [0, 1, 0, 1, 1]
        })
        
    def test_assign_period(self):
        """Testet die Zuordnung von Jahren zu Zeiträumen."""
        # Test für verschiedene Jahre
        self.assertEqual(assign_period(1900), "1893-1919")
        self.assertEqual(assign_period(1930), "1920-1949")
        self.assertEqual(assign_period(1965), "1950-1979")
        self.assertEqual(assign_period(1995), "1980-2009")
        self.assertEqual(assign_period(2015), "2010-2025")
        self.assertEqual(assign_period(np.nan), "Unbekannt")
        
    def test_identify_society_oriented_votes(self):
        """Testet die Identifikation gesellschaftsorientierter Abstimmungen."""
        result = identify_society_oriented_votes(self.test_data)
        
        # Überprüfe, ob die Spalte hinzugefügt wurde
        self.assertIn('society_oriented', result.columns)
        
        # Überprüfe spezifische Klassifikationen
        self.assertTrue(result.loc[0, 'society_oriented'])  # 'gesellschaftliche Reform'
        self.assertFalse(result.loc[1, 'society_oriented'])  # 'Wirtschaftsgesetz'
        self.assertTrue(result.loc[2, 'society_oriented'])  # 'Bildungsreform'
        self.assertTrue(result.loc[4, 'society_oriented'])  # 'Gleichstellungsinitiative'
        
    def test_identify_society_oriented_votes_custom_keywords(self):
        """Testet die Identifikation mit benutzerdefinierten Schlüsselwörtern."""
        custom_keywords = ['steuer', 'wirtschaft']
        result = identify_society_oriented_votes(self.test_data, custom_keywords)
        
        # Mit diesen Keywords sollten andere Abstimmungen identifiziert werden
        self.assertTrue(result.loc[1, 'society_oriented'])  # 'Wirtschaftsgesetz'
        self.assertTrue(result.loc[3, 'society_oriented'])  # 'Steuergesetz'
        
    def test_calculate_period_statistics(self):
        """Testet die Berechnung von Zeitraum-Statistiken."""
        # Füge period-Spalte hinzu
        df_with_period = self.test_data.copy()
        df_with_period['period'] = df_with_period['datum'].apply(
            lambda x: assign_period(pd.to_datetime(x, format='%d.%m.%Y').year)
        )
        
        result = calculate_period_statistics(df_with_period)
        
        # Überprüfe Struktur des Ergebnisses
        expected_columns = ['Zeitraum', 'Durchschnitt', 'Median', 'Anzahl']
        self.assertListEqual(list(result.columns), expected_columns)
        
        # Überprüfe, dass alle Zeiträume vorhanden sind
        self.assertGreater(len(result), 0)
        
    def test_calculate_correlation_time_acceptance(self):
        """Testet die Korrelationsberechnung zwischen Zeit und Annahmequote."""
        # Bereite Test-Daten vor
        df_with_analysis = identify_society_oriented_votes(self.test_data)
        df_with_analysis['datum'] = pd.to_datetime(df_with_analysis['datum'], format='%d.%m.%Y')
        df_with_analysis['year'] = df_with_analysis['datum'].dt.year
        
        correlation, p_value, interpretation = calculate_correlation_time_acceptance(df_with_analysis)
        
        # Überprüfe Rückgabetypen
        self.assertIsInstance(correlation, float)
        self.assertIsInstance(p_value, float)
        self.assertIsInstance(interpretation, str)
        
        # Überprüfe Wertebereiche
        self.assertTrue(-1 <= correlation <= 1)
        self.assertTrue(0 <= p_value <= 1)
        self.assertGreater(len(interpretation), 0)
        
    def test_calculate_correlation_insufficient_data(self):
        """Testet die Korrelationsberechnung mit ungenügenden Daten."""
        # Erstelle DataFrame ohne gesellschaftsorientierte Abstimmungen
        empty_df = pd.DataFrame({
            'society_oriented': [False, False],
            'year': [2000, 2001],
            'volkja-proz': [50, 60]
        })
        
        correlation, p_value, interpretation = calculate_correlation_time_acceptance(empty_df)
        
        self.assertEqual(correlation, 0.0)
        self.assertEqual(p_value, 1.0)
        self.assertIn("Nicht genügend Daten", interpretation)
        
    def test_load_and_prepare_data_file_not_found(self):
        """Testet das Verhalten bei nicht existierender Datei."""
        with self.assertRaises(FileNotFoundError):
            load_and_prepare_data("nicht_existierende_datei.csv")
            
    def create_temp_csv(self, data):
        """Hilfsfunktion zum Erstellen einer temporären CSV-Datei."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
        data.to_csv(temp_file.name, sep=';', index=False)
        temp_file.close()
        return temp_file.name
        
    def test_load_and_prepare_data_success(self):
        """Testet das erfolgreiche Laden und Vorbereiten von Daten."""
        # Erstelle temporäre CSV-Datei
        temp_file = self.create_temp_csv(self.test_data)
        
        try:
            result = load_and_prepare_data(temp_file)
            
            # Überprüfe, ob neue Spalten hinzugefügt wurden
            self.assertIn('year', result.columns)
            self.assertIn('period', result.columns)
            
            # Überprüfe Datentypen
            self.assertTrue(pd.api.types.is_datetime64_any_dtype(result['datum']))
            self.assertTrue(pd.api.types.is_integer_dtype(result['year']))
            
        finally:
            # Räume temporäre Datei auf
            os.unlink(temp_file)
            
    def tearDown(self):
        """Räumt nach den Tests auf."""
        pass


class TestDataValidation(unittest.TestCase):
    """Zusätzliche Tests für Datenvalidierung."""
    
    def test_data_integrity_checks(self):
        """Testet grundlegende Datenintegritätsprüfungen."""
        # Test mit ungültigen Daten
        invalid_data = pd.DataFrame({
            'datum': ['invalid_date', '01.01.2000'],
            'titel_kurz_d': ['Test 1', None],
            'titel_off_d': [None, 'Test 2'],
            'volkja-proz': [-5, 105]  # Ungültige Prozentangaben
        })
        
        # Die Funktion sollte auch mit ungültigen Daten umgehen können
        result = identify_society_oriented_votes(invalid_data)
        self.assertIn('society_oriented', result.columns)
        
    def test_edge_cases(self):
        """Testet Grenzfälle."""
        # Leerer DataFrame
        empty_df = pd.DataFrame()
        result = identify_society_oriented_votes(empty_df)
        self.assertTrue(result.empty)
        
        # DataFrame mit nur einer Zeile
        single_row_df = pd.DataFrame({
            'titel_kurz_d': ['Gesellschaftsreform'],
            'titel_off_d': ['Reform der Gesellschaft'],
            'volkja-proz': [50.0]
        })
        result = identify_society_oriented_votes(single_row_df)
        self.assertEqual(len(result), 1)
        self.assertTrue(result.loc[0, 'society_oriented'])


if __name__ == '__main__':
    # Führe alle Tests aus
    unittest.main(verbosity=2)
