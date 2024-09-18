###
# Restaurant-App
# Autor: Daniel Bahr

# Beschreibung:
# Diese Restaurant-App bietet zahlreiche Funktionen zur Verwaltung von Bestellungen, sowohl für Speisen als auch für Getränke.
# Benutzer können Bestellungen aufnehmen, ändern und stornieren. Eine digitale Speisekarte steht zur Verfügung. 
# Rechnungen können einzeln oder als Gesamtrechnung erstellt werden. Außerdem bietet die App eine Funktion zur 
# Anzeige von Monatsstatistiken, um einen Überblick über den Geschäftsverlauf zu erhalten.

# Abschlussprojekt Data-Analyst - Kurs 2025/05 - Phase 07 Python für Datenanalysten
###



# Import Module
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import regex as re
import os
import sys
import time
import tkinter as tk
import warnings
import webbrowser
from datetime import datetime
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from fpdf import FPDF


# Ignoriere spezifische Warnungen
warnings.filterwarnings("ignore", category=UserWarning, message="Boolean Series key will be reindexed to match DataFrame index")
warnings.filterwarnings("ignore", category=UserWarning)

# Sprung in das aktuelle Verzeichnis
script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)

# Prüfe auf vollständigkeit aller benötigten Daten
if not os.path.isdir('data'):
    print(f'Programmordner "data" fehlt. Programm kann nicht korrekt gestartet werden')
    sys.exit(1)
elif not os.path.isdir('tkinter_pics'):
    print(f'Programmordner "tkinter_pics" fehlt. Programm kann nicht korrekt gestartet werden')
    sys.exit(1)

# Erstellung benötigter Ordner
if not os.path.isdir('Rechnungen'):
    os.makedirs('Rechnungen')
if not os.path.isdir('Statistik'):
    os.makedirs('Statistik')

# Start Resturant - App
class Restaurant():
    # Laden der Bestelldaten:
    # Beim Start der Anwendung wird versucht, die offenen Bestellungen aus der Datei './data/Bestelldaten_offen.csv' zu laden. Falls die Datei nicht 
    # vorhanden oder fehlerhaft ist, wird ein leeres DataFrame mit den erforderlichen Spalten initialisiert (Bestell-ID, Datum, Tischnummer, 
    # Speise-ID, Speise, Menge, Status). Dies stellt sicher, dass die App auch ohne bestehende Bestelldaten ordnungsgemäß funktioniert.
    try:
        bestellungen_df = pd.read_csv('./data/Bestelldaten_offen.csv', dtype={'Menge': int, 'Tischnummer': int, 'Speise_ID': int})
    except:
        bestellungen_df = pd.DataFrame({
        'Bestell_ID': [],
        'Datum': [],
        'Tischnummer': [],
        'Speise_ID':[],
        'Speise': [],
        'Menge': [],
        'Status': []
    })

    # Laden der geschlossenen Bestelldaten:   
    # Beim Start der Anwendung wird versucht, die geschlossenen Bestellungen aus der Datei './data/Bestelldaten_geschlossen.csv' zu laden. Falls die Datei nicht 
    # vorhanden oder fehlerhaft ist, wird ein leeres DataFrame mit den erforderlichen Spalten initialisiert (Bestell-ID, Datum, Tischnummer, 
    # Speise-ID, Speise, Menge, Status). Dies stellt sicher, dass die App auch ohne bestehende Bestelldaten ordnungsgemäß funktioniert. 
    try:
        bestellungen_geschlossen_df = pd.read_csv('./data/Bestelldaten_geschlossen.csv', dtype={'Menge': int, 'Tischnummer': int, 'Speise_ID': int})
    except:
        bestellungen_geschlossen_df = pd.DataFrame({
        'Bestell_ID': [],
        'Datum': [],
        'Tischnummer': [],
        'Speise_ID':[],
        'Speise': [],
        'Menge': [],
        'Status': []
    })

    # Sicherstellung das beide Frames den richtigen Index gesetzt haben    
    bestellungen_df.set_index('Bestell_ID', inplace=True)
    bestellungen_geschlossen_df.set_index('Bestell_ID', inplace=True)

    # Laden der Speise- und Getränkekarte mit Details und Preisen
    speisekarte_df = pd.read_csv('./data/Speisekarte.csv', index_col='Speise_ID', dtype={'Speise_ID': int})
    getraenkekarte_df = pd.read_csv('./data/Getränkekarte.csv', index_col='Speise_ID', dtype={'Speise_ID': int})
    
    # Initialisierung der __init__ mit Übertrag des Tkinter - Root 
    def __init__(self, hintergrund) -> None:
        self.hintergrund = hintergrund
        self.mainframe()
    
    # Erneuerung des Background - Images
    def update_background(self, image_path: str) -> None:
        """
        Aktualisiert den Hintergrund des Canvas mit einem neuen Bild.

        Die Funktion:
        - Öffnet das Bild von dem angegebenen Pfad.
        - Ändert die Größe des Bildes auf 1200x800 Pixel.
        - Konvertiert das Bild in ein Format, das von Tkinter verwendet werden kann.
        - Löscht das bestehende Canvas und fügt das neue Hintergrundbild hinzu.
        - Speichert die Referenz zum neuen Hintergrundbild, um es in Tkinter korrekt anzuzeigen.
        - Aktualisiert das Canvas, um die Änderungen sichtbar zu machen.

        :param image_path: Der Pfad zur Bilddatei, die als Hintergrundbild verwendet werden soll.
        """
        
        # Öffnet das Bild von dem angegebenen Pfad
        self.bild = Image.open(image_path)
        
        # Ändert die Größe des Bildes auf 1200x800 Pixel
        self.bild = self.bild.resize((1200, 800))
        
        # Konvertiert das Bild in ein Format, das von Tkinter verwendet werden kann
        self.background_image = ImageTk.PhotoImage(self.bild)
        
        # Altes Canvas löschen
        self.hintergrund.delete("all")
        
        # Fügt das neue Hintergrundbild hinzu
        self.hintergrund.create_image(0, 0, image=self.background_image, anchor='nw')
        
        # Speichert die Referenz zum neuen Hintergrundbild
        self.hintergrund.image = self.background_image
        
        # Aktualisiert das Canvas, um die Änderungen sichtbar zu machen
        self.hintergrund.update() 

    # Erstellung des Tkinter - Hauptbildschirms
    def mainframe(self) -> None:
        """
        Erstellt das Hauptframe der Anwendung und fügt die Haupt-Buttons hinzu.
        
        Die Funktion:
        - Setzt den Hintergrund des Frames mithilfe eines Bildes.
        - Erstellt und positioniert das Startframe, das als Container für die Haupt-Buttons dient.
        - Fügt fünf Haupt-Buttons hinzu, die verschiedene Funktionen der Anwendung auslösen:
        - 'Speisekarte': Öffnet die Speisekarte.
        - 'Essen': Zeigt die Bestellmöglichkeiten für Essen.
        - 'Getränke': Zeigt die Bestellmöglichkeiten für Getränke.
        - 'Rechnungen': Zeigt die Rechnungen.
        - 'Abfragen': Zeigt Monatsdaten.
        """
        # Hauptframe setzen
        self.update_background('./tkinter_pics/Background_2.jpg')

        # Erstellung Startframe
        self.startframe = tk.LabelFrame(self.hintergrund, bg='#8b5a2b')        
        self.startframe_width = 1180
        self.startframe_height = 565
        self.startframe.place(x = 10, y = 225, width = self.startframe_width, height = self.startframe_height)

        # Erstellung der rechten Haupt-Buttons

        # Haupt-Button rechts -Speisekarte-
        speisekarte = tk.Button(self.startframe, text='Speisekarte', font=('arial', 20), bg='#cd853f', command= self.speisekarte)
        speisekarte.place(width=180, height=60, x=990, y=103)
        # Haupt-Button rechts -Essen-
        essen_bestellungen = tk.Button(self.startframe, text='Essen', font=('arial', 20), bg='#cd853f', command= self.bestellungen)
        essen_bestellungen.place(width=180, height=60, x=990, y=173)
        # Haupt-Button rechts -Getränke-
        getraenke_bestellungen = tk.Button(self.startframe, text='Getränke', font=('arial', 20), bg='#cd853f', command= self.getraenke)
        getraenke_bestellungen.place(width=180, height=60, x=990, y=243)
        # Haupt-Button rechts -Rechnungen-
        rechnungen = tk.Button(self.startframe, text='Rechnungen', font=('arial', 20), bg='#cd853f', command= self.rechnungen)
        rechnungen.place(width=180, height=60, x=990, y=313)
        # Haupt-Button rechts -Statistik-
        monatsdaten = tk.Button(self.startframe, text='Statistik', font=('arial', 20), bg='#cd853f', command= self.monatsdaten)
        monatsdaten.place(width=180, height=60, x=990, y=453)

    # Funktion für Haupt-Button -Speisekarte- um Speisekarte zu öffnen
    def speisekarte(self) -> None:
        """
        Öffnet die Speisekarte im PDF-Format.
        
        Die Funktion:
        - Öffnet die Datei './data/Speisekarte.pdf' im Standard-Webbrowser.
        """
        # Öffnet ./data/Speisekarte.pdf
        pdf_path: str = os.path.abspath('./data/Speisekarte.pdf')  # Relativer Pfad zur PDF-Datei
        webbrowser.open_new(pdf_path)

    # Funktion für Haupt-Button -Essen- um Bestellungen auszuführen
    def bestellungen(self) -> None:
        """
        Erstellt das Haupt-Frame für die Verwaltung von Essen-Bestellungen und fügt Navigationsbuttons hinzu.
        Die Funktion:
        - Erstellt ein Frame innerhalb des Start-Frames, das für die Verwaltung von Bestellungen verwendet wird.
        - Fügt obere Buttons zur Navigation in den verschiedenen Bestellfunktionen hinzu:
        - 'Neue Bestellung': Öffnet die Funktion zur Erstellung einer neuen Bestellung.
        - 'Storno / Liefern': Öffnet die Funktion zum Stornieren oder Liefern von Bestellungen.
        - 'Aktive Bestellungen': Öffnet die Funktion zur Anzeige aktiver Bestellungen.
        """  

        # Funktion für oberen Navigations-Button - Neue Bestellung -
        def neue_bestellung() -> None:
            """
            Erstellt ein neues Frame zur Aufnahme einer neuen Bestellung und fügt Buttons für die Tischauswahl hinzu.
            Die Funktion:
            - Erstellt ein Unter-Frame innerhalb des bestehenden Frames für neue Bestellungen.
            - Fügt Buttons für die Auswahl der Tische hinzu. Jeder Button ist für einen Tisch und ruft die Funktion `set_tisch_nummer` auf, um den Tisch auszuwählen.
            - Die Buttons werden in einer Schleife erstellt und in der Liste `tisch_buttons` gespeichert.
            """
            
            # Funktion nach Auswahl des Tisches
            def set_tisch_nummer(tisch_nummer: int) -> None:
                """
                Setzt die Tischnummer und zerstört alle Tasten in der Liste tisch_buttons.

                Args:
                    tisch_nummer (int): Die zu setzende Tischnummer.

                Returns:
                    None
                """
                tischnummer = tisch_nummer
                for button in tisch_buttons:
                    button.destroy()

                # Funktion für Button -Bestellung aufgeben-
                def bestellung_aufgeben(tischnummer: int) -> None:
                    """
                    Verarbeitet eine Bestellung und speichert die Daten in einer CSV-Datei.

                    :param tischnummer: Die Nummer des Tisches, von dem die Bestellung aufgegeben wird.
                    :type tischnummer: int
                    :return: Keine Rückgabewerte.
                    :rtype: None
                    """
                    # Initialisieren des Bestell-Dictionaries
                    speisen = {
                        'Speisen_ID': [],
                        'Menge': []
                    }
                    
                    # Durchlaufen der Speise-Labels und Befüllen des Dictionaries
                    for index, value in enumerate(speise_labels):
                        speisen['Speisen_ID'].append(index + 1)
                        speisen['Menge'].append(value.get())
                    
                    # Überprüfen, ob die Mengen nur Zahlen enthalten
                    matches = []
                    for i in speisen['Menge'][:]:
                        matches += re.findall(r'[^0-9]', str(i))
                    
                    # Fehlermeldung anzeigen, wenn nicht-numerische Werte gefunden wurden
                    if matches:
                        messagebox.showerror('Achtung', 'Fehlerhafte Menge')
                    else:
                        # Verarbeiten der Bestellungen
                        for id, menge in zip(speisen['Speisen_ID'], speisen['Menge']):
                            # Nur Bestellungen mit Menge > 0 verarbeiten
                            if menge > '0':  
                                # Bestell-ID automatisch ermitteln
                                bestell_id = self.bestellungen_df.index.max() + 1 if not self.bestellungen_df.empty else 1
                                while bestell_id in self.bestellungen_df.index or bestell_id in self.bestellungen_geschlossen_df.index:
                                    bestell_id += 1
                                bestell_id = int(bestell_id)
                                
                                # Datum auf den aktuellen Zeitpunkt setzen
                                datum = pd.Timestamp.now()

                                # tischnummer, speise_id und menge in Integer umwandeln
                                tischnummer = int(tischnummer)
                                speise_id = int(id)
                                menge = int(menge)    

                                # Speisenbezeichnung aus dem Speisekarten-DataFrame abrufen
                                speise = self.speisekarte_df.loc[speise_id, 'Speise'] 

                                # Status der Bestellung setzen
                                status = 'offen'    

                                # Erstellen des Bestell-Dictionaries mit Bezüge aus vorherigen Dictionary und Variablen
                                bestellung = {
                                    'Bestell_ID': bestell_id,
                                    'Datum': datum,
                                    'Tischnummer': tischnummer,
                                    'Speise_ID': speise_id,
                                    'Speise': speise,
                                    'Menge': menge,
                                    'Status': status
                                }
                                
                                # Umwandeln des Dictionaries in einen DataFrame
                                bestellung_df = pd.DataFrame([bestellung])
                                
                                # Überprüfen, ob self.bestellungen_df leer ist
                                if self.bestellungen_df.empty:
                                    # Direkt den neuen DataFrame zuweisen, wenn leer
                                    self.bestellungen_df = bestellung_df.set_index('Bestell_ID')
                                else:
                                    # Sonst die DataFrames zusammenführen
                                    self.bestellungen_df = pd.concat([self.bestellungen_df, bestellung_df.set_index('Bestell_ID')])
                        
                        # Speichern der Bestellungen in eine CSV-Datei
                        self.bestellungen_df.to_csv('./data/Bestelldaten_offen.csv')
                        
                        # Aufrufen der Funktion für aktive Bestellungen
                        aktive_bestellungen()
                    
                # Erstellung der Labels, Entrys und des -Bestellung aufgeben- Buttons 

                # Menge-Label oben
                menge_label = tk.Label(neue_bestellung_frame, text='Menge:', font=('arial', 20), bg='#8b5a2b', anchor='w')
                menge_label.place(x= 500 , y=10, width= 200, height= 30)
                # Info-Label welcher Tisch aktiv ist oben rechts
                tischnummer_label = tk.Label(neue_bestellung_frame, text=f'Tisch Nummer: {tisch_nummer}', font=('arial', 20), bg='#8b5a2b', anchor='w')
                tischnummer_label.place(x= 700 , y=10, width= 230, height= 30)
                # -Bestellung aufgeben- Button unten rechts
                bestellung_button = tk.Button(neue_bestellung_frame, text='Bestellung\naufgeben', font=('arial', 20), bg='#cd853f', command= lambda: bestellung_aufgeben(tischnummer))
                bestellung_button.place(x= 700 , y=340, width= 230, height= 70)

                # Folgend alle Essens-Gericht -> Label und Entry
                speise_id1_label = tk.Label(neue_bestellung_frame, text=self.speisekarte_df.loc[1, 'Speise'], font=('arial', 20), bg='#8b5a2b', anchor='w')
                speise_id1_label.place(x= 20 , y=60, width= 450, height= 30)
                speise_id1_entry = tk.Entry(neue_bestellung_frame, font=('arial', 20))
                speise_id1_entry.place(x= 500 , y=60, width= 100, height= 30)
                
                speise_id2_label = tk.Label(neue_bestellung_frame, text=self.speisekarte_df.loc[2, 'Speise'], font=('arial', 20), bg='#8b5a2b', anchor='w')
                speise_id2_label.place(x= 20 , y=95, width= 450, height= 30)
                speise_id2_entry = tk.Entry(neue_bestellung_frame, font=('arial', 20))
                speise_id2_entry.place(x= 500 , y=95, width= 100, height= 30)

                speise_id3_label = tk.Label(neue_bestellung_frame, text=self.speisekarte_df.loc[3, 'Speise'], font=('arial', 20), bg='#8b5a2b', anchor='w')
                speise_id3_label.place(x= 20 , y=130, width= 450, height= 30)
                speise_id3_entry = tk.Entry(neue_bestellung_frame, font=('arial', 20))
                speise_id3_entry.place(x= 500 , y=130, width= 100, height= 30)

                speise_id4_label = tk.Label(neue_bestellung_frame, text=self.speisekarte_df.loc[4, 'Speise'], font=('arial', 20), bg='#8b5a2b', anchor='w')
                speise_id4_label.place(x= 20 , y=165, width= 450, height= 30)
                speise_id4_entry = tk.Entry(neue_bestellung_frame, font=('arial', 20))
                speise_id4_entry.place(x= 500 , y=165, width= 100, height= 30)

                speise_id5_label = tk.Label(neue_bestellung_frame, text=self.speisekarte_df.loc[5, 'Speise'], font=('arial', 20), bg='#8b5a2b', anchor='w')
                speise_id5_label.place(x= 20 , y=200, width= 450, height= 30)
                speise_id5_entry = tk.Entry(neue_bestellung_frame, font=('arial', 20))
                speise_id5_entry.place(x= 500 , y=200, width= 100, height= 30)

                speise_id6_label = tk.Label(neue_bestellung_frame, text=self.speisekarte_df.loc[6, 'Speise'], font=('arial', 20), bg='#8b5a2b', anchor='w')
                speise_id6_label.place(x= 20 , y=235, width= 450, height= 30)
                speise_id6_entry = tk.Entry(neue_bestellung_frame, font=('arial', 20))
                speise_id6_entry.place(x= 500 , y=235, width= 100, height= 30)

                speise_id7_label = tk.Label(neue_bestellung_frame, text=self.speisekarte_df.loc[7, 'Speise'], font=('arial', 20), bg='#8b5a2b', anchor='w')
                speise_id7_label.place(x= 20 , y=270, width= 450, height= 30)
                speise_id7_entry = tk.Entry(neue_bestellung_frame, font=('arial', 20))
                speise_id7_entry.place(x= 500 , y=270, width= 100, height= 30)

                speise_id8_label = tk.Label(neue_bestellung_frame, text=self.speisekarte_df.loc[8, 'Speise'], font=('arial', 20), bg='#8b5a2b', anchor='w')
                speise_id8_label.place(x= 20 , y=305, width= 450, height= 30)
                speise_id8_entry = tk.Entry(neue_bestellung_frame, font=('arial', 20))
                speise_id8_entry.place(x= 500 , y=305, width= 100, height= 30)

                speise_id9_label = tk.Label(neue_bestellung_frame, text=self.speisekarte_df.loc[9, 'Speise'], font=('arial', 20), bg='#8b5a2b', anchor='w')
                speise_id9_label.place(x= 20 , y=340, width= 450, height= 30)
                speise_id9_entry = tk.Entry(neue_bestellung_frame, font=('arial', 20))
                speise_id9_entry.place(x= 500 , y=340, width= 100, height= 30)

                speise_id10_label = tk.Label(neue_bestellung_frame, text=self.speisekarte_df.loc[10, 'Speise'], font=('arial', 20), bg='#8b5a2b', anchor='w')
                speise_id10_label.place(x= 20 , y=375, width= 450, height= 30)
                speise_id10_entry = tk.Entry(neue_bestellung_frame, font=('arial', 20))
                speise_id10_entry.place(x= 500 , y=375, width= 100, height= 30)

                # Festhalten der Speise-Entrys zur weiteren Verwendung in nächster Funktion -bestellung_aufgeben-
                speise_labels = [speise_id1_entry, speise_id2_entry, speise_id3_entry, speise_id4_entry, speise_id5_entry, speise_id6_entry, speise_id7_entry, speise_id8_entry, speise_id9_entry, speise_id10_entry]

            # Erstellung Unter-Frame zum Start einer neuen Bestellung
            neue_bestellung_frame = tk.LabelFrame(self.bestellung_frame, bg='#8b5a2b')
            neue_bestellung_frame.place(x=20, y=100, width=940, height=445)

            # Erstellung Tischbuttons zur Auswahl des Tisches für Essen-Bestellung
            # tisch_buttons [] <-- Hier werden in der Schleife die Tische eingetragen um sie im nächsten Frame mit .destroy zu löschen    
            tisch_buttons = []
            for i in range(0, 10):
                # Erstellung eines Buttons für jeden Tisch
                tisch = tk.Button(
                    neue_bestellung_frame,
                    text=f'Tisch {i+1}',
                    font=('arial', 20),
                    bg='#cd853f',
                    command=lambda i=i: set_tisch_nummer(i+1)  # Setzt die Tischnummer, die dem Button zugeordnet ist
                )
                tisch.place(x=20, y=20 + i*40, width=120, height=30)
                tisch_buttons.append(tisch)           
        
        # Erstellung der Funktion für oberen Navigations-Button -aktive Bestellungen-
        def aktive_bestellungen() -> None:
            """
            Aktualisiert und zeigt die offenen Bestellungen in einem Treeview-Widget an.
            
            Die Methode filtert die Bestellungen, die den Status 'offen' haben und deren
            Speise_ID kleiner als 100 ist. Die gefilterten Daten werden in einem Treeview-Widget
            angezeigt, das in einem Tkinter-Frame eingebettet ist.
            """
            
            # Definiert die Spaltenüberschriften für das Treeview-Widget
            columns = ['Bestell_ID'] + list(self.bestellungen_df[
                (self.bestellungen_df['Status'] == 'offen') &
                (self.bestellungen_df['Speise_ID'] < 100)
            ].columns)

            # Erzeugt ein Treeview-Widget und zeigt nur die Kopfzeilen an
            tree = ttk.Treeview(self.bestellung_frame, columns=columns, show='headings')

            # Spaltenüberschriften festlegen und zentrieren
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150, anchor='center')

            # Daten in die Tabelle einfügen
            for index, row in self.bestellungen_df.iterrows():
                if row['Status'] == 'offen' and row['Speise_ID'] < 100:
                    datum_formatiert = pd.to_datetime(row['Datum']).strftime('%d.%m.%Y %H:%M')
                    tree.insert('', 'end', values=[index] + [datum_formatiert] + row.drop('Datum').tolist())

            # Tabelle in Tkinter-Fenster einfügen
            tree.place(x=20, y=100, width=940, height=445)

            # Spaltenbreite anpassen
            if tree.get_children():
                for col in columns:
                    max_width = max(len(str(tree.set(item, col))) for item in tree.get_children())
                    tree.column(col, width=max_width * 10)

            # Sicherstellen, dass das Treeview-Widget alle Aufgaben abgeschlossen hat
            tree.update_idletasks()  
        
        # Erstellung der Funktion für oberen Navigations-Button -Storno/Liefer-
        def storno_liefer() -> None:
            """
            Erzeugt ein LabelFrame für die Stornierung oder Lieferung von Bestellungen und zeigt
            eine Tabelle der offenen Bestellungen an, basierend auf der Tischnummer.

            Die Funktion:
            - Erstellt und platziert ein LabelFrame für die Benutzeroberfläche.
            - Fügt Widgets wie Labels, Eingabefelder und Buttons hinzu.
            - Filtert die offenen Bestellungen und zeigt diese in einem Treeview an.
            """

            # Funktion zur Verarbeitung der Tischnummer mit Weiterverwendung
            def eingabe_tischnummer() -> None:
                """
                Verarbeitet die Eingabe der Tischnummer, filtert die offenen Bestellungen nach der angegebenen Tischnummer
                und zeigt die entsprechenden Daten in einem Treeview an. Fügt zudem verschiedene Buttons für weitere Aktionen hinzu.

                Die Funktion:
                - Liest die Tischnummer aus dem Eingabefeld.
                - Validiert die Eingabe und zeigt eine Fehlermeldung bei ungültigen Eingaben.
                - Filtert die Bestellungen nach Tischnummer und zeigt die Daten in einem Treeview an.
                - Fügt zusätzliche Widgets wie Eingabefelder und Buttons für die Bearbeitung von Bestellungen hinzu.
                """

                # Funktion für Button -Menge ändern-
                def menge_aendern() -> None:
                    """
                    Ändert die Menge einer Bestellung basierend auf der im Eingabefeld angegebenen Bestell_ID und neuen Menge.
                    Die Funktion prüft die Gültigkeit der Bestell_ID und der Menge, aktualisiert die Menge im DataFrame
                    und speichert die aktualisierten Bestellungen in einer CSV-Datei.

                    Die Funktion:
                    - Liest die Bestell_ID und die neue Menge aus den Eingabefeldern.
                    - Überprüft die Gültigkeit der Bestell_ID und der Menge und zeigt Fehlermeldungen bei ungültigen Eingaben an.
                    - Aktualisiert die Menge der Bestellung im DataFrame und speichert die Daten in einer CSV-Datei.
                    - Zeigt eine Bestätigungsnachricht an, wenn die Menge erfolgreich geändert wurde.
                    """
                    
                    try:
                        # Liest die Bestell_ID aus dem Eingabefeld
                        bestell_id = ID_label_entry.get()
                    except Exception:
                        # Zeigt eine Fehlermeldung an, wenn die Bestell_ID nicht gefunden wird
                        messagebox.showinfo('Achtung', f'Bestell_ID: {bestell_id} nicht gefunden...')
                    
                    if bestell_id < '1' or bestell_id is None:
                        # Zeigt eine Fehlermeldung an, wenn die Bestell_ID ungültig ist
                        messagebox.showinfo('Achtung', f'Bestell_ID: {bestell_id} nicht gefunden...')
                    else:         
                        try:
                            # Versucht, die Bestell_ID in eine ganze Zahl umzuwandeln
                            bestell_id = int(bestell_id)
                        except ValueError:
                            # Zeigt eine Fehlermeldung bei fehlerhafter Bestell_ID an
                            messagebox.showerror('Achtung', 'Fehlerhafte Eingabe -> Bestell_ID')
                        
                        # Liest die neue Menge aus dem Eingabefeld
                        menge = neue_menge_entry.get()
                        
                        try:
                            # Versucht, die neue Menge in eine ganze Zahl umzuwandeln
                            menge = int(menge)
                        except ValueError:
                            # Zeigt eine Fehlermeldung bei fehlerhafter Menge an
                            messagebox.showerror('Achtung', 'Fehlerhafte Eingabe -> Menge')
                        
                        if menge <= 0:
                            # Zeigt eine Fehlermeldung an, wenn die Menge kleiner oder gleich 0 ist
                            messagebox.showerror('Achtung', 'Menge darf nicht 0 sein...\nZum Stornieren Storno wählen!')
                        else:
                            # Aktualisiert die Menge der Bestellung im DataFrame
                            self.bestellungen_df.loc[bestell_id, 'Menge'] = menge
                            messagebox.showinfo('Hinweis', 'Menge erfolgreich geändert')
                            
                            # Speichert die aktualisierten Bestellungen in einer CSV-Datei
                            self.bestellungen_df.to_csv('./data/Bestelldaten_offen.csv')

                # Funktion für Button -liefer-  
                def liefer() -> None:
                    """
                    Liefert eine Bestellung basierend auf der im Eingabefeld angegebenen Bestell_ID aus.
                    Die Funktion prüft die Bestell_ID, aktualisiert den Status der Bestellung auf 'geliefert' und
                    speichert die aktualisierten Bestellungen in einer CSV-Datei. Zudem wird der entsprechende
                    Eintrag im Treeview entfernt, wenn die Bestellung erfolgreich geliefert wurde.

                    Die Funktion:
                    - Liest die Bestell_ID aus dem Eingabefeld.
                    - Überprüft die Gültigkeit der Bestell_ID und zeigt Fehlermeldungen bei ungültigen IDs an.
                    - Ändert den Status der Bestellung auf 'geliefert' und speichert die Daten in einer CSV-Datei.
                    - Entfernt den Eintrag aus dem Treeview, wenn die Bestell_ID übereinstimmt.
                    """
                    
                    try:
                        # Liest die Bestell_ID aus dem Eingabefeld
                        bestell_id = ID_label_entry.get()
                    except Exception:
                        # Zeigt eine Fehlermeldung an, wenn die Bestell_ID nicht gefunden wird
                        messagebox.showinfo('Achtung', f'Bestell_ID: {bestell_id} nicht gefunden...')
                    
                    if bestell_id < '1' or bestell_id is None:
                        # Zeigt eine Fehlermeldung an, wenn die Bestell_ID ungültig ist
                        messagebox.showinfo('Achtung', f'Bestell_ID: {bestell_id} nicht gefunden...')
                    else:
                        try:
                            # Versucht, die Bestell_ID in eine ganze Zahl umzuwandeln
                            bestell_id = int(bestell_id)
                        except ValueError:
                            # Zeigt eine Fehlermeldung bei fehlerhafter Eingabe an
                            messagebox.showerror('Achtung', 'Fehlerhafte Eingabe -> Bestell_Id')
                        else:
                            # Setzt den Status der Bestellung auf 'geliefert'
                            self.bestellungen_df.loc[bestell_id, 'Status'] = 'geliefert'
                            
                            # Überprüft, ob die Menge der Bestellung 0 ist, und ändert den Status entsprechend
                            if self.bestellungen_df.loc[bestell_id, 'Menge'] == 0:
                                self.bestellungen_df.loc[bestell_id, 'Status'] = 'geliefert'
                            
                            # Zeigt eine Bestätigungsnachricht an
                            messagebox.showinfo('Hinweis', f'Bestell_ID: {bestell_id} geliefert')
                            
                            # Speichert die aktualisierten Bestellungen in einer CSV-Datei
                            self.bestellungen_df.to_csv('./data/Bestelldaten_offen.csv')
                            
                            # Entfernt den Eintrag aus dem Treeview, wenn die Bestell_ID übereinstimmt
                            for item_id in tree.get_children():
                                # Hole die Werte des aktuellen Eintrags
                                values = tree.item(item_id, 'values')
                                # Prüfe, ob der erste Wert (Bestell_ID) mit der angegebenen ID übereinstimmt
                                if str(values[0]).startswith(str(bestell_id)):
                                    # Lösche den Eintrag, wenn die Bedingung erfüllt ist
                                    tree.delete(item_id)
                            
                # Funktion für Button -Liefer alles-
                def liefer_alles() -> None:
                    """
                    Liefert alle offenen Bestellungen für die im Eingabefeld angegebene Tischnummer aus.
                    Die Funktion filtert die offenen Bestellungen nach Tischnummer und aktualisiert deren Status auf 'geliefert'.
                    Anschließend werden die aktualisierten Bestellungen in einer CSV-Datei gespeichert.

                    Die Funktion:
                    - Liest die Tischnummer aus dem Eingabefeld.
                    - Filtert die offenen Bestellungen nach der angegebenen Tischnummer und Speise_ID.
                    - Überprüft, ob gefilterte Bestellungen vorhanden sind.
                    - Ändert den Status der Bestellungen auf 'geliefert' und speichert die Daten in einer CSV-Datei.
                    - Zeigt eine Bestätigungsnachricht an und ruft eine weitere Funktion auf, um die aktiven Bestellungen zu aktualisieren.
                    """
                    
                    # Tischnummer aus dem Eingabefeld holen
                    tischnummer = tischnummer_entry.get()
                    tischnummer = int(tischnummer)
                    
                    # DataFrame filtern
                    gefiltert_df = self.bestellungen_df[self.bestellungen_df['Status'] == 'offen'][self.bestellungen_df['Tischnummer'] == tischnummer][self.bestellungen_df['Speise_ID'] < 100]
                    
                    # Überprüfen, ob gefilterte Daten vorhanden sind
                    if gefiltert_df.empty:
                        messagebox.showinfo('Achtung', f'Keine offenen Essens-Bestellungen für Tischnummer: {tischnummer}')
                    else:
                        # Status der gefilterten Bestellungen auf 'geliefert' ändern
                        self.bestellungen_df.loc[gefiltert_df.index, 'Status'] = 'geliefert'
                        messagebox.showinfo('Hinweis', f'Alle Essen für Tischnummer: {tischnummer} geliefert.')
                        
                        # Speichert die aktualisierten Bestellungen in einer CSV-Datei
                        self.bestellungen_df.to_csv('./data/Bestelldaten_offen.csv')
                        
                        # Ruft die Funktion zur Aktualisierung der aktiven Bestellungen auf
                        aktive_bestellungen()

                # Funktion für Button -Storno-
                def storno() -> None:
                    """
                    Verarbeitet die Stornierung einer Bestellung basierend auf der eingegebenen Bestell_ID.
                    Wenn die ID gültig ist, wird der Status der Bestellung auf 'storniert' gesetzt, die Bestellung
                    wird in die geschlossenen Bestellungen verschoben und die Daten werden in CSV-Dateien gespeichert.

                    Die Funktion:
                    - Liest die Bestell_ID aus dem Eingabefeld.
                    - Validiert die Eingabe und zeigt Fehlermeldungen bei ungültigen Eingaben an.
                    - Fragt den Benutzer, ob die Bestellung gelöscht werden soll.
                    - Wenn die Bestellung gelöscht wird, aktualisiert sie die DataFrames und speichert sie in CSV-Dateien.
                    - Zeigt die aktualisierten offenen Bestellungen in einem Treeview an.
                    """
                    
                    # Liest die Bestell_ID aus dem Eingabefeld
                    bestell_id = ID_label_entry.get()
                    
                    try:
                        # Versucht, die Bestell_ID in eine ganze Zahl umzuwandeln
                        bestell_id = int(bestell_id)
                    except ValueError:
                        # Zeigt eine Fehlermeldung bei ungültiger Bestell_ID an
                        messagebox.showerror('Achtung', 'Falsche Eingabe -> Bestell_ID')
                    else:
                        # Überprüft, ob die Bestell_ID im DataFrame vorhanden ist
                        if bestell_id in self.bestellungen_df.index:
                            # Fragt den Benutzer, ob die Bestellung gelöscht werden soll
                            loeschen = messagebox.askquestion('Achtung', f'Bestell_ID: {bestell_id}\nengültig löschen ?')
                            if loeschen == 'yes':
                                # Setzt den Status der Bestellung auf 'storniert'
                                self.bestellungen_df.loc[bestell_id, 'Status'] = 'storniert'
                                
                                # Verschiebt die Bestellung in den DataFrame für geschlossene Bestellungen
                                self.bestellungen_geschlossen_df = pd.concat([self.bestellungen_geschlossen_df, self.bestellungen_df.loc[[bestell_id]]])
                                
                                # Löscht die Bestellung aus dem DataFrame der offenen Bestellungen
                                self.bestellungen_df.drop(bestell_id, inplace=True)
                                
                                # Speichert die aktualisierten DataFrames in CSV-Dateien
                                self.bestellungen_df.to_csv('./data/Bestelldaten_offen.csv')
                                self.bestellungen_geschlossen_df.to_csv('./data/Bestelldaten_geschlossen.csv')
                                
                                # Zeigt eine Bestätigungsnachricht an
                                messagebox.showinfo('Hinweis', 'Bestellung erfolgreich storniert!')

                                # Filtert die offenen Bestellungen nach Tischnummer und Speise_ID
                                gefiltert_df = self.bestellungen_df[self.bestellungen_df['Status'] == 'offen'][self.bestellungen_df['Tischnummer'] == eingabe_tischnummer][self.bestellungen_df['Speise_ID'] < 100]
                                
                                # Definiert die Spalten des Treeviews
                                columns = ['Bestell_ID'] + list(gefiltert_df.columns)
                                tree = ttk.Treeview(storno_liefer_frame, columns=columns, show='headings')
                                
                                if len(gefiltert_df) < 1:
                                    # Zeigt eine Info-Nachricht an, wenn keine offenen Bestellungen vorhanden sind
                                    messagebox.showinfo('Achtung', f'Keine offenen Bestellungen für Tischnummer: {eingabe_tischnummer}')
                                else:
                                    # Spaltenüberschriften festlegen und zentrieren
                                    for col in columns:
                                        tree.heading(col, text=col)
                                        tree.column(col, width=150, anchor='center')
                                    
                                    # Daten in die Tabelle einfügen
                                    for index, row in gefiltert_df.iterrows():
                                        # Datum formatieren
                                        datum_formatiert = pd.to_datetime(row['Datum']).strftime('%d.%m.%Y %H:%M')
                                        # Zeile mit formatiertem Datum und Index (Bestell_ID) einfügen
                                        tree.insert('', 'end', values=[index] + [datum_formatiert] + row.drop('Datum').tolist())
                                    
                                    # Tabelle in Tkinter-Fenster einfügen
                                    tree.place(x=20, y=225, width=900, height=200)
                                    
                                    if tree.get_children():
                                        for col in columns:
                                            # Berechnet die maximale Breite für jede Spalte
                                            max_width = max(len(str(tree.set(item, col))) for item in tree.get_children())
                                            tree.column(col, width=max_width * 10)
                            else:
                                # Zeigt eine Info-Nachricht an, wenn der Storniervorgang abgebrochen wurde
                                messagebox.showinfo('Hinweis', 'Storniervorgang abgebrochen!')
                        else:
                            # Zeigt eine Warnung an, wenn die Bestell_ID nicht gefunden wird
                            messagebox.showwarning('Achtung', f'Bestell_ID {bestell_id} nicht gefunden')
                
                # Liest die Tischnummer aus dem Eingabefeld
                eingabe_tischnummer = tischnummer_entry.get()
                
                try:
                    eingabe_tischnummer = int(eingabe_tischnummer)
                except ValueError:
                    # Zeigt eine Fehlermeldung bei fehlerhafter Eingabe
                    messagebox.showerror('Achtung', 'Fehlerhafte Eingabe')
                    return

                # Filtert die offenen Bestellungen nach der Tischnummer
                gefiltert_df = self.bestellungen_df[self.bestellungen_df['Status'] == 'offen'][self.bestellungen_df['Tischnummer'] == eingabe_tischnummer]                
                if len(gefiltert_df) < 1:
                    # Zeigt eine Info-Nachricht an, wenn keine offenen Bestellungen vorhanden sind
                    messagebox.showinfo('Achtung', f'Keine offenen Bestellungen für Tischnummer: {eingabe_tischnummer}')
                    return
                # Filtert zusätzlich nach Speise_ID < 100 ( Essen )
                gefiltert_df = gefiltert_df[self.bestellungen_df['Speise_ID'] < 100]
                
                # Definiert die Spalten des Treeviews
                columns = ['Bestell_ID'] + list(gefiltert_df.columns)
                tree = ttk.Treeview(storno_liefer_frame, columns=columns, show='headings')
                
                # Spaltenüberschriften festlegen und zentrieren
                for col in columns:
                    tree.heading(col, text=col)
                    tree.column(col, width=150, anchor='center')
                
                # Daten in die Tabelle einfügen
                for index, row in gefiltert_df.iterrows():
                    # Datum formatieren
                    datum_formatiert = pd.to_datetime(row['Datum']).strftime('%d.%m.%Y %H:%M')
                    # Zeile mit formatiertem Datum und Index (Bestell_ID) einfügen
                    tree.insert('', 'end', values=[index] + [datum_formatiert] + row.drop('Datum').tolist())
                
                # Tabelle in Tkinter-Fenster einfügen
                tree.place(x=20, y=225, width=900, height=200)

                if tree.get_children():
                    for col in columns:
                        # Berechnet die maximale Breite für jede Spalte
                        max_width = max(len(str(tree.set(item, col))) for item in tree.get_children())
                        tree.column(col, width=max_width * 10)
                
                # Label und Eingabefeld für die Bestell_ID
                ID_label = tk.Label(
                    storno_liefer_frame,
                    text='Bestell_ID eingeben:',
                    font=('arial', 20),
                    bg='#8b5a2b',
                    anchor='w'
                )
                ID_label.place(x=20, y=90, width=300, height=30)
                ID_label_entry = tk.Entry(storno_liefer_frame, font=('arial', 20))
                ID_label_entry.place(x=350, y=90, width=100, height=30)
                
                # Label und Eingabefeld für die neue Menge
                menge_label = tk.Label(storno_liefer_frame, text='Neue Menge:', font=('arial', 20), bg='#8b5a2b', anchor='w')
                menge_label.place(x=20, y=130, width=300, height=30)
                neue_menge_entry = tk.Entry(storno_liefer_frame, font=('arial', 20))
                neue_menge_entry.place(x=350, y=130, width=100, height=30)
                
                # Buttons für verschiedene Aktionen ->

                # Button für Aktion -Menge verändern-
                menge_button = tk.Button(storno_liefer_frame, text='Menge ändern', font=('arial', 20), bg='#cd853f', command=menge_aendern)
                menge_button.place(x=740, y=128, width=180, height=35)
                # Button für Aktion -Positionen einzeln liefern-
                liefer_button = tk.Button(storno_liefer_frame, text='Liefer', font=('arial', 20), bg='#cd853f', command=liefer)
                liefer_button.place(x=740, y=88, width=180, height=35)
                # Button für Aktion -Stornieren-
                storno_button = tk.Button(storno_liefer_frame, text='Storno', font=('arial', 20), bg='#cd853f', command=storno)
                storno_button.place(x=740, y=178, width=180, height=35)
                # Button für Aktion -Alles liefern-
                liefer_alles_button = tk.Button(storno_liefer_frame, text='Liefer alle\nEssen', font=('arial', 20), bg='#cd853f', command=liefer_alles)
                liefer_alles_button.place(x=740, y=20, width=180, height=60)
           
            if len(self.bestellungen_df[self.bestellungen_df['Status'] == 'offen'][self.bestellungen_df['Speise_ID'] < 100]) < 1:
                messagebox.showinfo('Achtung', 'Keine offenen Bestellungen vorhanden')
            else:
                # Erstellen des Frames für die Stornierung/Lieferung
                storno_liefer_frame = tk.LabelFrame(self.bestellung_frame, bg='#8b5a2b')
                storno_liefer_frame.place(x=20, y=100, width=940, height=445)

                # Label für die Eingabe der Tischnummer
                tischnummer_label = tk.Label(storno_liefer_frame, text='Tischnummer eingeben:', font=('arial', 20), bg='#8b5a2b', anchor='w')
                tischnummer_label.place(x=20, y=20, width=300, height=30)
                
                # Eingabefeld für die Tischnummer
                tischnummer_entry = tk.Entry(storno_liefer_frame, font=('arial', 20))
                tischnummer_entry.place(x=350, y=20, width=100, height=30)
                
                # Button zur Suche nach Bestellungen anhand der Tischnummer
                tischnummer_button = tk.Button(storno_liefer_frame, text='Suche', font=('arial', 20), bg='#cd853f', command=eingabe_tischnummer, anchor='center')
                tischnummer_button.place(x=500, y=20, width=100, height=30)

                # Filtert die Bestellungen nach Status 'offen' und Speise_ID < 100 ( Essen )
                gefiltert_df = self.bestellungen_df[
                self.bestellungen_df['Status'] == 'offen'][self.bestellungen_df['Speise_ID'] < 100]

                # Definiert die Spalten des Treeviews
                columns = ['Bestell_ID'] + list(gefiltert_df.columns)
                tree = ttk.Treeview(storno_liefer_frame, columns=columns, show='headings')

                if len(gefiltert_df) < 1:
                    # Zeigt eine Nachricht an, wenn keine offenen Bestellungen vorhanden sind
                    messagebox.showinfo(
                        'Achtung',
                        f'Keine offenen Bestellungen für Tischnummer: {eingabe_tischnummer}'
                    )
                else:
                    # Spaltenüberschriften festlegen und zentrieren
                    for col in columns:
                        tree.heading(col, text=col)
                        tree.column(col, width=150, anchor='center')
                    
                    # Daten in die Tabelle einfügen
                    for index, row in gefiltert_df.iterrows():
                        # Datum formatieren
                        datum_formatiert = pd.to_datetime(row['Datum']).strftime('%d.%m.%Y %H:%M')
                        # Zeile mit formatiertem Datum und Index (Bestell_ID) einfügen
                        tree.insert('', 'end', values=[index] + [datum_formatiert] + row.drop('Datum').tolist())
                    
                    # Tabelle in Tkinter-Fenster einfügen
                    tree.place(x=20, y=225, width=900, height=200)

                    if tree.get_children():
                        for col in columns:
                            # Berechnet die maximale Breite für jede Spalte
                            max_width = max(len(str(tree.set(item, col))) for item in tree.get_children())
                            tree.column(col, width=max_width * 10)

        # Erstellung Frame für Essen-Bestellungen
        self.bestellung_frame = tk.LabelFrame(self.startframe, bg='#8b4513')
        self.bestellung_frame.place(x = 0, y = 0, width = 980, height = 565)

        # Erstelle obere Buttons zur Navigation in Essen-Bestellungen

        # Neue Bestellung-Button
        neue_bestellung_button = tk.Button(self.bestellung_frame, text= 'Neue Bestellung', font= ('arial', 20), bg= '#cd853f', command= neue_bestellung)
        neue_bestellung_button.place(width=300, height=60, x=20, y=20)
        # Storno/Liefer-Button
        bestellung_stornoliefer_button = tk.Button(self.bestellung_frame, text= 'Storno / Liefern', font= ('arial', 20), bg= '#cd853f', command= storno_liefer)
        bestellung_stornoliefer_button.place(width=300, height=60, x=340, y=20)
        # Aktive Bestellungen-Button
        aktive_bestellungen_button = tk.Button(self.bestellung_frame, text= 'Aktive Bestellungen', font= ('arial', 20), bg= '#cd853f', command= aktive_bestellungen)
        aktive_bestellungen_button.place(width=300, height=60, x=660, y=20)

    # Funktion für Haupt-Button -Getränke- um Bestellungen auszuführen
    def getraenke(self) -> None:
        """
        Erstellt das Frame für Getränke-Bestellungen und fügt die entsprechenden Buttons hinzu.

        Die Funktion:
        - Erstellt ein neues LabelFrame innerhalb des Startframes zur Verwaltung der Getränke-Bestellungen.
        - Fügt drei Buttons hinzu:
            - 'Neue Bestellung': Startet den Prozess für eine neue Bestellung.
            - 'Storno / Liefern': Öffnet die Ansicht zum Stornieren oder Liefern von Bestellungen.
            - 'Aktive Bestellungen': Zeigt die aktiven Bestellungen an.
        """
         # Funktion für oberen Navigations-Button - Neue Bestellung -   
        def neue_bestellung() -> None:
            """
            Erstellt das Frame zur Eingabe einer neuen Bestellung und fügt Tisch-Buttons zur Auswahl hinzu.

            Die Funktion:
            - Erstellt ein neues LabelFrame innerhalb des Bestellungs-Frames.
            - Fügt 10 Buttons hinzu, die den jeweiligen Tischnummern zugeordnet sind.
            - Jeder Button wählt eine Tischnummer aus, die über die Funktion `set_tisch_nummer` weiterverarbeitet wird.
            """
            
            # Funktion für Button -Bestellung aufgeben-
            def set_tisch_nummer(tisch_nummer: int) -> None:
                """
                Setzt die Tischnummer und bereitet das UI für die Bestellung vor, indem es die entsprechenden Labels und Eingabefelder anzeigt.
                
                Args:
                    tisch_nummer (int): Die ausgewählte Tischnummer für die Bestellung.
                """
                # Speichern der Tischnummer
                tischnummer = tisch_nummer

                # Löschen der vorhandenen Tasten für die Tischauswahl
                for button in tisch_buttons:
                    button.destroy()

                # Funktion für Button -Bestellung aufgeben-
                def bestellung_aufgeben(tischnummer: int) -> None:
                    """
                    Verarbeitet die Bestellung für den angegebenen Tisch, prüft die eingegebenen Mengen auf Fehler und speichert die Bestellung in einer CSV-Datei.
                    
                    Args:
                        tischnummer (int): Die Tischnummer, für die die Bestellung aufgegeben wird.
                    """
                    tischnummer = tischnummer

                    # Initialisierung eines Wörterbuchs für die Getränke- und Mengenangaben
                    getraenke = {
                        'Speise_ID': [],  # Liste der Speise-IDs
                        'Menge': []  # Liste der zugehörigen Mengen
                    }

                    # Iteration durch die eingegebenen Werte (Mengen) und Speichern der Speise-IDs und Mengen
                    for index, value in enumerate(getraenke_labels):
                        getraenke['Speise_ID'].append(index + 1)
                        getraenke['Menge'].append(value.get())

                    # Überprüfung auf nicht numerische Eingaben in den Mengenfeldern
                    matches = []
                    for i in getraenke['Menge'][:]:
                        matches += re.findall(r'[^0-9]', str(i))

                    # Fehlermeldung, falls nicht numerische Zeichen in den Mengen enthalten sind
                    if matches:
                        messagebox.showerror('Achtung', 'Fehlerhafte Menge')
                    else:
                        # Iteration über die Speise-IDs und Mengen, um Bestellungen für gültige Mengen (> 0) zu generieren
                        for id, menge in zip(getraenke['Speise_ID'], getraenke['Menge']):
                            if menge > '0':
                                # Automatische Zuweisung der Bestell-ID, abhängig von vorhandenen Bestellungen
                                bestell_id = self.bestellungen_df.index.max() + 1 if not self.bestellungen_df.empty else 1
                                bestell_id = int(bestell_id)

                                # Automatisches Erfassen des aktuellen Datums
                                datum = pd.Timestamp.now()

                                # Konvertierung der Tischnummer, Speise_ID und menge in einen Integer und Anpassung an Getränke ID mit +100
                                tischnummer = int(tischnummer)
                                speise_id = int(id) + 100
                                menge = int(menge)

                                # Abruf der Speise aus der Getränkekarte
                                getraenke = self.getraenkekarte_df.loc[speise_id, 'Speise']

                                # Setzen des Status der Bestellung auf 'offen'
                                status = 'offen'

                                # Erstellung eines Dictionary für die aktuelle Bestellung
                                bestellung = {
                                    'Bestell_ID': bestell_id,
                                    'Datum': datum,
                                    'Tischnummer': tischnummer,
                                    'Speise_ID': speise_id,
                                    'Speise': getraenke,
                                    'Menge': menge,
                                    'Status': status
                                }

                                # Konvertierung der Bestellung in einen DataFrame
                                bestellung_df = pd.DataFrame([bestellung])

                                # Überprüfen, ob self.bestellungen_df leer ist
                                if self.bestellungen_df.empty:
                                    # Falls leer, neuen DataFrame setzen und Index festlegen
                                    self.bestellungen_df = bestellung_df.set_index('Bestell_ID')
                                else:
                                    # Zusammenfügen des neuen DataFrames mit bestehenden Bestellungen
                                    self.bestellungen_df = pd.concat([self.bestellungen_df, bestellung_df.set_index('Bestell_ID')])

                        # Speichern der offenen Bestellungen in einer CSV-Datei
                        self.bestellungen_df.to_csv('./data/Bestelldaten_offen.csv')

                        # Aktualisierung der aktiven Bestellungen
                        aktive_bestellungen()
                    
                # Erstellung der Labels, Entrys und des -Bestellung aufgeben- Buttons

                # Menge-Label oben
                menge_label = tk.Label(neue_bestellung_frame, text='Menge:', font=('arial', 20), bg='#8b5a2b', anchor='w')
                menge_label.place(x= 500 , y=10, width= 200, height= 30)
                # Info-Label welcher Tisch aktiv ist oben rechts
                tischnummer_label = tk.Label(neue_bestellung_frame, text=f'Tisch Nummer: {tisch_nummer}', font=('arial', 20), bg='#8b5a2b', anchor='w')
                tischnummer_label.place(x= 700 , y=10, width= 230, height= 30)
                # -Bestellung aufgeben- Button unten rechts
                bestellung_button = tk.Button(neue_bestellung_frame, text='Bestellung\naufgeben', font=('arial', 20), bg='#cd853f', command= lambda: bestellung_aufgeben(tischnummer))
                bestellung_button.place(x= 700 , y=340, width= 230, height= 70)

                # Folgend alle Essens-Gericht -> Label und Entry
                speise_id1_label = tk.Label(neue_bestellung_frame, text=self.getraenkekarte_df.loc[101, 'Speise'], font=('arial', 20), bg='#8b5a2b', anchor='w')
                speise_id1_label.place(x= 20 , y=60, width= 450, height= 30)
                speise_id1_entry = tk.Entry(neue_bestellung_frame, font=('arial', 20))
                speise_id1_entry.place(x= 500 , y=60, width= 100, height= 30)
                
                speise_id2_label = tk.Label(neue_bestellung_frame, text=self.getraenkekarte_df.loc[102, 'Speise'], font=('arial', 20), bg='#8b5a2b', anchor='w')
                speise_id2_label.place(x= 20 , y=95, width= 450, height= 30)
                speise_id2_entry = tk.Entry(neue_bestellung_frame, font=('arial', 20))
                speise_id2_entry.place(x= 500 , y=95, width= 100, height= 30)

                speise_id3_label = tk.Label(neue_bestellung_frame, text=self.getraenkekarte_df.loc[103, 'Speise'], font=('arial', 20), bg='#8b5a2b', anchor='w')
                speise_id3_label.place(x= 20 , y=130, width= 450, height= 30)
                speise_id3_entry = tk.Entry(neue_bestellung_frame, font=('arial', 20))
                speise_id3_entry.place(x= 500 , y=130, width= 100, height= 30)

                speise_id4_label = tk.Label(neue_bestellung_frame, text=self.getraenkekarte_df.loc[104, 'Speise'], font=('arial', 20), bg='#8b5a2b', anchor='w')
                speise_id4_label.place(x= 20 , y=165, width= 450, height= 30)
                speise_id4_entry = tk.Entry(neue_bestellung_frame, font=('arial', 20))
                speise_id4_entry.place(x= 500 , y=165, width= 100, height= 30)

                speise_id5_label = tk.Label(neue_bestellung_frame, text=self.getraenkekarte_df.loc[105, 'Speise'], font=('arial', 20), bg='#8b5a2b', anchor='w')
                speise_id5_label.place(x= 20 , y=200, width= 450, height= 30)
                speise_id5_entry = tk.Entry(neue_bestellung_frame, font=('arial', 20))
                speise_id5_entry.place(x= 500 , y=200, width= 100, height= 30)

                speise_id6_label = tk.Label(neue_bestellung_frame, text=self.getraenkekarte_df.loc[106, 'Speise'], font=('arial', 20), bg='#8b5a2b', anchor='w')
                speise_id6_label.place(x= 20 , y=235, width= 450, height= 30)
                speise_id6_entry = tk.Entry(neue_bestellung_frame, font=('arial', 20))
                speise_id6_entry.place(x= 500 , y=235, width= 100, height= 30)

                speise_id7_label = tk.Label(neue_bestellung_frame, text=self.getraenkekarte_df.loc[107, 'Speise'], font=('arial', 20), bg='#8b5a2b', anchor='w')
                speise_id7_label.place(x= 20 , y=270, width= 450, height= 30)
                speise_id7_entry = tk.Entry(neue_bestellung_frame, font=('arial', 20))
                speise_id7_entry.place(x= 500 , y=270, width= 100, height= 30)

                speise_id8_label = tk.Label(neue_bestellung_frame, text=self.getraenkekarte_df.loc[108, 'Speise'], font=('arial', 20), bg='#8b5a2b', anchor='w')
                speise_id8_label.place(x= 20 , y=305, width= 450, height= 30)
                speise_id8_entry = tk.Entry(neue_bestellung_frame, font=('arial', 20))
                speise_id8_entry.place(x= 500 , y=305, width= 100, height= 30)

                speise_id9_label = tk.Label(neue_bestellung_frame, text=self.getraenkekarte_df.loc[109, 'Speise'], font=('arial', 20), bg='#8b5a2b', anchor='w')
                speise_id9_label.place(x= 20 , y=340, width= 450, height= 30)
                speise_id9_entry = tk.Entry(neue_bestellung_frame, font=('arial', 20))
                speise_id9_entry.place(x= 500 , y=340, width= 100, height= 30)

                speise_id10_label = tk.Label(neue_bestellung_frame, text=self.getraenkekarte_df.loc[110, 'Speise'], font=('arial', 20), bg='#8b5a2b', anchor='w')
                speise_id10_label.place(x= 20 , y=375, width= 450, height= 30)
                speise_id10_entry = tk.Entry(neue_bestellung_frame, font=('arial', 20))
                speise_id10_entry.place(x= 500 , y=375, width= 100, height= 30)

                # Festhalten der Speise-Entrys zur weiteren Verwendung in nächster Funktion -bestellung_aufgeben-
                getraenke_labels = [speise_id1_entry, speise_id2_entry, speise_id3_entry, speise_id4_entry, speise_id5_entry, speise_id6_entry, speise_id7_entry, speise_id8_entry, speise_id9_entry, speise_id10_entry]

            # Erstellen eines neuen Frames für die neue Bestellung
            neue_bestellung_frame = tk.LabelFrame(self.bestellung_frame, bg='#8b5a2b')
            neue_bestellung_frame.place(x=20, y=100, width=940, height=445)

            # Erstellung Tischbuttons zur Auswahl des Tisches für Essen-Bestellung
            # tisch_buttons [] <-- Hier werden in der Schleife die Tische eingetragen um sie im nächsten Frame mit .destroy zu löschen 
            tisch_buttons = []

            # Erstellen der Tisch-Buttons (für 10 Tische)
            for tischnummer in range(0, 10):
                # Jeder Button ist einem Tisch zugeordnet und ruft set_tisch_nummer(i+1) auf
                # Übergibt die Tischnummer an set_tisch_nummer
                tisch = tk.Button(neue_bestellung_frame, text=f'Tisch {tischnummer+1}', font=('arial', 20), bg='#cd853f', command=lambda i=tischnummer: set_tisch_nummer(i+1))
                tisch.place(x=20, y=20 + tischnummer*40, width=120, height=30)
                # Fügt den Button der Liste hinzu
                tisch_buttons.append(tisch)          
        
        # Funktion für oberen Button -Aktive Bestellung-
        def aktive_bestellungen() -> None:
            """
            Zeigt die aktiven (offenen) Bestellungen in einem Treeview-Widget an. 
            Die Daten werden aus dem DataFrame self.bestellungen_df gelesen, 
            und es werden nur Bestellungen mit dem Status 'offen' und einer Speise_ID > 99 angezeigt.
            """
            
            # Definieren der Spalten: Bestell_ID und alle weiteren Spalten der offenen Bestellungen
            columns = ['Bestell_ID'] + list(self.bestellungen_df[
                (self.bestellungen_df['Status'] == 'offen') &  # Filtern nach Bestellungen mit Status 'offen'
                (self.bestellungen_df['Speise_ID'] > 99)  # Nur Bestellungen mit Speise_ID > 99
            ].columns)

            # Treeview-Widget erstellen und Spalten festlegen
            tree = ttk.Treeview(self.bestellung_frame, columns=columns, show='headings')

            # Spaltenüberschriften festlegen und zentrieren
            for col in columns:
                tree.heading(col, text=col)  # Überschrift der Spalte setzen
                tree.column(col, width=150, anchor='center')  # Spaltenbreite und Ausrichtung zentrieren

            # Daten in die Tabelle einfügen
            for index, row in self.bestellungen_df.iterrows():
                # Prüfen, ob die Bestellung offen ist und die Speise_ID > 99 ist
                if row['Status'] == 'offen' and row['Speise_ID'] > 99:
                    # Datum formatieren
                    datum_formatiert = pd.to_datetime(row['Datum']).strftime('%d.%m.%Y %H:%M')
                    # Zeile in das Treeview-Widget einfügen
                    tree.insert('', 'end', values=[index] + [datum_formatiert] + row.drop('Datum').tolist())

            # Tabelle in das Tkinter-Fenster einfügen (positionieren)
            tree.place(x=20, y=100, width=940, height=445)

            # Spaltenbreite anpassen, wenn Daten vorhanden sind
            if tree.get_children():
                for col in columns:
                    # Maximale Breite jeder Spalte ermitteln
                    max_width = max(len(str(tree.set(item, col))) for item in tree.get_children())
                    # Spaltenbreite dynamisch anpassen
                    tree.column(col, width=max_width * 10)

            # Sicherstellen, dass das Treeview-Widget alle Aufgaben abgeschlossen hat
            tree.update_idletasks()  
        
        # Erstellung der Funktion für oberen Navigations-Button -Storno/Liefer-
        def storno_liefer() -> None:
            """
            Erstellt ein Interface für die Stornierung von Bestellungen über die Eingabe der Tischnummer.
            Ein Suchfeld für die Tischnummer wird bereitgestellt, um die entsprechende Bestellung zu suchen und zu stornieren.
            """

            # Funktion zur Verarbeitung der Tischnummer mit Weiterverwendung
            def eingabe_tischnummer() -> None:
                """
                Verarbeitet die Eingabe der Tischnummer und zeigt offene Bestellungen für den angegebenen Tisch an.
                Ermöglicht die Bearbeitung und den Abschluss von Bestellungen über ein Tkinter-Interface.
                """
                
                # Funktion für Button -Menge ändern-
                def menge_aendern() -> None:
                    """
                    Ändert die Menge einer bestehenden Bestellung anhand der eingegebenen Bestell_ID.
                    Überprüft die Eingaben auf Fehler und aktualisiert die Bestellmenge, falls gültig.
                    """
                    try:
                        # Holt die Bestell_ID aus dem Eingabefeld
                        bestell_id = ID_label_entry.get()
                    except:
                        # Zeigt eine Info-Nachricht, wenn die Bestell_ID nicht gefunden wurde
                        messagebox.showinfo('Achtung', f'Bestell_ID: {bestell_id} nicht gefunden...')

                    # Überprüft, ob die Bestell_ID ungültig ist (kleiner als 1 oder None)
                    if bestell_id < '1' or bestell_id is None:
                        messagebox.showinfo('Achtung', f'Bestell_ID: {bestell_id} nicht gefunden...')
                    else:
                        try:
                            # Konvertiert die Bestell_ID in eine Ganzzahl
                            bestell_id = int(bestell_id)
                        except:
                            # Zeigt eine Fehlermeldung bei ungültiger Bestell_ID-Eingabe
                            messagebox.showerror('Achtung', 'Fehlerhafte Eingabe -> Bestell_ID')

                        # Holt die neue Menge aus dem Eingabefeld
                        menge = neue_menge_entry.get()
                        try:
                            # Konvertiert die Menge in eine Ganzzahl
                            menge = int(menge)
                        except:
                            # Zeigt eine Fehlermeldung bei ungültiger Mengen-Eingabe
                            messagebox.showerror('Achtung', 'Fehlerhafte Eingabe -> Menge')

                        # Überprüft, ob die Menge kleiner oder gleich 0 ist
                        if menge <= 0:
                            # Zeigt eine Fehlermeldung, wenn die Menge ungültig ist
                            messagebox.showerror('Achtung', 'Menge darf nicht 0 sein...\nZum Stornieren Storno wählen!')
                        else:
                            # Aktualisiert die Menge in der DataFrame für die angegebene Bestell_ID
                            self.bestellungen_df.loc[bestell_id, 'Menge'] = menge
                            # Zeigt eine Bestätigungsmeldung bei erfolgreicher Änderung
                            messagebox.showinfo('Hinweis', 'Menge erfolgreich geändert')
                            # Speichert die geänderten Bestelldaten in einer CSV-Datei
                            self.bestellungen_df.to_csv('./data/Bestelldaten_offen.csv')
                    
                # Funktion für Button -liefer-  
                def liefer() -> None:
                    """
                    Liefert eine Bestellung basierend auf der im Eingabefeld angegebenen Bestell_ID aus.
                    Die Funktion prüft die Bestell_ID, aktualisiert den Status der Bestellung auf 'geliefert' und
                    speichert die aktualisierten Bestellungen in einer CSV-Datei. Zudem wird der entsprechende
                    Eintrag im Treeview entfernt, wenn die Bestellung erfolgreich geliefert wurde.

                    Die Funktion:
                    - Liest die Bestell_ID aus dem Eingabefeld.
                    - Überprüft die Gültigkeit der Bestell_ID und zeigt Fehlermeldungen bei ungültigen IDs an.
                    - Ändert den Status der Bestellung auf 'geliefert' und speichert die Daten in einer CSV-Datei.
                    - Entfernt den Eintrag aus dem Treeview, wenn die Bestell_ID übereinstimmt.
                    """
                    
                    try:
                        # Liest die Bestell_ID aus dem Eingabefeld
                        bestell_id = ID_label_entry.get()
                    except Exception:
                        # Zeigt eine Fehlermeldung an, wenn die Bestell_ID nicht gefunden wird
                        messagebox.showinfo('Achtung', f'Bestell_ID: {bestell_id} nicht gefunden...')
                    
                    if bestell_id < '1' or bestell_id is None:
                        # Zeigt eine Fehlermeldung an, wenn die Bestell_ID ungültig ist
                        messagebox.showinfo('Achtung', f'Bestell_ID: {bestell_id} nicht gefunden...')
                    else:
                        try:
                            # Versucht, die Bestell_ID in eine ganze Zahl umzuwandeln
                            bestell_id = int(bestell_id)
                        except ValueError:
                            # Zeigt eine Fehlermeldung bei fehlerhafter Eingabe an
                            messagebox.showerror('Achtung', 'Fehlerhafte Eingabe -> Bestell_Id')
                        else:
                            # Setzt den Status der Bestellung auf 'geliefert'
                            self.bestellungen_df.loc[bestell_id, 'Status'] = 'geliefert'
                            
                            # Überprüft, ob die Menge der Bestellung 0 ist, und ändert den Status entsprechend
                            if self.bestellungen_df.loc[bestell_id, 'Menge'] == 0:
                                self.bestellungen_df.loc[bestell_id, 'Status'] = 'geliefert'
                            
                            # Zeigt eine Bestätigungsnachricht an
                            messagebox.showinfo('Hinweis', f'Bestell_ID: {bestell_id} geliefert')
                            
                            # Speichert die aktualisierten Bestellungen in einer CSV-Datei
                            self.bestellungen_df.to_csv('./data/Bestelldaten_offen.csv')
                            
                            # Entfernt den Eintrag aus dem Treeview, wenn die Bestell_ID übereinstimmt
                            for item_id in tree.get_children():
                                # Hole die Werte des aktuellen Eintrags
                                values = tree.item(item_id, 'values')
                                # Prüfe, ob der erste Wert (Bestell_ID) mit der angegebenen ID übereinstimmt
                                if str(values[0]).startswith(str(bestell_id)):
                                    # Lösche den Eintrag, wenn die Bedingung erfüllt ist
                                    tree.delete(item_id)
                
                # Funktion für Button -Liefer alles-
                def liefer_alles() -> None:
                    """
                    Markiert alle offenen Getränkebestellungen für eine angegebene Tischnummer als 'geliefert'.
                    Aktualisiert den Status der Bestellungen und speichert die geänderten Daten.
                    """

                    # Tischnummer aus dem Eingabefeld holen
                    tischnummer = tischnummer_entry.get()
                    tischnummer = int(tischnummer)

                    # DataFrame nach offenen Bestellungen und der eingegebenen Tischnummer filtern
                    gefiltert_df = self.bestellungen_df[self.bestellungen_df['Status'] == 'offen'][self.bestellungen_df['Tischnummer'] == tischnummer][self.bestellungen_df['Speise_ID'] > 99]

                    # Überprüfen, ob gefilterte Daten vorhanden sind
                    if gefiltert_df.empty:
                        # Zeigt eine Info-Nachricht, wenn keine offenen Bestellungen gefunden werden
                        messagebox.showinfo('Achtung', f'Keine offenen Getränke-Bestellungen für Tischnummer: {tischnummer}')
                    else:
                        # Ändert den Status der gefilterten Bestellungen auf 'geliefert'
                        self.bestellungen_df.loc[gefiltert_df.index, 'Status'] = 'geliefert'

                        # Zeigt eine Bestätigungsmeldung nach erfolgreicher Lieferung aller Bestellungen
                        messagebox.showinfo('Hinweis', f'Alle Getränke für Tischnummer: {tischnummer} geliefert.')

                        # Speichert die aktualisierten Bestelldaten in einer CSV-Datei
                        self.bestellungen_df.to_csv('./data/Bestelldaten_offen.csv')

                        # Aktualisiert die Ansicht der aktiven Bestellungen
                        aktive_bestellungen()

                # Funktion für Button -Storno-
                def storno() -> None:
                    """
                    Storniert eine Bestellung anhand der angegebenen Bestell_ID. 
                    Ändert den Status der Bestellung auf 'storniert', verschiebt die Bestellung in die geschlossenen Bestellungen
                    und aktualisiert die entsprechenden CSV-Dateien.
                    """
                    # Bestell_ID aus dem Eingabefeld holen
                    bestell_id = ID_label_entry.get()
                    
                    try:
                        # Versucht, die Bestell_ID in eine ganze Zahl zu konvertieren
                        bestell_id = int(bestell_id)
                    except ValueError:
                        # Zeigt eine Fehlermeldung, wenn die Eingabe keine gültige Zahl ist
                        messagebox.showerror('Achtung', 'Falsche Eingabe -> Bestell_ID')
                    else:
                        # Überprüft, ob die Bestell_ID im DataFrame vorhanden ist
                        if bestell_id in self.bestellungen_df.index:
                            # Bestätigungsdialog für das Löschen anzeigen
                            loeschen = messagebox.askquestion('Achtung', f'Bestell_ID: {bestell_id}\nengültig löschen?')
                            
                            if loeschen == 'yes':
                                # Ändert den Status der Bestellung auf 'storniert'
                                self.bestellungen_df.loc[bestell_id, 'Status'] = 'storniert'
                                
                                # Verschiebt die stornierte Bestellung in den DataFrame der geschlossenen Bestellungen
                                self.bestellungen_geschlossen_df = pd.concat([self.bestellungen_geschlossen_df, self.bestellungen_df.loc[[bestell_id]]])
                                
                                # Löscht die stornierte Bestellung aus dem offenen Bestellungen DataFrame
                                self.bestellungen_df.drop(bestell_id, inplace=True)
                                
                                # Speichert die aktualisierten DataFrames in CSV-Dateien
                                self.bestellungen_df.to_csv('./data/Bestelldaten_offen.csv')
                                self.bestellungen_geschlossen_df.to_csv('./data/Bestelldaten_geschlossen.csv')
                                
                                # Zeigt eine Bestätigungsnachricht an
                                messagebox.showinfo('Hinweis', 'Bestellung erfolgreich storniert!')
                                
                                # Filtert die offenen Bestellungen nach Tischnummer und Speise_ID > 99 ( Getränke )
                                gefiltert_df = self.bestellungen_df[self.bestellungen_df['Status'] == 'offen'][self.bestellungen_df['Tischnummer'] == eingabe_tischnummer][self.bestellungen_df['Speise_ID'] > 99]
                                
                                # Definiert die Spalten des Treeviews
                                columns = ['Bestell_ID'] + list(gefiltert_df.columns)
                                tree = ttk.Treeview(storno_liefer_frame, columns=columns, show='headings')
                                
                                if gefiltert_df.empty:
                                    # Zeigt eine Info-Nachricht, wenn keine offenen Bestellungen gefunden werden
                                    messagebox.showinfo('Achtung', f'Keine offenen Bestellungen für Tischnummer: {eingabe_tischnummer}')
                                    tree.place(x=20, y=225, width=900, height=200)
                                else:
                                    # Spaltenüberschriften festlegen und zentrieren
                                    for col in columns:
                                        tree.heading(col, text=col)
                                        tree.column(col, width=150, anchor='center')
                                    
                                    # Daten in die Tabelle einfügen
                                    for index, row in gefiltert_df.iterrows():
                                        # Datum formatieren
                                        datum_formatiert = pd.to_datetime(row['Datum']).strftime('%d.%m.%Y %H:%M')
                                        # Zeile mit formatiertem Datum und Index (Bestell_ID) einfügen
                                        tree.insert('', 'end', values=[index] + [datum_formatiert] + row.drop('Datum').tolist())
                                    
                                    # Tabelle in Tkinter-Fenster einfügen
                                    tree.place(x=20, y=225, width=900, height=200)
                                    
                                    if tree.get_children():
                                        # Spaltenbreite anpassen
                                        for col in columns:
                                            max_width = max(len(str(tree.set(item, col))) for item in tree.get_children())
                                            tree.column(col, width=max_width * 10)
                            else:
                                # Zeigt eine Info-Nachricht, wenn der Storniervorgang abgebrochen wurde
                                messagebox.showinfo('Hinweis', 'Storniervorgang abgebrochen!')
                        else:
                            # Zeigt eine Warnung an, wenn die Bestell_ID nicht gefunden wurde
                            messagebox.showwarning('Achtung', f'Bestell_ID {bestell_id} nicht gefunden')
                
                # Holt die Eingabe der Tischnummer aus dem Eingabefeld
                eingabe_tischnummer = tischnummer_entry.get()

                # Überprüft, ob die Tischnummer eine gültige Zahl ist
                try:
                    eingabe_tischnummer = int(eingabe_tischnummer)
                except:
                    # Zeigt eine Fehlermeldung bei ungültiger Eingabe
                    messagebox.showerror('Achtung', 'Fehlerhafte Eingabe')

                # Überprüft, ob es offene Bestellungen für die eingegebene Tischnummer gibt
                if len(self.bestellungen_df[self.bestellungen_df['Status'] == 'offen'][self.bestellungen_df['Tischnummer'] == eingabe_tischnummer]) < 1:
                    messagebox.showinfo('Achtung', f'Keine offenen Bestellungen für Tischnummer: {eingabe_tischnummer}')
                else:
                    # Filtert das DataFrame nach offenen Bestellungen für die eingegebene Tischnummer und Speise_IDs > 99
                    gefiltert_df = self.bestellungen_df[self.bestellungen_df['Status'] == 'offen'][self.bestellungen_df['Tischnummer'] == eingabe_tischnummer][self.bestellungen_df['Speise_ID'] > 99]
                    
                    # Definiert die Spalten des Treeviews
                    columns = ['Bestell_ID'] + list(gefiltert_df.columns)
                    tree = ttk.Treeview(storno_liefer_frame, columns=columns, show='headings')

                    # Überprüft, ob gefilterte Bestellungen vorhanden sind
                    if len(gefiltert_df) < 1:
                        messagebox.showinfo('Achtung', f'Keine offenen Bestellungen für Tischnummer: {eingabe_tischnummer}')
                    else:
                        # Spaltenüberschriften festlegen und zentrieren
                        for col in columns:
                            tree.heading(col, text=col)
                            tree.column(col, width=150, anchor='center')

                        # Daten in die Tabelle einfügen
                        for index, row in gefiltert_df.iterrows():
                            # Datum formatieren
                            datum_formatiert = pd.to_datetime(row['Datum']).strftime('%d.%m.%Y %H:%M')
                            # Zeile mit formatiertem Datum und Index (Bestell_ID) einfügen
                            tree.insert('', 'end', values=[index] + [datum_formatiert] + row.drop('Datum').tolist())

                        # Tabelle in Tkinter-Fenster einfügen
                        tree.place(x=20, y=225, width=900, height=200)

                        # Spaltenbreite anpassen, falls es Daten gibt
                        if tree.get_children():
                            for col in columns:
                                max_width = max(len(str(tree.set(item, col))) for item in tree.get_children())
                                tree.column(col, width=max_width * 10)

                        # Label und Eingabefeld für die Bestell_ID
                        ID_label = tk.Label(
                            storno_liefer_frame,
                            text='Bestell_ID eingeben:',
                            font=('arial', 20),
                            bg='#8b5a2b',
                            anchor='w'
                        )
                        ID_label.place(x=20, y=90, width=300, height=30)
                        ID_label_entry = tk.Entry(storno_liefer_frame, font=('arial', 20))
                        ID_label_entry.place(x=350, y=90, width=100, height=30)
                        
                        # Label und Eingabefeld für die neue Menge
                        menge_label = tk.Label(storno_liefer_frame, text='Neue Menge:', font=('arial', 20), bg='#8b5a2b', anchor='w')
                        menge_label.place(x=20, y=130, width=300, height=30)
                        neue_menge_entry = tk.Entry(storno_liefer_frame, font=('arial', 20))
                        neue_menge_entry.place(x=350, y=130, width=100, height=30)
                        
                        # Buttons für verschiedene Aktionen ->

                        # Button für Aktion -Menge verändern-
                        menge_button = tk.Button(storno_liefer_frame, text='Menge ändern', bg='#cd853f', font=('arial', 20), command=menge_aendern)
                        menge_button.place(x=740, y=128, width=180, height=35)
                        # Button für Aktion -Positionen einzeln liefern-
                        liefer_button = tk.Button(storno_liefer_frame, text='Liefer', bg='#cd853f', font=('arial', 20), command=liefer)
                        liefer_button.place(x=740, y=88, width=180, height=35)
                        # Button für Aktion -Stornieren-
                        storno_button = tk.Button(storno_liefer_frame, text='Storno', bg='#cd853f', font=('arial', 20), command=storno)
                        storno_button.place(x=740, y=178, width=180, height=35)
                        # Button für Aktion -Alles liefern-
                        liefer_alles_button = tk.Button(storno_liefer_frame, text='Liefer alle\nGetränke', font=('arial', 20), bg='#cd853f', command=liefer_alles)
                        liefer_alles_button.place(x=740, y=20, width=180, height=60)

            if len(self.bestellungen_df[self.bestellungen_df['Status'] == 'offen'][self.bestellungen_df['Speise_ID'] > 99]) < 1:
                messagebox.showinfo('Achtung', 'Keine offenen Bestellungen vorhanden')
            else:
                # Erstellt ein LabelFrame für die Storno-Funktion im Bestellungs-Frame
                storno_liefer_frame = tk.LabelFrame(self.bestellung_frame, bg='#8b5a2b')
                storno_liefer_frame.place(x=20, y=100, width=940, height=445)

                # Label für die Eingabe der Tischnummer
                tischnummer_label = tk.Label(storno_liefer_frame, text='Tischnummer eingeben:', font=('arial', 20), bg='#8b5a2b', anchor='w')
                tischnummer_label.place(x=20, y=20, width=300, height=30)

                # Eingabefeld für die Tischnummer
                tischnummer_entry = tk.Entry(storno_liefer_frame, font=('arial', 20))
                tischnummer_entry.place(x=350, y=20, width=100, height=30)

                # Button zum Suchen der Bestellung anhand der eingegebenen Tischnummer
                tischnummer_button = tk.Button(storno_liefer_frame, text='Suche', font=('arial', 20), bg='#cd853f', command=eingabe_tischnummer, anchor='center')
                tischnummer_button.place(x=500, y=20, width=100, height=30)

                # Filtert die Bestellungen nach Status 'offen' und Speise_ID > 99 ( Getränke )
                gefiltert_df = self.bestellungen_df[
                self.bestellungen_df['Status'] == 'offen'][self.bestellungen_df['Speise_ID'] > 99]

                # Definiert die Spalten des Treeviews
                columns = ['Bestell_ID'] + list(gefiltert_df.columns)
                tree = ttk.Treeview(storno_liefer_frame, columns=columns, show='headings')

                if len(gefiltert_df) < 1:
                    # Zeigt eine Nachricht an, wenn keine offenen Bestellungen vorhanden sind
                    messagebox.showinfo(
                        'Achtung',
                        f'Keine offenen Bestellungen für Tischnummer: {eingabe_tischnummer}'
                    )
                else:
                    # Spaltenüberschriften festlegen und zentrieren
                    for col in columns:
                        tree.heading(col, text=col)
                        tree.column(col, width=150, anchor='center')
                    
                    # Daten in die Tabelle einfügen
                    for index, row in gefiltert_df.iterrows():
                        # Datum formatieren
                        datum_formatiert = pd.to_datetime(row['Datum']).strftime('%d.%m.%Y %H:%M')
                        # Zeile mit formatiertem Datum und Index (Bestell_ID) einfügen
                        tree.insert('', 'end', values=[index] + [datum_formatiert] + row.drop('Datum').tolist())
                    
                    # Tabelle in Tkinter-Fenster einfügen
                    tree.place(x=20, y=225, width=900, height=200)

                    if tree.get_children():
                        for col in columns:
                            # Berechnet die maximale Breite für jede Spalte
                            max_width = max(len(str(tree.set(item, col))) for item in tree.get_children())
                            tree.column(col, width=max_width * 10)
        
        # Erstellung eines neuen Frames für Getränke-Bestellungen
        self.bestellung_frame = tk.LabelFrame(self.startframe, bg='#8b4513')
        self.bestellung_frame.place(x=0, y=0, width=980, height=565)

        # Erstellung des Buttons für neue Bestellungen
        neue_bestellung_button = tk.Button(self.bestellung_frame, text='Neue Bestellung', bg='#cd853f', font=('arial', 20), command=neue_bestellung)
        neue_bestellung_button.place(width=300, height=60, x=20, y=20)

        # Erstellung des Buttons für Storno und Lieferung
        bestellung_stornoliefer_button = tk.Button(self.bestellung_frame, text='Storno / Liefern', font=('arial', 20), bg='#cd853f', command=storno_liefer)
        bestellung_stornoliefer_button.place(width=300, height=60, x=340, y=20)

        # Erstellung des Buttons für aktive Bestellungen
        aktive_bestellungen_button = tk.Button(self.bestellung_frame, text='Aktive Bestellungen', font=('arial', 20), bg='#cd853f', command=aktive_bestellungen)
        aktive_bestellungen_button.place(width=300, height=60, x=660, y=20)

    # Funktion für rechten Hauptbutton -Rechnungen-
    def rechnungen(self) -> None:
        """
        Erstellt das GUI-Layout für das Rechnungs-Management, einschließlich der Buttons für 
        die Erstellung von Rechnungen, das Erstellen von Positionsrechnungen und das Anzeigen aktiver Rechnungen.
        """

        # Funktion für oberen Navigationsbutton -Rechnung erstellen-
        def rechnung_erstellen() -> None:
            """
            Erstellt eine Rechnung für alle gelieferten Bestellungen und zeigt sie in einem Treeview an.
            Die Rechnung wird basierend auf den Daten in den DataFrames 'bestellungen_df', 'speisekarte_df' und 'getraenkekarte_df' erstellt.
            """

            # Funktion zur Weiterverarbeitung nach Tischwahl -> Erstellung Rechnung per PDF
            def tischnummer_auswahl() -> None:
                """
                Verarbeitet die Auswahl einer Tischnummer, erstellt eine Rechnung im PDF-Format und aktualisiert die Bestellstatus.
                Diese Methode holt die Tischnummer aus dem Eingabefeld, filtert die relevanten Daten, erstellt eine PDF-Rechnung,
                öffnet die Rechnung im Webbrowser, und aktualisiert die Status der Bestellungen in den DataFrames.
                """

                # Funktion zur Erstellung der PDF - Rechnung
                def pdf_rechnung(data: dict, filename: str ) -> None:
                    """
                    Erstellt eine PDF-Rechnung basierend auf den übergebenen Daten.

                    :param data: Ein Dictionary mit den Rechnungsdaten. Erwartete Struktur:
                                {
                                    'Tischnummer': int,
                                    'Bestell_IDs': List[int],
                                    'Speisen': Dict[str, List[float]]
                                }
                    :param filename: Der Name der zu speichernden PDF-Datei. Standardmäßig './Rechnungen/Rechnung_Golden_Panda_{datetime.now().strftime("%d_%B_%Y_%H-%M-%S")}.pdf'.
                    """
                    # Erstellung PDF - Rechnung

                    # Erstelle ein neues FPDF-Objekt
                    pdf = FPDF()  
                    # Füge eine neue Seite hinzu
                    pdf.add_page()  

                    # Füge das Logo hinzu
                    pdf.image('./tkinter_pics/Logo.png', x=100, y=20, w=120)  

                    # Schriftart und Größe festlegen
                    pdf.set_font('Arial', 'B', 16)
                    # Füge den Titel hinzu
                    pdf.cell(200, 10, txt='Restaurant Golden Panda', ln=True, align='C')  

                    # Leere Zeile für Abstand
                    pdf.ln(10)

                    # Adresse und Datum
                    pdf.set_font('Arial', '', 10)
                    # Adresse hinzufügen
                    pdf.cell(100, 10, txt='Adresse: Zum Goldenen Bambusstab 7 ', ln=True) 
                    # Telefon hinzufügen 
                    pdf.cell(100, 10, txt='Telefon: 01234-567890', ln=True)  
                     # Datum hinzufügen
                    pdf.cell(100, 10, txt=f'{np.datetime64('today')}', ln=True) 

                    # Tischnummer und Bestell-ID
                    pdf.ln(10)
                    # Tischnummer hinzufügen
                    pdf.cell(100, 10, txt=f'Tischnummer: {data['Tischnummer']}', ln=True)  
                    # Bestell-ID hinzufügen
                    pdf.cell(100, 10, txt=f'Bestell-ID: {data['Bestell_IDs']}', ln=True)  

                    # Tabelle hinzufügen
                    pdf.ln(10)
                    pdf.set_font('Arial', 'B', 12)
                    # Spaltenüberschrift für Speise
                    pdf.cell(50, 10, 'Speise', border=1)  
                    # Spaltenüberschrift für Menge
                    pdf.cell(20, 10, 'Menge', border=1, align='C') 
                    # Spaltenüberschrift für Netto 
                    pdf.cell(30, 10, 'Netto (EUR)', border=1, align='C')  
                    # Spaltenüberschrift für MwSt
                    pdf.cell(40, 10, 'MwSt. 19% (EUR)', border=1, align='C')  
                    # Spaltenüberschrift für Brutt
                    pdf.cell(40, 10, 'Brutto (EUR)', border=1, align='C')
                    pdf.ln(10)

                    # Daten einfügen
                    pdf.set_font('Arial', '', 12)
                    total_netto = 0  # Gesamtsumme Netto
                    total_mwst = 0  # Gesamtsumme MwSt
                    total_brutto = 0  # Gesamtsumme Brutto

                    for speise, details in data['Speisen'].items():
                        menge, brutto = details
                        # Berechnung der MwSt
                        mwst = round(brutto / 119 * 19, 2) 
                        # Speise hinzufügen 
                        pdf.cell(50, 10, speise, border=1)  
                        # Menge hinzufügen
                        pdf.cell(20, 10, str(menge), border=1, align='C')  
                        # Netto hinzufügen
                        pdf.cell(30, 10, f'{brutto-mwst:.2f}', border=1, align='C') 
                        # MwSt hinzufügen 
                        pdf.cell(40, 10, f'{mwst:.2f}', border=1, align='C')  
                        # Brutto hinzufügen
                        pdf.cell(40, 10, f'{brutto:.2f}', border=1, align='C')  
                        pdf.ln(10)

                        # Summen aktualisieren
                        total_netto += brutto - mwst
                        total_mwst += mwst
                        total_brutto += brutto

                    # Gesamtsummen
                    pdf.ln(5)
                    pdf.set_font('Arial', 'B', 12)
                    # Zwischensumme Netto
                    pdf.cell(100, 10, 'Zwischensumme Netto:', ln=False)  
                    pdf.cell(40, 10, f'{total_netto:.2f} EUR', ln=True, align='R')

                    # Gesamt MwSt
                    pdf.cell(100, 10, 'Gesamt MwSt. (19%):', ln=False)  
                    pdf.cell(40, 10, f'{total_mwst:.2f} EUR', ln=True, align='R')

                    # Gesamtbetrag Brutto
                    pdf.cell(100, 10, 'Gesamtbetrag Brutto:', ln=False)  
                    pdf.cell(40, 10, f'{total_brutto:.2f} EUR', ln=True, align='R')

                    # Fußzeile
                    pdf.ln(10)
                    # Fußzeile Text
                    pdf.cell(0, 10, 'Vielen Dank für Ihren Besuch im Restaurant Golden Panda!', ln=True, align='C')  
                    # Fußzeile Text
                    pdf.cell(0, 10, 'Wir hoffen, Sie bald wieder begrüßen zu dürfen.', ln=True, align='C')  

                    # Speichere das PDF
                    pdf.output(filename)

                tischnummer = rechnung_entry.get()
                # Versuche, die Tischnummer in eine Ganzzahl umzuwandeln
                try:
                    tischnummer = int(tischnummer)  
                except ValueError:
                    # Zeige Fehlermeldung bei ungültiger Eingabe
                    messagebox.showerror('Fehler', 'Falsche Eingabe -> Tischnummer')  
                else:
                    # Lese die Rechnungsdetails aus der CSV-Datei
                    detail_df = pd.read_csv('./data/Rechnungsdetails.csv')
                    detail_df.set_index('Bestell_ID', inplace=True)
                    filtered_df = detail_df[detail_df['Tischnummer'] == tischnummer]
                    
                    if len(filtered_df) < 1:
                        # Zeige Fehlermeldung, wenn keine offenen Rechnungsposten vorhanden sind
                        messagebox.showerror('Achtung', f'Für Tischnummer: {tischnummer} sind keine offenen Rechnungsposten vorhanden...')
                    else:
                        # Gruppiere die Daten nach Speise und berechne die Menge und den Preis
                        grouped_df = filtered_df.groupby('Speise')[['Menge', 'Preis']].sum()
                        bestell_ids = filtered_df.index.get_level_values('Bestell_ID').tolist()

                        data_rechnung = {
                            'Bestell_IDs': [],
                            'Tischnummer': tischnummer,
                            'Speisen': {}
                        }

                        # Füge die Speisen-Daten in das Dictionary ein
                        for speise, menge, preis in zip(grouped_df.index.get_level_values('Speise'), grouped_df['Menge'], grouped_df['Preis']):
                            data_rechnung['Speisen'][speise] = [menge, preis]
                            
                        # Aktualisiere die Bestell-IDs
                        bestell_ids = filtered_df.index.get_level_values('Bestell_ID').tolist()
                        data_rechnung['Tischnummer'] = tischnummer
                        data_rechnung['Bestell_IDs'] = bestell_ids

                        # Erstelle die PDF-Rechnung und öffne sie im Webbrowser
                        file_name = f'./Rechnungen/Rechnung_Golden_Panda_{datetime.now().strftime("%d_%B_%Y_%H-%M-%S")}.pdf'
                        pdf_rechnung(data_rechnung, file_name)
                        pdf_path = os.path.abspath(file_name)  # Relativer Pfad zur PDF-Datei
                        webbrowser.open_new(pdf_path)
                        
                        # Setze den Status der Bestellungen auf 'geschlossen'
                        for i in bestell_ids:
                            self.bestellungen_df.loc[i, 'Status'] = 'geschlossen'
                        
                        # Exportiere die geschlossenen Bestellungen
                        export_frame = self.bestellungen_df[self.bestellungen_df['Status'] == 'geschlossen']
                        # Überprüfen, ob self.bestellungen_df leer ist
                        if self.bestellungen_geschlossen_df.empty:
                            # Wenn leer, direkt den neuen DataFrame mit set_index zuweisen
                            self.bestellungen_geschlossen_df = export_frame
                        else:
                            # Andernfalls die DataFrames mit pd.concat zusammenführen
                            self.bestellungen_geschlossen_df = pd.concat([self.bestellungen_geschlossen_df, export_frame])
                        
                        # Aktualisiere die DataFrames und exportiere sie als CSV-Dateien
                        self.bestellungen_df = self.bestellungen_df.drop(export_frame.index)
                        self.bestellungen_geschlossen_df.to_csv('./data/Bestelldaten_geschlossen.csv')
                        self.bestellungen_df.to_csv('./data/Bestelldaten_offen.csv')

                    # Filtere die offenen Bestellungen nach Tischnummer und Status 'geliefert'
                    gefiltert_df = self.bestellungen_df[self.bestellungen_df['Status'] == 'geliefert'][self.bestellungen_df['Tischnummer'] == tischnummer]
                    
                    # Definiere die Spalten des Treeviews
                    columns = ['Bestell_ID'] + list(gefiltert_df.columns)
                    tree = ttk.Treeview(aktive_rechnung_frame, columns=columns, show='headings')
                    
                    if len(gefiltert_df) < 1:
                        # Zeige Info, wenn keine offenen Bestellungen vorhanden sind
                        messagebox.showinfo('Achtung', f'Keine offenen Bestellungen für Tischnummer: {tischnummer}')
                        tree.place(x=20, y=225, width=900, height=200)
                    else:
                        # Spaltenüberschriften festlegen und zentrieren
                        for col in columns:
                            tree.heading(col, text=col)
                            tree.column(col, width=150, anchor='center')
                        
                        # Füge die Daten in die Tabelle ein
                        for index, row in gefiltert_df.iterrows():
                            # Datum formatieren
                            datum_formatiert = pd.to_datetime(row['Datum']).strftime('%d.%m.%Y %H:%M')
                            # Zeile mit formatiertem Datum und Index (Bestell_ID) einfügen
                            tree.insert('', 'end', values=[index] + [datum_formatiert] + row.drop('Datum').tolist())
                        
                        # Tabelle in Tkinter-Fenster einfügen
                        tree.place(x=20, y=225, width=900, height=200)
                        
                        if tree.get_children():
                            for col in columns:
                                max_width = max(len(str(tree.set(item, col))) for item in tree.get_children())
                                tree.column(col, width=max_width * 10)             

                gefiltert_df = self.bestellungen_df[self.bestellungen_df['Status'] == 'geliefert'][self.bestellungen_df['Tischnummer'] == tischnummer]

                # Definiert die Spalten des Treeviews
                columns = ['Bestell_ID'] + list(gefiltert_df.columns)
                tree = ttk.Treeview(aktive_rechnung_frame, columns=columns, show='headings')
                if len(gefiltert_df ) < 1:
                    messagebox.showinfo('Achtung', f'Keine offenen Bestellungen für Tischnummer: {tischnummer}')
                    tree.place(x=20, y=225, width=900, height=200)
                else:
                    # Spaltenüberschriften festlegen und zentrieren
                    for col in columns:
                        tree.heading(col, text=col)
                        tree.column(col, width=150, anchor='center')
                    # Daten in die Tabelle einfügen
                    for index, row in gefiltert_df.iterrows():
                        # Datum formatieren
                        datum_formatiert = pd.to_datetime(row['Datum']).strftime('%d.%m.%Y %H:%M')
                        # Zeile mit formatiertem Datum und Index (Bestell_ID) einfügen
                        tree.insert('', 'end', values=[index] + [datum_formatiert] + row.drop('Datum').tolist())
                    # Tabelle in Tkinter-Fenster einfügen
                    tree.place(x=20, y=225, width=900, height=200)
                    if tree.get_children():
                        for col in columns:
                            max_width = max(len(str(tree.set(item, col))) for item in tree.get_children())
                            tree.column(col, width=max_width * 10)

            # Erzeugt ein LabelFrame für die Rechnungsanzeige
            aktive_rechnung_frame = tk.LabelFrame(self.rechnung_frame, bg='#8b5a2b')
            aktive_rechnung_frame.place(x=20, y=100, width=940, height=445)

            # Label für die Tischnummer-Eingabe
            rechnung_label = tk.Label(aktive_rechnung_frame, text='Tischnummer eingeben:', font=('arial', 20), bg='#8b5a2b', anchor='w')
            rechnung_label.place(x=20, y=20, width=300, height=30)

            # Eingabefeld für die Tischnummer
            rechnung_entry = tk.Entry(aktive_rechnung_frame, font=('arial', 20))
            rechnung_entry.place(x=350, y=20, width=100, height=30)

            # Button zur Erstellung der Rechnung
            rechnung_button = tk.Button(aktive_rechnung_frame, text='Rechnung erstellen', font=('arial', 20), bg='#cd853f', anchor='center', command=tischnummer_auswahl)
            rechnung_button.place(x=500, y=18, height=36)

            # DataFrame filtern, um nur gelieferte Bestellungen anzuzeigen
            rechnung_frame = self.bestellungen_df[self.bestellungen_df['Status'] == 'geliefert'].reset_index()

            # Preisdaten der Speisekarte und Getränkekarte zusammenführen
            preise_df = pd.concat([self.speisekarte_df, self.getraenkekarte_df], ignore_index=False)
            rechnung_frame = rechnung_frame.merge(preise_df['Preis'], on='Speise_ID', how='left')

            # Berechnungen durchführen und DataFrame für Rechnungsdetails vorbereiten
            rechnung_frame.set_index('Bestell_ID', inplace=True)
            rechnung_frame['Preis'] = round(rechnung_frame['Menge'] * rechnung_frame['Preis'], 2)
            rechnung_frame.to_csv('./data/Rechnungsdetails.csv')

            # Gruppieren nach Tischnummer und Berechnen der Gesamtsumme
            gefiltert_df = rechnung_frame.groupby('Tischnummer')[['Menge', 'Preis']].sum().round(2)
            gefiltert_df['Preis'] = gefiltert_df['Preis'].apply(lambda x: f"{x} €")

            # Definiert die Spalten des Treeviews
            columns = ['Tischnummer'] + list(gefiltert_df.columns)
            tree = ttk.Treeview(aktive_rechnung_frame, columns=columns, show='headings')

            # Spaltenüberschriften festlegen und zentrieren
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150, anchor='center')

            # Daten in die Tabelle einfügen
            for index, row in gefiltert_df.iterrows():
                tree.insert('', 'end', values=[index] + list(row))

            # Tabelle in Tkinter-Fenster einfügen
            tree.place(x=20, y=225, width=900, height=200)

            # Spaltenbreite anpassen
            if tree.get_children():
                for col in columns:
                    max_width = max(len(str(tree.set(item, col))) for item in tree.get_children())
                    tree.column(col, width=max_width * 10)            

        # Funktion für oberen Navigations-Button -Aktive Rechnungen-
        def aktive_rechnung() -> None:
            """
            Erstellt eine Übersicht der aktiven Rechnungen, die bereits geliefert wurden.
            Diese Funktion zeigt eine Tabelle mit den Tischnummern und den zugehörigen Preisen.
            """
            # Filtert die Bestellungen nach dem Status 'geliefert'
            rechnung_frame = self.bestellungen_df[self.bestellungen_df['Status'] == 'geliefert']

            # Kombiniert die Speisekarte und Getränkekarte und fügt die Preise hinzu
            preise_df = pd.concat([self.speisekarte_df, self.getraenkekarte_df], ignore_index=False)
            rechnung_frame = pd.merge(rechnung_frame, preise_df['Preis'], on='Speise_ID')

            # Berechnet den Gesamtpreis pro Position
            rechnung_frame['Preis'] = round(rechnung_frame['Menge'] * rechnung_frame['Preis'], 2)

            # Erstellt ein LabelFrame für die Anzeige der aktiven Rechnungen
            aktive_rechnung_frame = tk.LabelFrame(self.rechnung_frame, bg='#8b5a2b')
            aktive_rechnung_frame.place(x=20, y=100, width=940, height=445)

            # Gruppiert die Rechnungen nach Tischnummer und summiert Menge und Preis
            gefiltert_df = rechnung_frame.groupby('Tischnummer')[['Menge', 'Preis']].sum().round(2)
            gefiltert_df['Preis'] = gefiltert_df['Preis'].apply(lambda x: f"{x} €")

            # Definiert die Spalten des Treeviews
            columns = ['Tischnummer'] + list(gefiltert_df.columns)
            
            # Treeview mit dem angepassten Style
            
            tree = ttk.Treeview(aktive_rechnung_frame, columns=columns, show='headings', style="Custom.Treeview")

            # Setzt die Spaltenüberschriften und -breiten
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150, anchor='center')

            # Fügt die Daten in die Tabelle ein
            for index, row in gefiltert_df.iterrows():
                tree.insert('', 'end', values=[index] + list(row))

            # Platziert die Tabelle im Tkinter-Fenster
            tree.place(x=20, y=225, width=900, height=200)

            # Passt die Spaltenbreiten an die längsten Werte an
            if tree.get_children():
                for col in columns:
                    max_width = max(len(str(tree.set(item, col))) for item in tree.get_children())
                    tree.column(col, width=max_width * 10)

        # Funktion für oberen Navigations-Butto -POS Rechnung-
        def pos_rechnung() -> None:
            """
            Verarbeitet die POS-Rechnung und zeigt die Details für die offenen Bestellungen an. 
            Erstellt die Rechnungsdetails und zeigt sie in einem Treeview-Widget an.
            """

            # Funktion nach Eingabe Tischnummer
            def tischnummer_auswahl() -> None:
                """
                Verarbeitet die Auswahl der Tischnummer und zeigt die entsprechenden Rechnungsdetails an.
                """

                def get_rechnung() -> None:
                    """
                    Verarbeitet die Rechnungsdaten basierend auf der Eingabe im id_menge_entry und erstellt eine Rechnung.
                    """
                    
                    # Funktion zur Erstellung der PDF - Rechnung
                    def pdf_rechnung(data: dict, filename: str ) -> None:
                        """
                        Erstellt ein PDF-Dokument für eine Rechnung basierend auf den übergebenen Daten.

                        Args:
                            data (dict): Ein Dictionary, das die Rechnungsdaten enthält. 
                                        Sollte mindestens die Schlüssel 'Tischnummer' und 'Speisen' enthalten.
                            filename (str): Der Name der Datei, in der die PDF-Rechnung gespeichert wird.

                        Returns:
                            None
                        """
                        # Erstellung PDF - Rechnung
                        pdf = FPDF()  # Initialisiere das PDF-Dokument
                        pdf.add_page()  # Füge eine neue Seite hinzu

                        pdf.image('./tkinter_pics/Logo.png', x=100, y=20, w=120)  # Füge ein Logo auf der Seite hinzu

                        # Schriftart und Größe festlegen
                        pdf.set_font('Arial', 'B', 16)
                        pdf.cell(200, 10, txt='Restaurant Golden Panda', ln=True, align='C')

                        # Leere Zeile für Abstand
                        pdf.ln(10)
                        
                        # Adresse und Datum
                        pdf.set_font('Arial', '', 10)
                        pdf.cell(100, 10, txt='Adresse: Zum Goldenen Bambusstab 7 ', ln=True)
                        pdf.cell(100, 10, txt='Telefon: 01234-567890', ln=True)
                        pdf.cell(100, 10, txt=f'{np.datetime64('today')}', ln=True)  # Datum hinzufügen
                        
                        # Tischnummer und Bestell-ID
                        pdf.ln(10)
                        pdf.cell(100, 10, txt=f'Tischnummer: {data["Tischnummer"]}', ln=True)  # Tischnummer aus den Daten
                        pdf.cell(100, 10, txt=f'Bestell-ID: {data["Bestell_IDs"]}', ln=True)  # Bestell-ID aus den Daten
                        
                        # Tabelle hinzufügen
                        pdf.ln(10)
                        pdf.set_font('Arial', 'B', 12)
                        pdf.cell(40, 10, 'Speise', border=1)
                        pdf.cell(20, 10, 'Menge', border=1, align='C')
                        pdf.cell(40, 10, 'Netto (EUR)', border=1, align='C')
                        pdf.cell(40, 10, 'MwSt. 19% (EUR)', border=1, align='C')
                        pdf.cell(40, 10, 'Brutto (EUR)', border=1, align='C')
                        pdf.ln(10)

                        # Daten einfügen
                        pdf.set_font('Arial', '', 12)
                        total_netto = 0
                        total_mwst = 0
                        total_brutto = 0

                        for speise, details in data['Speisen'].items():
                            menge, brutto = details
                            mwst = round(brutto / 119 * 19, 2)  # Berechne die Mehrwertsteuer

                            # Füge Zeile zur Tabelle hinzu
                            pdf.cell(40, 10, speise, border=1)
                            pdf.cell(20, 10, str(menge), border=1, align='C')
                            pdf.cell(40, 10, f'{brutto-mwst:.2f}', border=1, align='C')
                            pdf.cell(40, 10, f'{mwst:.2f}', border=1, align='C')
                            pdf.cell(40, 10, f'{brutto:.2f}', border=1, align='C')
                            pdf.ln(10)

                            total_netto += brutto - mwst  # Summe der Netto-Beträge
                            total_mwst += mwst  # Summe der Mehrwertsteuer
                            total_brutto += brutto  # Summe der Bruttobeträge

                        # Gesamtsummen
                        pdf.ln(5)
                        pdf.set_font('Arial', 'B', 12)
                        pdf.cell(100, 10, 'Zwischensumme Netto:', ln=False)
                        pdf.cell(40, 10, f'{total_netto:.2f} EUR', ln=True, align='R')

                        pdf.cell(100, 10, 'Gesamt MwSt. (19%):', ln=False)
                        pdf.cell(40, 10, f'{total_mwst:.2f} EUR', ln=True, align='R')

                        pdf.cell(100, 10, 'Gesamtbetrag Brutto:', ln=False)
                        pdf.cell(40, 10, f'{total_brutto:.2f} EUR', ln=True, align='R')

                        # Fußzeile
                        pdf.ln(10)
                        pdf.cell(0, 10, 'Vielen Dank für Ihren Besuch im Restaurant Golden Panda!', ln=True, align='C')
                        pdf.cell(0, 10, 'Wir hoffen, Sie bald wieder begrüßen zu dürfen.', ln=True, align='C')

                        # Speichere das PDF
                        pdf.output(filename)  # Speichert die PDF-Datei unter dem angegebenen Namen

                    # Hole den Inhalt der Eingabefelder und parse die Bestell_IDs und Mengen
                    inhalt: str = id_menge_entry.get()
                    inhalt = inhalt.split(',')
                    if len(inhalt) % 2 != 0 :
                        messagebox.showwarning('Achtung', 'Bestell_ID, Menge -> Eigabe nicht korrekt')
                    else:
                        bestell_id: list[int] = [int(i) for i in inhalt[0::2]]
                        
                        try:
                            # Hole die Speise_IDs basierend auf den Bestell_IDs
                            speise_id: list[int] = [self.bestellungen_df.loc[int(i)]['Speise_ID'] for i in bestell_id]
                        except:
                            # Zeige eine Fehlermeldung bei fehlerhaften Bestell_IDs
                            messagebox.showinfo('Achtung', 'Falsche Eingabe -> Bestell_ID')
                        else:
                            # Hole die Mengen
                            menge: list[int] = [int(i) for i in inhalt[1::2]]
                            menge_2: list[int] = menge.copy()
                            preise_df: pd.DataFrame = pd.concat([self.speisekarte_df, self.getraenkekarte_df], ignore_index=False)

                            # Erstelle ein Daten-Layout für die Rechnung
                            data: dict = {
                                'Tischnummer': tischnummer,  # Tischnummer für die Rechnung
                                'Speisen': {}  # Initialisiere ein leeres Dictionary für die Speisen
                            }
                            # Füge Speisen und deren Menge zum Daten-Layout hinzu
                            for speise, menge in zip(speise_id, menge):
                                data['Speisen'][speise] = menge  

                            data_rechnung: dict = {
                                'Bestell_IDs': bestell_id,  # Liste der Bestell_IDs
                                'Tischnummer': tischnummer,  # Tischnummer für die Rechnung
                                'Speisen': {}  # Initialisiere ein leeres Dictionary für die Speisen in der Rechnung
                            }
                            # Konvertiere den ID und Menge in eine ganze Zahl
                            for i, v in data['Speisen'].items():
                                index: int = int(i)  
                                menge: int = int(v)  
                                
                                if index < 100:
                                    # Überprüfe, ob die Speise-ID in der Speisekarte vorhanden ist
                                    if index in self.speisekarte_df.index:
                                        speise_name: str = self.speisekarte_df.loc[index, 'Speise']  # Hole den Namen der Speise
                                        # Füge die Speise und deren Preis zur Rechnung hinzu
                                        data_rechnung['Speisen'][speise_name] = [menge, preise_df[preise_df['Speise'] == speise_name]['Preis'].values[0] * menge]
                                
                                if index > 99:
                                    # Überprüfe, ob die Getränk-ID in der Getränkekarte vorhanden ist
                                    if index in self.getraenkekarte_df.index:
                                        speise_name: str = self.getraenkekarte_df.loc[index, 'Speise']  # Hole den Namen des Getränks
                                        # Füge das Getränk und dessen Preis zur Rechnung hinzu
                                        data_rechnung['Speisen'][speise_name] = [menge, preise_df[preise_df['Speise'] == speise_name]['Preis'].values[0] * menge]
                            
                            # Erstelle ein temporäres DataFrame für die Bestellungen
                            temp_frame: pd.DataFrame = pd.DataFrame({
                                'Bestell_ID': bestell_id,
                                'Datum': [self.bestellungen_df.loc[i]['Datum'] for i in bestell_id],
                                'Tischnummer': [self.bestellungen_df.loc[i]['Tischnummer'] for i in bestell_id],
                                'Speise_ID': [self.bestellungen_df.loc[i]['Speise_ID'] for i in bestell_id],
                                'Speise': [self.bestellungen_df.loc[i]['Speise'] for i in bestell_id],
                                'Menge': menge_2,
                                'Status': [self.bestellungen_df.loc[i]['Status'] for i in bestell_id]
                            })
                            temp_frame.set_index('Bestell_ID', inplace=True)
                            break_var: int = 0
                            
                            # Überprüfe und aktualisiere die Mengen
                            for i in temp_frame.index:
                                neue_menge: int = self.bestellungen_df.loc[i, 'Menge'] - temp_frame.loc[i, 'Menge']
                                if neue_menge < 0:
                                    messagebox.showerror('Achtung', 'Fehlerhafte Mengenangabe...\nMengen dürfen 0 nicht unterschreiten!')
                                    break_var = 1

                            if break_var == 0:
                                # Erstelle die Rechnung und öffne sie
                                file_name = f'./Rechnungen/Rechnung_Golden_Panda_{datetime.now().strftime("%d_%B_%Y_%H-%M-%S")}.pdf'
                                pdf_rechnung(data_rechnung, file_name)
                                pdf_path = os.path.abspath(file_name)  # Relativer Pfad zur PDF-Datei
                                webbrowser.open_new(pdf_path)
                                
                                for i in temp_frame.index:
                                    neue_menge: int = self.bestellungen_df.loc[i, 'Menge'] - temp_frame.loc[i, 'Menge']
                                    if neue_menge < 0:
                                        messagebox.showerror('Achtung', 'Fehlerhafte Mengenangabe...\nMengen dürfen 0 nicht unterschreiten!')
                                    else:
                                        # Aktualisiere die Menge in self.bestellungen_df
                                        self.bestellungen_df.loc[i, 'Menge'] = neue_menge
                                        
                                        if neue_menge == 0:
                                            # Lösche die Bestellung und aktualisiere den Status
                                            self.bestellungen_df.drop(i, inplace=True)
                                            temp_frame.loc[i, 'Status'] = 'geschlossen'
                                            
                                            if i in self.bestellungen_geschlossen_df.index:
                                                # Aktualisiere die Menge in bestellungen_geschlossen_df
                                                self.bestellungen_geschlossen_df.loc[i, 'Menge'] += temp_frame.loc[i, 'Menge']
                                                self.bestellungen_df.to_csv('./data/Bestelldaten_offen.csv')
                                                self.bestellungen_geschlossen_df.to_csv('./data/Bestelldaten_geschlossen.csv')
                                            else:
                                                # Füge neue Bestellung zum DataFrame hinzu
                                                self.bestellungen_geschlossen_df = pd.concat([self.bestellungen_geschlossen_df, temp_frame.loc[[i]]])
                                                self.bestellungen_df.to_csv('./data/Bestelldaten_offen.csv')
                                                self.bestellungen_geschlossen_df.to_csv('./data/Bestelldaten_geschlossen.csv')
                                        
                                        else:
                                            # Setze den Status auf 'geschlossen' und aktualisiere bestellungen_geschlossen_df
                                            temp_frame.loc[i, 'Status'] = 'geschlossen'
                                            if i in self.bestellungen_geschlossen_df.index:
                                                self.bestellungen_geschlossen_df.loc[i, 'Menge'] += temp_frame.loc[i, 'Menge']
                                                self.bestellungen_df.to_csv('./data/Bestelldaten_offen.csv')
                                                self.bestellungen_geschlossen_df.to_csv('./data/Bestelldaten_geschlossen.csv')
                                            else:
                                                self.bestellungen_geschlossen_df = pd.concat([self.bestellungen_geschlossen_df, temp_frame.loc[[i]]])
                                                self.bestellungen_df.to_csv('./data/Bestelldaten_offen.csv')
                                                self.bestellungen_geschlossen_df.to_csv('./data/Bestelldaten_geschlossen.csv')
                            
                            # Aktualisiere die Treeview-Anzeige für die offenen Bestellungen
                            gefiltert_df: pd.DataFrame = self.bestellungen_df[self.bestellungen_df['Status'] == 'geliefert'][self.bestellungen_df['Tischnummer'] == tischnummer]
                            columns: list[str] = ['Bestell_ID'] + list(gefiltert_df.columns)
                            tree = ttk.Treeview(aktive_rechnung_frame, columns=columns, show='headings')
                            
                            if len(gefiltert_df) < 1:
                                messagebox.showinfo('Achtung', f'Keine offenen Bestellungen für Tischnummer: {tischnummer}')
                                tree.place(x=20, y=225, width=900, height=200)
                            else:
                                # Setze die Spaltenüberschriften und deren Ausrichtung
                                for col in columns:
                                    tree.heading(col, text=col)
                                    tree.column(col, width=150, anchor='center')
                                
                                # Füge die Daten in die Tabelle ein
                                for index, row in gefiltert_df.iterrows():
                                    datum_formatiert: str = pd.to_datetime(row['Datum']).strftime('%d.%m.%Y %H:%M')
                                    tree.insert('', 'end', values=[index] + [datum_formatiert] + row.drop('Datum').tolist())
                                
                                # Platziere den Treeview im Frame und passe die Spaltenbreiten an
                                tree.place(x=20, y=225, width=900, height=200)
                                if tree.get_children():
                                    for col in columns:
                                        max_width: int = max(len(str(tree.set(item, col))) for item in tree.get_children())
                                        tree.column(col, width=max_width * 10)

                # Füge die Label und Eingabefelder für Bestell_ID und Menge hinzu
                id_menge_label = tk.Label(aktive_rechnung_frame, text='Bestell_ID, Menge:', font=('arial', 20), bg='#8b5a2b', anchor='w')
                id_menge_label.place(x=20, y=90, width=300, height=30)
                id_menge_entry = tk.Entry(aktive_rechnung_frame, font=('arial', 14))
                id_menge_entry.place(x=350, y=90, width=100, height=30)
                
                # Füge den Button zur Erstellung der Rechnung hinzu
                rechnung_button = tk.Button(aktive_rechnung_frame, text='Rechnung erstellen', font=('arial', 20), bg='#cd853f', anchor='center', command=get_rechnung)
                rechnung_button.place(x=500, y=88, width=300, height=36)
                
                # Lese die Tischnummer aus dem Eingabefeld
                tischnummer = tischnummer_entry.get()
                try:
                    tischnummer = int(tischnummer)
                except ValueError:
                    # Zeige eine Fehlermeldung, wenn die Tischnummer ungültig ist
                    messagebox.showerror('Fehler', 'Falsche Eingabe -> Tischnummer')
                else:
                    # Lese die Rechnungsdetails aus der CSV-Datei
                    detail_df = pd.read_csv('./data/Rechnungsdetails.csv')
                    detail_df.set_index('Bestell_ID', inplace=True)
                    filtered_df = detail_df[detail_df['Tischnummer'] == tischnummer]
                    
                    if len(filtered_df) < 1:
                        # Zeige eine Fehlermeldung, wenn keine offenen Rechnungsposten vorhanden sind
                        messagebox.showerror('Achtung', f'Für Tischnummer: {tischnummer} sind keine offenen Rechnungsposten vorhanden...')
                    else:
                        # Filtere die offenen Bestellungen für die angegebene Tischnummer
                        gefiltert_df = self.bestellungen_df[self.bestellungen_df['Status'] == 'geliefert'][self.bestellungen_df['Tischnummer'] == tischnummer]
                        
                        # Definiere die Spalten des Treeviews
                        columns = ['Bestell_ID'] + list(gefiltert_df.columns)
                        tree = ttk.Treeview(aktive_rechnung_frame, columns=columns, show='headings')
                        
                        if len(gefiltert_df) < 1:
                            # Zeige eine Info-Meldung, wenn keine offenen Bestellungen vorhanden sind
                            messagebox.showinfo('Achtung', f'Keine offenen Bestellungen für Tischnummer: {tischnummer}')
                        else:
                            # Setze die Spaltenüberschriften und deren Ausrichtung
                            for col in columns:
                                tree.heading(col, text=col)
                                tree.column(col, width=150, anchor='center')
                            
                            # Füge die Daten in den Treeview ein
                            for index, row in gefiltert_df.iterrows():
                                # Formatiere das Datum
                                datum_formatiert = pd.to_datetime(row['Datum']).strftime('%d.%m.%Y %H:%M')
                                # Füge eine Zeile mit formatiertem Datum und Index (Bestell_ID) ein
                                tree.insert('', 'end', values=[index] + [datum_formatiert] + row.drop('Datum').tolist())
                            
                            # Platziere den Treeview im Frame
                            tree.place(x=20, y=225, width=900, height=200)
                            
                            # Passe die Spaltenbreiten an die größte Eintragsbreite an
                            if tree.get_children():
                                for col in columns:
                                    max_width = max(len(str(tree.set(item, col))) for item in tree.get_children())
                                    tree.column(col, width=max_width * 10)

            # Erstelle das Frame für die aktive Rechnung
            aktive_rechnung_frame = tk.LabelFrame(self.rechnung_frame, bg='#8b5a2b')
            aktive_rechnung_frame.place(x=20, y=100, width=940, height=445)
            
            # Füge das Label für die Tischnummer-Eingabe hinzu
            tischnummer_label = tk.Label(aktive_rechnung_frame, text='Tischnummer eingeben:', font=('arial', 20), bg='#8b5a2b', anchor='w')
            tischnummer_label.place(x=20, y=20, width=300, height=30)
            
            # Füge das Eingabefeld für die Tischnummer hinzu
            tischnummer_entry = tk.Entry(aktive_rechnung_frame, font=('arial', 14))
            tischnummer_entry.place(x=350, y=20, width=100, height=30)
            
            # Füge den Button für die Tischnummer-Auswahl hinzu
            rechnung_button = tk.Button(aktive_rechnung_frame, text='Tischnummer auswahl', bg='#cd853f', font=('arial', 20), anchor='center', command=tischnummer_auswahl)
            rechnung_button.place(x=500, y=18, width=300, height=36)
            
            # Bereite die Rechnungsdaten vor
            rechnung_frame = self.bestellungen_df[self.bestellungen_df['Status'] == 'geliefert'].reset_index()
            preise_df = pd.concat([self.speisekarte_df, self.getraenkekarte_df], ignore_index=False)
            rechnung_frame = rechnung_frame.merge(preise_df['Preis'], on='Speise_ID', how='left')
            rechnung_frame.set_index('Bestell_ID', inplace=True)
            rechnung_frame['Preis'] = round(rechnung_frame['Menge'] * rechnung_frame['Preis'], 2)
            rechnung_frame.to_csv('./data/Rechnungsdetails.csv')

            # Filtere die Daten für die Anzeige im Treeview
            gefiltert_df = rechnung_frame.groupby('Tischnummer')[['Menge', 'Preis']].sum().round(2)
            gefiltert_df['Preis'] = gefiltert_df['Preis'].apply(lambda x: f"{x} €")
            columns = ['Tischnummer'] + list(gefiltert_df.columns)
            
            # Erstelle und konfiguriere den Treeview für die Anzeige der Rechnungsdaten
            tree = ttk.Treeview(aktive_rechnung_frame, columns=columns, show='headings')
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150, anchor='center')
            
            # Füge die Daten in den Treeview ein
            for index, row in gefiltert_df.iterrows():
                tree.insert('', 'end', values=[index] + list(row))
            
            # Platziere den Treeview im Frame
            tree.place(x=20, y=225, width=900, height=200)
            
            # Passe die Spaltenbreiten an die größte Eintragsbreite an
            if tree.get_children():
                for col in columns:
                    max_width = max(len(str(tree.set(item, col))) for item in tree.get_children())
                    tree.column(col, width=max_width * 10)


        # Erzeugt ein LabelFrame für die Rechnungsverwaltung
        self.rechnung_frame = tk.LabelFrame(self.startframe, bg='#8b4513')
        self.rechnung_frame.place(x=0, y=0, width=980, height=565)

        # Button zum Erstellen einer neuen Rechnung
        neue_bestellung_button = tk.Button(self.rechnung_frame, text='Rechnung erstellen', font=('arial', 20), bg='#cd853f', command=rechnung_erstellen)
        neue_bestellung_button.place(width=300, height=60, x=20, y=20)

        # Button für die Erstellung einer Positionsrechnung
        bestellung_stornoliefer_button = tk.Button(self.rechnung_frame, text='Pos. Rechnung', font=('arial', 20), bg='#cd853f', command=pos_rechnung)
        bestellung_stornoliefer_button.place(width=300, height=60, x=340, y=20)

        # Button zum Anzeigen aktiver Rechnungen
        aktive_bestellungen_button = tk.Button(self.rechnung_frame, text='Aktive Rechnungen', font=('arial', 20), bg='#cd853f', command=aktive_rechnung)
        aktive_bestellungen_button.place(width=300, height=60, x=660, y=20)

    def monatsdaten(self) -> None:
        """
        Analysiert die Bestelldaten des Monats, erstellt Diagramme und einen Finanzbericht als PDF.

        Dieser Bericht umfasst:
        - Einlesen der Bestelldaten und Filtern von Essen, Getränken und Stornos.
        - Erstellen von Diagrammen für Essen, Getränke und Stornos.
        - Erstellen eines PDFs mit einer Zusammenfassung, Tabellen und Diagrammen.

        Returns:
            None
        """
        # Daten einlesen
        try:
            data_df: pd.DataFrame = pd.read_csv('./data/Bestelldaten_geschlossen.csv')  # Lese Bestelldaten ein
            data_df.set_index('Bestell_ID', inplace=True)  # Setze 'Bestell_ID' als Index
        except:
            messagebox.showinfo('Achtung', 'Keine Daten zur Auswertung vorhanden')
        else:

            # Essen und Getränke filtern
            essen_df: pd.DataFrame = data_df[data_df['Speise_ID'] < 100]  # Filtere Essen
            getraenke_df: pd.DataFrame = data_df[data_df['Speise_ID'] > 100]  # Filtere Getränke
            stornos_df: pd.DataFrame = data_df[data_df['Status'] == 'storniert']  # Filtere Stornos

            # Umsatzdaten vorbereiten
            preisliste: pd.DataFrame = pd.concat([pd.read_csv('./data/Speisekarte.csv'), pd.read_csv('./data/Getränkekarte.csv')]).set_index('Speise_ID')  # Preisliste einlesen
            umsatzzählung: pd.DataFrame = (data_df.merge(preisliste[['Preis']], on='Speise_ID')
                                        .assign(Umsatz_in_Euro=lambda x: x['Menge'] * x['Preis'])
                                        .set_index('Speise_ID')
                                        .groupby('Speise')[['Menge', 'Umsatz_in_Euro']].sum().round(2)
                                        .sort_values('Umsatz_in_Euro', ascending=False))  # Berechne Umsatzdaten

            # Diagramme erstellen
            def save_barplot(data: pd.DataFrame, title: str, filename: str) -> None:
                """
                Speichert ein Balkendiagramm der übergebenen Daten.

                Args:
                    data (pd.DataFrame): Die Daten für das Diagramm.
                    title (str): Der Titel des Diagramms.
                    filename (str): Der Name der Datei, in der das Diagramm gespeichert wird.

                Returns:
                    None
                """
                fig, ax = plt.subplots(figsize=(8, 4))
                sns.barplot(data=data, x=data.index, y='Menge', ax=ax)
                plt.title(title)
                plt.xticks(rotation=45, ha='right')
                plt.savefig(filename, transparent=False, facecolor='white', bbox_inches="tight")
                plt.close()

            # Speichere die Diagramme als Bilder
            save_barplot(essen_df.groupby('Speise')['Menge'].sum().sort_values(ascending=False).to_frame(), 'Zählung Essen', './Statistik/essen_zaehlung.png')
            save_barplot(getraenke_df.groupby('Speise')['Menge'].sum().sort_values(ascending=False).to_frame(), 'Zählung Getränke', './Statistik/getraenke_zaehlung.png')
            save_barplot(stornos_df.groupby('Speise')['Menge'].sum().sort_values(ascending=False).to_frame(), 'Zählung Stornos', './Statistik/storno_zaehlung.png')

            # Tabelle als Bild speichern
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.axis('tight')
            ax.axis('off')
            table_data = ax.table(cellText=umsatzzählung.reset_index().values,
                                colLabels=umsatzzählung.reset_index().columns,
                                cellLoc='center', 
                                loc='center')
            plt.savefig('./Statistik/umsatzzählung_dataframe.png', bbox_inches='tight')
            plt.close()

            # Plot erstellen für Menge und Umsatz pro Speise
            fig, ax1 = plt.subplots(figsize=(12, 8))
            sns.barplot(x=umsatzzählung.index, y=umsatzzählung['Menge'], ax=ax1, color='blue', label='Menge')
            ax1.set_xlabel('Speise')
            ax1.set_ylabel('Anzahl Speise', color='blue')
            ax1.tick_params(axis='y', labelcolor='blue')

            # Setzen der Ticks und Labels sicherstellen
            ax1.set_xticks(np.arange(len(umsatzzählung.index)))
            ax1.set_xticklabels(umsatzzählung.index, rotation=45, ha='right')

            ax2 = ax1.twinx()
            ax2.plot(umsatzzählung.index, umsatzzählung['Umsatz_in_Euro'], color='red', marker='o', label='Umsatz')
            ax2.set_ylabel('Umsatz (EUR)', color='red')
            ax2.tick_params(axis='y', labelcolor='red')

            plt.title('Menge und Umsatz pro Speise')
            ax1.legend(loc='upper left')
            ax2.legend(loc='upper right')
            fig.tight_layout()
            plt.savefig('./Statistik/umsatz.png', transparent=False, facecolor='white', bbox_inches="tight")
            plt.close()

            # Dynamisches Datum beziehen
            current_date: str = datetime.now().strftime("%d. %B %Y")  # Erhalte das aktuelle Datum im Format Tag. Monat Jahr

            # Bericht erstellen
            class PDF(FPDF):
                def header(self) -> None:
                    """
                    Fügt den Header der PDF hinzu.

                    Returns:
                        None
                    """
                    self.set_font('Arial', 'B', 16)
                    self.cell(0, 10, f'Finanzbericht - {current_date}', 0, 1, 'C')
                    self.ln(10)
                
                def chapter_title(self, title: str) -> None:
                    """
                    Fügt den Titel eines Kapitels hinzu.

                    Args:
                        title (str): Der Titel des Kapitels.

                    Returns:
                        None
                    """
                    self.set_font('Arial', 'B', 14)
                    self.cell(0, 10, title, 0, 1, 'L')
                    self.ln(5)
                
                def chapter_body(self, body: str) -> None:
                    """
                    Fügt den Textkörper eines Kapitels hinzu.

                    Args:
                        body (str): Der Textkörper des Kapitels.

                    Returns:
                        None
                    """
                    self.set_font('Arial', '', 12)
                    self.multi_cell(0, 10, body)
                    self.ln()
                
                def add_image(self, image_path: str, x: int = 10, y: int = 10, w: int = 200, h: int = 150) -> None:
                    """
                    Fügt ein Bild zur PDF hinzu.

                    Args:
                        image_path (str): Der Pfad zum Bild.
                        x (int): Die X-Position des Bildes.
                        y (int): Die Y-Position des Bildes.
                        w (int): Die Breite des Bildes.
                        h (int): Die Höhe des Bildes.

                    Returns:
                        None
                    """
                    self.image(image_path, x=x, y=y, w=w, h=h)
                
                def add_table(self, data: list, col_labels: list, title: str) -> None:
                    """
                    Fügt eine Tabelle zur PDF hinzu.

                    Args:
                        data (list): Die Daten für die Tabelle.
                        col_labels (list): Die Spaltenbezeichnungen der Tabelle.
                        title (str): Der Titel der Tabelle.

                    Returns:
                        None
                    """
                    self.set_font('Arial', 'B', 12)
                    self.cell(0, 10, title, 0, 1, 'L')
                    self.ln(5)
                    self.set_font('Arial', 'B', 10)
                    for col_label in col_labels:
                        self.cell(60, 10, col_label, 1, 0, 'C')
                    self.ln()
                    self.set_font('Arial', '', 10)
                    for row in data:
                        for cell in row:
                            self.cell(60, 10, str(cell), 1, 0, 'C')
                        self.ln()
                    self.ln()

            pdf: PDF = PDF()  # Erstelle eine neue PDF-Instanz
            pdf.add_page()  # Füge eine Seite zur PDF hinzu

            # Titel und Bericht
            pdf.chapter_title('Zusammenfassung der Bestellungen')

            # Berechnungen für Bericht
            essen_menge: pd.Series = essen_df.groupby('Speise')['Menge'].sum().sort_values(ascending=False)
            getraenke_menge: pd.Series = getraenke_df.groupby('Speise')['Menge'].sum().sort_values(ascending=False)
            stornos_menge: pd.Series = stornos_df.groupby('Speise')['Menge'].sum().sort_values(ascending=False)
            top_essen: pd.DataFrame = essen_menge.head(3).to_frame().reset_index()
            top_getraenke: pd.DataFrame = getraenke_menge.head(3).to_frame().reset_index()
            top_stornos: pd.DataFrame = stornos_menge.head(3).to_frame().reset_index()

            gesamt_umsatz: float = umsatzzählung['Umsatz_in_Euro'].sum()
            gesamt_menge: int = umsatzzählung['Menge'].sum()

            bericht: str = (
                f"Bis zum {current_date} wurden insgesamt {len(data_df)} Bestellungen im Restaurant verarbeitet. "
                "Die Bestellungen umfassen sowohl Essens- als auch Getränkepositionen, die in den folgenden Kategorien zusammengefasst werden:\n\n"
                f"- **Essen**: {len(essen_df)} Bestellungen\n"
                f"- **Getränke**: {len(getraenke_df)} Bestellungen\n"
                f"- **Stornos**: {len(stornos_df)} Bestellungen\n\n"
                "Detailanalyse der Bestellungen:\n"
                "1. **Essen**\n"
                f"Top 3 Speisen nach Menge:\n"
                "2. **Getränke**\n"
                f"Top 3 Getränke nach Menge:\n"
                "3. **Stornos**\n"
                f"Top 3 stornierte Speisen nach Menge:\n\n"
                f"**Gesamtumsatz**: {gesamt_umsatz:.2f} EUR\n"
                f"**Gesamtmenge verkauft**: {gesamt_menge}\n"
                "Umsatzanalyse zeigt die wichtigsten Verkaufspositionen des Monats. Top-3 Essen und Getränke sowie Stornos sind detailliert dargestellt."
            )
            # Füge den Bericht zum PDF hinzu
            pdf.chapter_body(bericht)  

            # Tabellen hinzufügen
            pdf.add_page()
            pdf.add_table(top_essen.values, top_essen.columns, "Top 3 Essen nach Menge")
            pdf.add_table(top_getraenke.values, top_getraenke.columns, "Top 3 Getränke nach Menge")
            pdf.add_table(top_stornos.values, top_stornos.columns, "Top 3 Stornos nach Menge")

            # Seite 3: Diagramme hinzufügen
            pdf.add_page()
            pdf.add_image('./Statistik/essen_zaehlung.png', x=5, y=20, w=150, h=100)
            pdf.ln(80)
            pdf.add_image('./Statistik/getraenke_zaehlung.png', x=5, y=130, w=150, h=100)

            # Seite 4: Diagramme hinzufügen
            pdf.add_page()
            pdf.add_image('./Statistik/umsatzzählung_dataframe.png', x=5, y=-25, w=200, h=150)
            pdf.ln(80)
            pdf.add_image('./Statistik/umsatz.png', x=5, y=130, w=200, h=150)

            # Speichern
            file_name = f'./Statistik/Finanzbericht_{datetime.now().strftime("%d_%B_%Y_%H-%M-%S")}.pdf'
            pdf.output(file_name)  # Speichere die PDF-Datei
            pdf_path: str = os.path.abspath(file_name)  # Relativer Pfad zur PDF-Datei

            # Warte und überprüfe, ob die Datei erstellt wurde
            while not os.path.isfile(pdf_path):
                try:
                    time.sleep(1)  # Warte 1 Sekunde, um die CPU zu entlasten
                except Exception as e:
                    print(f"Fehler: {e}")
                    break
            else:
                webbrowser.open_new(pdf_path)  # Öffne die PDF-Datei im Standardbrowser

# Funktion über Menüband -Programm schließen-
def beenden() -> None:
    """
    Überprüft den Status der Bestellungen im Restaurant und handelt entsprechend:

    - Wenn offene Bestellungen vorhanden sind, wird eine Warnmeldung angezeigt,
      die die offenen Vorgänge auflistet.
    - Wenn keine offenen Bestellungen vorhanden sind, werden die Bestelldaten in
      zwei CSV-Dateien gespeichert: 'Bestelldaten_offen.csv' und 'Bestelldaten_geschlossen.csv'.
    - Zeigt eine Informationsmeldung an, dass die Daten gesichert wurden und schließt das Programm.

    :return: None
    """
    if Restaurant.bestellungen_df['Status'].count() > 0:
        # Warnmeldung anzeigen, wenn offene Bestellungen vorhanden sind
        show_warning_with_dynamic_size(
            f'Es sind nicht geschlossene Vorgänge vorhanden:\n{Restaurant.bestellungen_df.groupby(["Tischnummer", "Bestell_ID"])[["Menge"]].count()}\n\nSchließen nicht möglich mit offenen Vorgängen !'
        )
    else:
        # Bestelldaten in CSV-Dateien speichern
        Restaurant.bestellungen_df.to_csv('./data/Bestelldaten_offen.csv')
        Restaurant.bestellungen_geschlossen_df.to_csv('./data/Bestelldaten_geschlossen.csv')

        # Informationsmeldung anzeigen und Programm beenden
        messagebox.showinfo('Speichern...', 'Datenbanken gesichert\nZum Beenden klicken')
        root.quit()

# Funktion zum Erstellen eines Warnfensters mit dynamischer Größe
def show_warning_with_dynamic_size(text: str) -> None:
    """
    Zeigt ein neues Tkinter-Fenster mit einer Warnmeldung an. Das Fenster enthält
    ein Text-Widget zum Anzeigen der Nachricht und eine Scrollbar für den Textinhalt.
    Ein Schließen-Button ermöglicht das Schließen des Fensters.

    :param text: Die Warnmeldung, die im Text-Widget angezeigt werden soll.
    :type text: str
    :return: Gibt keinen Wert zurück.
    :rtype: None
    """
    # Erstellen Sie ein neues Tkinter-Fenster
    window = tk.Toplevel()
    window.geometry('500x300')
    window.title("Achtung")
    
    # Erstellen Sie einen Frame für das Text-Widget und die Scrollbar
    frame = tk.Frame(window)
    frame.pack(fill=tk.BOTH, expand=True)
    
    # Erstellen Sie das Text-Widget mit Scrollbar
    text_widget = tk.Text(frame, wrap=tk.WORD, height=10, width=50)
    text_widget.insert(tk.END, text)
    text_widget.configure(state=tk.DISABLED)  # Nur zum Lesen
    
    # Scrollbar hinzufügen
    scrollbar = tk.Scrollbar(frame, command=text_widget.yview)
    text_widget.configure(yscrollcommand=scrollbar.set)
    
    # Packen der Widgets
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)    
    
    # Setzen Sie einen Schließ-Button für das Fenster
    close_button = tk.Button(window, text="Schließen", command=window.destroy)
    close_button.pack(pady=10)
    
    # Starten Sie die Tkinter-Ereignisschleife für das neue Fenster
    window.mainloop()

#%% Startfenster

root = tk.Tk()
root.geometry('1200x800')
root.resizable(False, False)

# Hintergrund - Bild setzen
hintergrund = tk.Canvas(root, width=1200, height=800)
hintergrund.pack(fill="both", expand=True)
bild = Image.open('./tkinter_pics/Background.jpeg') 
bild = bild.resize((1200, 800))
background_image = ImageTk.PhotoImage(bild)
hintergrund.create_image(0, 0, image=background_image, anchor='nw')

# Erstellung der Menüleisten
menubar = tk.Menu(root)
root.config(menu=menubar)

# Menü 1
menue1 = tk.Menu(menubar, tearoff=0, font=('arial', 18))
menubar.add_cascade(label='Start', menu=menue1)
menue1.add_command(label='Datenbank laden', command= lambda: Restaurant(hintergrund))
menue1.add_command(label='Programm beenden', command= beenden)
# menue1.add_command(label='Datenbank speichern', command=datenbank_speichern)

root.mainloop()
