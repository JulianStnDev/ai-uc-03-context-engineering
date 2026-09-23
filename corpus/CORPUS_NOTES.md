# Korpus-Notizen (nur für Menschen – NICHT indexieren)

Diese Datei beschreibt den FocusFlow-Korpus und seine absichtlich eingebauten
Fallen. Sie dient als Grundlage zum Schreiben der Testfragen und darf **nicht**
im Retrieval-Index oder im Kontextfenster landen. Loader sollten `CORPUS_NOTES.md`
explizit ausschließen.

Stand: 23.09.2026 · 20 Artikel · je 208–263 Wörter · alle auf Deutsch

## Artikelliste

| Datei | Titel | Stand | Bereich |
|---|---|---|---|
| preise-und-tarife.md | Preise und Tarife | 02.07.2026 | Abo & Abrechnung |
| pro-funktionen-und-preise.md | FocusFlow Pro – Was ist enthalten und was kostet es? | **14.03.2024** | Abo & Abrechnung – **veraltet** |
| tarif-wechseln.md | Zwischen monatlicher und jährlicher Zahlung wechseln | 18.06.2026 | Abo & Abrechnung |
| erstattungen.md | Erstattungsrichtlinie | 05.05.2026 | Abo & Abrechnung |
| abo-kuendigen.md | Abo kündigen | 21.04.2026 | Abo & Abrechnung |
| doppelte-abbuchung.md | Doppelte Abbuchung | 09.09.2026 | Abo & Abrechnung |
| passwort-zuruecksetzen.md | Passwort zurücksetzen | 12.02.2026 | Konto & Sicherheit |
| anmelden-mit-google.md | Mit Google anmelden | 30.01.2026 | Konto & Sicherheit |
| konten-zusammenfuehren.md | Zwei Konten zusammenführen | 11.03.2026 | Konto & Sicherheit |
| konto-loeschen.md | Konto löschen | 27.05.2026 | Konto & Sicherheit |
| verdaechtige-anmeldungen.md | Verdächtige Anmeldungen | 14.08.2026 | Konto & Sicherheit |
| habits-anlegen.md | Habits anlegen und verwalten | 03.03.2026 | Funktionen |
| fokus-timer.md | Der Fokus-Timer | 22.07.2026 | Funktionen |
| streaks.md | So funktionieren Streaks | 16.04.2026 | Funktionen |
| synchronisierung.md | Synchronisierung zwischen Geräten | 08.08.2026 | Funktionen |
| widgets.md | Widgets einrichten | 25.06.2026 | Funktionen |
| benachrichtigungen.md | Benachrichtigungen und Erinnerungen | 19.05.2026 | Funktionen |
| datenschutz-und-speicherort.md | Datenschutz und Speicherort deiner Daten | 10.01.2026 | Sonstiges |
| bekannte-probleme.md | Bekannte Probleme | 15.09.2026 | Sonstiges |
| roadmap-faq.md | Roadmap: Häufige Fragen zu neuen Funktionen | 01.09.2026 | Sonstiges |

## Pflicht-Produktfakten (Ground Truth)

| Fakt | Wert | Quelle(n) |
|---|---|---|
| Free-Limit | max. 3 aktive Habits (archivierte zählen nicht) | preise-und-tarife, habits-anlegen, abo-kuendigen, erstattungen |
| Pro-Preis | 6,99 USD/Monat oder 59 USD/Jahr | preise-und-tarife (+ Rechenbeispiel in tarif-wechseln) |
| Testphase | **keine** | preise-und-tarife |
| Login | E-Mail/Passwort oder Google, sonst nichts | anmelden-mit-google |
| Plattformen | iOS, Android, Web | preise-und-tarife, synchronisierung |
| Dark Mode | nicht vorhanden, geplant ohne Termin | widgets, bekannte-probleme, roadmap-faq |
| Doppelabbuchung | bekanntes Problem bei Tarifwechsel (v. a. Web, monatlich → jährlich) | doppelte-abbuchung, bekannte-probleme, tarif-wechseln |

## Falle 1: Veraltete Preisseite

- **Datei:** `pro-funktionen-und-preise.md`, Stand 14.03.2024, nicht als veraltet markiert
- **Widerspricht** `preise-und-tarife.md` (02.07.2026):

| | veraltet (2024) | aktuell (2026) |
|---|---|---|
| Monatlich | 4,99 USD | **6,99 USD** |
| Jährlich | 39,99 USD („ein Drittel sparen“) | **59 USD** (ca. 30 % sparen) |
| Testphase | 7 Tage kostenlos | **keine Testphase** |

- Free-Limit (3 Habits) und Plattformen sind in beiden Artikeln gleich, sodass die Seite plausibel wirkt.
- Worauf es ankommt: Nimmt das System die aktuellere Quelle (Datum)? Merkt es den Widerspruch? Die Testphase ist besonders heimtückisch, weil nur die veraltete Seite das Wort „Testphase“ prominent in einer Überschrift hat. Die aktuelle Seite erwähnt sie nur in einem Satz.

## Falle 2: Bewusste Lücken

Folgende naheliegende Themen kommen im Korpus **nicht** vor. Die korrekte Antwort ist „dazu gibt es keine Information in der Hilfe“ bzw. ein Verweis an den Support:

- Team-, Firmen- oder Schullizenzen / Mengenrabatte
- App-Sprachen / Lokalisierung (die App-Sprache wird nirgends erwähnt)
- Studenten-, Bildungs- oder sonstige Rabatte, Gutscheincodes, Geschenkabos
- Familienfreigabe (Apple Family Sharing / Google Play Familienmediathek)
- Rechnungen, Umsatzsteuer, Firmenrechnung mit USt-ID
- Zahlungsmethoden im Detail (PayPal, SEPA, …), Preise in Euro/Landeswährung
- Smartwatch-Apps (Apple Watch, Wear OS)
- Datenimport aus anderen Habit-Apps
- Telefon-Support / Support-Erreichbarkeit und Antwortzeiten

Grenzfälle, die abgedeckt sind, obwohl sie wie Lücken wirken:
- Apple-Login: indirekt beantwortet („Andere Anmeldedienste werden derzeit nicht unterstützt“, anmelden-mit-google)
- Desktop-App: „nicht geplant“ (roadmap-faq)
- 2FA: „gibt es nicht, geplant“ (verdaechtige-anmeldungen + roadmap-faq)

## Falle 3: Mehrquellen-Fälle

**3a: Tarifwechsel + Erstattung (Hauptfall)**
- `tarif-wechseln.md`: Monatlich → jährlich gilt sofort, Restmonat wird als Guthaben verrechnet (Beispiel: 54,34 USD). Jährlich → monatlich gilt erst zum Laufzeitende, ohne anteilige Verrechnung. Zur Erstattung steht dort nur ein Verweis auf die „allgemeinen Erstattungsrichtlinien“.
- `erstattungen.md`: Jahresabo 14 Tage voll erstattbar (ab Kauf bzw. Verlängerung), danach nichts. Erstattet wird der tatsächlich gezahlte Betrag, also abzüglich Guthaben. Nach einer Erstattung endet Pro sofort. Monatsabo wird nie erstattet.
- Nur beide zusammen beantworten z. B.: „Ich bin vor X Tagen von monatlich auf jährlich gewechselt, will zurück und mein Geld wiederhaben“ (≤ 14 Tage: tatsächlich gezahlter Betrag zurück, Pro endet sofort, danach neu monatlich abschließen; > 14 Tage: keine Erstattung, Wechsel erst zum Laufzeitende).

**3b: Doppelabbuchung + Erstattung**
- `doppelte-abbuchung.md`: erst 3–5 Werktage warten (Vormerkung), dann über das Formular „Zahlungsproblem melden“. Bei Store-Abos an Apple/Google wenden.
- `erstattungen.md`: Doppelbelastungen werden immer voll erstattet, unabhängig von der 14-Tage-Frist. Bearbeitung 5–10 Werktage.

**3c: Konten zusammenführen + Kündigen/Erstattung**
- `konten-zusammenfuehren.md`: Nur ein Konto darf Pro haben, das andere muss gekündigt werden und auslaufen, ohne automatische Erstattung.
- `abo-kuendigen.md`: Pro läuft bis zum Periodenende weiter.
- `erstattungen.md`: ggf. innerhalb von 14 Tagen erstattbar.

**3d: Google-Login + Synchronisierung/Passwort-Reset**
- „Meine Habits sind weg“ bzw. „Ich bekomme keine Passwort-Mail“ hat oft die Ursache, dass zwei getrennte Konten existieren (E-Mail vs. Google). Die Teile stehen in `anmelden-mit-google`, `synchronisierung`, `passwort-zuruecksetzen` und `konten-zusammenfuehren`.

## Falle 4: Ähnlich klingende Artikel mit unterschiedlicher Aussage

**Hauptpaar: `abo-kuendigen.md` vs. `konto-loeschen.md`**
Beide beginnen fast gleich („Du möchtest FocusFlow [Pro] nicht mehr nutzen …“).

| | Abo kündigen | Konto löschen |
|---|---|---|
| Pro-Zugang | läuft **bis Periodenende** weiter | Web-Abo endet **sofort** |
| Erstattung Restlaufzeit | – (keine weitere Abbuchung) | **keine Erstattung** der Restlaufzeit |
| Store-Abo (Apple/Google) | im Store kündigen | wird **nicht** automatisch beendet, läuft weiter |
| Daten | bleiben vollständig erhalten | endgültig gelöscht (Backups nach 30 Tagen) |
| Rückgängig | jederzeit Pro neu abschließen | nicht möglich |

**Nebenpaare (weniger stark):**
- `abo-kuendigen.md` vs. `erstattungen.md`: Kündigung bedeutet, dass Pro weiterläuft. Eine Erstattung bedeutet, dass Pro sofort endet.
- `preise-und-tarife.md` vs. `pro-funktionen-und-preise.md`: siehe Falle 1.
- `streaks.md` vs. `habits-anlegen.md`: Die 2-Tage-Rückwirkung steht in beiden, der Streak-Schutz (Pro, 2 Tage/Monat, nicht für „X-mal pro Woche“) nur in streaks. Das Risiko ist, dass „2 Tage“ verwechselt wird.

## Weitere prüfbare Detailfakten (Auswahl)

- Passwort-Link 60 Min. gültig, Passwort min. 10 Zeichen
- Konten zusammenführen: bis zu 5 Werktage, nicht umkehrbar
- DSGVO-Anfragen: datenschutz@focusflow.app, Bearbeitung innerhalb eines Monats
- Sicherheit: security@focusflow.app, keine eigene 2FA
- Server: Frankfurt am Main (EU), TLS + AES-256
- Fokus-Timer: 25/5/15, Pro 5–90 Min., Web-Tab muss offen bleiben
- Streak: Tagesgrenze Mitternacht Gerätezeit, Wochen ab Montag, Warnung 20:00
- Widgets: iOS ab 17 (Home + Sperrbildschirm), Android ab 10, Web keine, Timer-Widget nur Pro, immer helles Design
- Bekanntes Problem behoben: doppelter Verlauf in iOS 4.12, behoben in 4.13
