"""
Unit Tests für die Utilities des detaillierten EDA.

Diese Datei enthält Unit Tests für alle Funktionen in utils_detailliertes_eda.py.
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
from utils_analyse_detailliert import (
    load_society_data,
    define_social_keywords,
    classify_society_votes,
    extract_canton_columns,
    calculate_canton_liberality_ranking,
    analyze_temporal_patterns,
    validate_classification_sample,
    generate_summary_statistics
)


class TestUtilsDetailliertesEDA(unittest.TestCase):
    """Test-Klasse für die Utilities des detaillierten EDA."""
    
    def setUp(self):
        """Erstellt Test-Daten für die Tests."""
        self.test_data = pd.DataFrame({
            'anr': [1, 2, 3, 4, 5, 6],
            'datum': ['2000-01-01', '2005-06-15', '2010-12-20', '2015-03-05', '2020-11-10', '2022-05-30'],
            'titel_kurz_d': [
                'Gleichstellung der Geschlechter',
                'Steuerreform',
                'Krankenversicherungsreform',
                'Wirtschaftsförderung',
                'Bildungsgesetz',
                'Nationalstrassenbau'
            ],
            'titel_off_d': [
                'Bundesgesetz über Gleichstellung',
                'Revision der Steuergesetze',
                'Reform der Krankenversicherung',
                'Gesetz zur Wirtschaftsförderung',
                'Neues Bildungsgesetz',
                'Bundesgesetz über Nationalstrassen'
            ],
            'text_d': [
                'Förderung der Gleichstellung von Frauen',
                'Senkung der Unternehmenssteuern',
                'Verbesserung des Gesundheitswesens',
                'Unterstützung der Wirtschaft',
                'Reform des Bildungssystems',
                'Ausbau der Verkehrsinfrastruktur'
            ],
            'volkja-proz': [55.2, 42.8, 63.1, 48.9, 59.4, 36.7],
            'zh-japroz': [62.1, 38.5, 68.9, 52.3, 64.2, 41.2],
            'be-japroz': [58.7, 41.2, 61.4, 47.8, 57.9, 35.1],
            'ge-japroz': [69.3, 35.9, 72.1, 49.5, 66.8, 28.4]
        })
        
    def test_define_social_keywords(self):
        """Testet die Definition der Schlüsselwörter."""
        social_keywords, non_social_keywords = define_social_keywords()
        
        # Überprüfe, dass Listen nicht leer sind
        self.assertGreater(len(social_keywords), 0)
        self.assertGreater(len(non_social_keywords), 0)
        
        # Überprüfe, dass erwartete Keywords enthalten sind
        self.assertIn('gleichstellung', social_keywords)
        self.assertIn('bildung', social_keywords)
        self.assertIn('krankenversicherung', social_keywords)
        
        self.assertIn('steuerharmonisierung', non_social_keywords)
        self.assertIn('nationalstrassen', non_social_keywords)
        self.assertIn('wirtschaftspolitik', non_social_keywords)
        
        # Überprüfe, dass keine Überschneidungen bestehen
        overlap = set(social_keywords) & set(non_social_keywords)
        self.assertEqual(len(overlap), 0, f"Überschneidende Keywords gefunden: {overlap}")
        
    def test_classify_society_votes(self):
        """Testet die Klassifikation gesellschaftsorientierter Abstimmungen."""
        result = classify_society_votes(self.test_data)
        
        # Überprüfe, dass die Spalte hinzugefügt wurde
        self.assertIn('society_oriented', result.columns)
        
        # Überprüfe spezifische Klassifikationen
        classifications = result['society_oriented'].tolist()
        
        # Erwartete Klassifikationen basierend auf den Testdaten
        expected = [
            True,   # Gleichstellung
            False,  # Steuerreform (ausgeschlossen)
            True,   # Krankenversicherung
            False,  # Wirtschaftsförderung (ausgeschlossen)
            True,   # Bildungsgesetz
            False   # Nationalstrassenbau (ausgeschlossen)
        ]
        
        self.assertEqual(classifications, expected)
        
    def test_classify_society_votes_custom_keywords(self):
        """Testet die Klassifikation mit benutzerdefinierten Keywords."""
        custom_social = ['steuer', 'wirtschaft']
        custom_non_social = ['bildung']
        
        result = classify_society_votes(self.test_data, custom_social, custom_non_social)
        
        # Mit diesen Keywords sollten Steuer- und Wirtschaftsthemen als gesellschaftsorientiert gelten
        # aber Bildung ausgeschlossen werden
        self.assertTrue(result.loc[1, 'society_oriented'])  # Steuerreform
        self.assertTrue(result.loc[3, 'society_oriented'])  # Wirtschaftsförderung
        self.assertFalse(result.loc[4, 'society_oriented'])  # Bildungsgesetz (ausgeschlossen)
        
    def test_extract_canton_columns(self):
        """Testet die Extraktion der Kantonsspalten."""
        canton_cols = extract_canton_columns(self.test_data)
        
        expected_cols = ['zh-japroz', 'be-japroz', 'ge-japroz']
        self.assertEqual(sorted(canton_cols), sorted(expected_cols))
        
    def test_calculate_canton_liberality_ranking(self):
        """Testet die Berechnung des Kantons-Rankings."""
        # Füge Klassifikation hinzu
        classified_data = classify_society_votes(self.test_data)
        
        ranking = calculate_canton_liberality_ranking(classified_data)
        
        # Überprüfe Struktur
        expected_columns = ['Kanton', 'Durchschnittliche_Ja_Prozente', 'Rang']
        self.assertEqual(list(ranking.columns), expected_columns)
        
        # Überprüfe, dass Rang korrekt zugewiesen ist
        self.assertEqual(ranking.iloc[0]['Rang'], 1)  # Höchster Rang
        self.assertEqual(ranking.iloc[-1]['Rang'], len(ranking))  # Niedrigster Rang
        
        # Überprüfe, dass Sortierung korrekt ist (höchste Ja-Prozente zuerst)
        ja_prozente = ranking['Durchschnittliche_Ja_Prozente'].tolist()
        self.assertEqual(ja_prozente, sorted(ja_prozente, reverse=True))
        
    def test_analyze_temporal_patterns(self):
        """Testet die zeitliche Musteranalyse."""
        # Füge Klassifikation und Jahr hinzu
        classified_data = classify_society_votes(self.test_data)
        classified_data['datum'] = pd.to_datetime(classified_data['datum'])
        classified_data['year'] = classified_data['datum'].dt.year
        
        results = analyze_temporal_patterns(classified_data)
        
        # Überprüfe, dass keine Fehler aufgetreten sind
        self.assertNotIn('error', results)
        
        # Überprüfe erwartete Keys
        expected_keys = ['total_votes', 'time_span', 'mean_acceptance', 'median_acceptance']
        for key in expected_keys:
            self.assertIn(key, results)
            
        # Überprüfe Wertebereiche
        self.assertGreater(results['total_votes'], 0)
        self.assertGreaterEqual(results['time_span'], 0)
        self.assertTrue(0 <= results['mean_acceptance'] <= 100)
        self.assertTrue(0 <= results['median_acceptance'] <= 100)
        
    def test_analyze_temporal_patterns_insufficient_data(self):
        """Testet die zeitliche Analyse mit ungenügenden Daten."""
        # Erstelle DataFrame mit nur einer gesellschaftsorientierten Abstimmung
        small_data = self.test_data.iloc[:1].copy()
        small_data = classify_society_votes(small_data)
        small_data.loc[0, 'society_oriented'] = True
        small_data['year'] = 2000
        
        results = analyze_temporal_patterns(small_data)
        
        # Sollte Fehler zurückgeben
        self.assertIn('error', results)
        
    def test_validate_classification_sample(self):
        """Testet die Validierungsstichprobe."""
        classified_data = classify_society_votes(self.test_data)
        
        sample = validate_classification_sample(classified_data, sample_size=4)
        
        # Überprüfe, dass Stichprobe nicht leer ist
        self.assertGreater(len(sample), 0)
        
        # Überprüfe, dass sowohl True als auch False Klassifikationen enthalten sind
        # (falls beide Typen in den Originaldaten vorhanden sind)
        society_count = classified_data['society_oriented'].sum()
        non_society_count = len(classified_data) - society_count
        
        if society_count > 0 and non_society_count > 0:
            sample_society = sample['society_oriented'].sum()
            sample_non_society = len(sample) - sample_society
            self.assertGreater(sample_society, 0)
            self.assertGreater(sample_non_society, 0)
            
    def test_generate_summary_statistics(self):
        """Testet die Generierung von Zusammenfassungsstatistiken."""
        classified_data = classify_society_votes(self.test_data)
        classified_data['datum'] = pd.to_datetime(classified_data['datum'])
        classified_data['year'] = classified_data['datum'].dt.year
        
        stats = generate_summary_statistics(classified_data)
        
        # Überprüfe erwartete Keys
        expected_keys = [
            'total_votes', 'society_votes', 'society_percentage',
            'society_mean_acceptance', 'other_mean_acceptance',
            'time_span_start', 'time_span_end', 'time_span_years'
        ]
        
        for key in expected_keys:
            self.assertIn(key, stats)
            
        # Überprüfe Wertebereiche
        self.assertEqual(stats['total_votes'], len(classified_data))
        self.assertTrue(0 <= stats['society_percentage'] <= 100)
        self.assertTrue(0 <= stats['society_mean_acceptance'] <= 100)
        self.assertTrue(0 <= stats['other_mean_acceptance'] <= 100)
        
    def create_temp_csv(self, data):
        """Hilfsfunktion zum Erstellen einer temporären CSV-Datei."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
        data.to_csv(temp_file.name, sep=';', index=False)
        temp_file.close()
        return temp_file.name
        
    def test_load_society_data_success(self):
        """Testet das erfolgreiche Laden von Gesellschaftsdaten."""
        # Erstelle temporäre CSV-Datei
        temp_file = self.create_temp_csv(self.test_data)
        
        try:
            result = load_society_data(temp_file)
            
            # Überprüfe, dass Daten geladen wurden
            self.assertEqual(len(result), len(self.test_data))
            
            # Überprüfe, dass Datum und Jahr hinzugefügt wurden
            self.assertIn('year', result.columns)
            self.assertTrue(pd.api.types.is_datetime64_any_dtype(result['datum']))
            
        finally:
            # Räume temporäre Datei auf
            os.unlink(temp_file)
            
    def test_load_society_data_file_not_found(self):
        """Testet das Verhalten bei nicht existierender Datei."""
        with self.assertRaises(FileNotFoundError):
            load_society_data("nicht_existierende_datei.csv")


class TestDataValidationDetailed(unittest.TestCase):
    """Zusätzliche Tests für Datenvalidierung im detaillierten EDA."""
    
    def test_edge_cases_classification(self):
        """Testet Grenzfälle bei der Klassifikation."""
        # Leerer DataFrame
        empty_df = pd.DataFrame()
        result = classify_society_votes(empty_df)
        self.assertTrue(result.empty)
        
        # DataFrame ohne relevante Spalten
        minimal_df = pd.DataFrame({'id': [1, 2], 'value': [10, 20]})
        result = classify_society_votes(minimal_df)
        self.assertIn('society_oriented', result.columns)
        self.assertFalse(result['society_oriented'].any())  # Sollte alle False sein
        
    def test_missing_data_handling(self):
        """Testet den Umgang mit fehlenden Daten."""
        # DataFrame mit NaN-Werten
        data_with_nan = pd.DataFrame({
            'titel_kurz_d': ['Gleichstellung', np.nan, 'Bildung'],
            'titel_off_d': [np.nan, 'Steuergesetz', 'Bildungsreform'],
            'volkja-proz': [50.0, np.nan, 60.0]
        })
        
        result = classify_society_votes(data_with_nan)
        
        # Sollte ohne Fehler funktionieren
        self.assertEqual(len(result), 3)
        self.assertIn('society_oriented', result.columns)
        
    def test_ranking_edge_cases(self):
        """Testet Grenzfälle beim Ranking."""
        # Keine gesellschaftsorientierten Abstimmungen
        no_society_data = pd.DataFrame({
            'society_oriented': [False, False],
            'zh-japroz': [50, 60],
            'volkja-proz': [45, 55]
        })
        
        ranking = calculate_canton_liberality_ranking(no_society_data)
        self.assertTrue(ranking.empty)
        
        # Nur eine Kantonsspalte
        single_canton = pd.DataFrame({
            'society_oriented': [True, True],
            'zh-japroz': [50, 60],
            'volkja-proz': [45, 55]
        })
        
        ranking = calculate_canton_liberality_ranking(single_canton)
        self.assertEqual(len(ranking), 1)
        self.assertEqual(ranking.iloc[0]['Kanton'], 'zh')


if __name__ == '__main__':
    # Führe alle Tests aus
    unittest.main(verbosity=2)
