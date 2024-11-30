# pdfdec{1,2,3}.py

### ehemals: stripPsw.py

zeigt die pdf-Dateien des Ordners "my_path", die mit Passwort verschlüsselt sind.
Wenn eine derartige Datei selektiert ist und der Button 'pdf entschlüsseln' gedrückt wird,
wird die pdf in eine neue pdf-Datei OHNE Paswort kopiert.
Wird die Check-Box 'pdf nach Öffnen löschen' aktiviert,
so wird die Passwort geschützte pdf gelöscht.
Die App zeigt anschließend in ihrem Fenster den Inhalt der ersten Seite der pdf an.

Anpassung an Linux:
- Anpassungen in pdfdec3.py
- Pfad zu den Rechnungen
- anschließend (nach decrypt) wird die verschlüsselte Rechnung nach './alt' verschoben
  rg, 2024-08-07

rg, 2024-01-15