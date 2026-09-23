# Judge-Stichprobe zur Kalibrierung

10 zufällig gezogene Urteile von `claude-sonnet-5` (Seed 42, gestreut über Varianten, Typen und Kriterien). Bitte je Urteil die letzte Spalte bzw. das Feld „Julian stimmt zu?“ ausfüllen.

Bei `treu` prüft der Judge, ob jede Behauptung durch den Kontext gedeckt ist, den das Antwortmodell gesehen hat. Die Kontext-Dateien stehen dabei; der volle Kontext steht in `data/answers.jsonl`.

| Nr | Frage | Variante | Typ | Kriterium | Urteil | Julian stimmt zu? ja/nein |
|---|---|---|---|---|---|---|
| 1 | #19 | sections | mehrquellen | kernaussage_ok | ❌ nein |  |
| 2 | #20 | articles | aehnlich | kernaussage_ok | ✅ ja |  |
| 3 | #16 | sections | einfach | kernaussage_ok | ✅ ja |  |
| 4 | #13 | contextual | einfach | treu | ✅ ja |  |
| 5 | #13 | articles | einfach | treu | ✅ ja |  |
| 6 | #23 | sections | aehnlich | treu | ✅ ja |  |
| 7 | #10 | contextual | mehrquellen | treu | ✅ ja |  |
| 8 | #10 | articles | mehrquellen | kernaussage_ok | ❌ nein |  |
| 9 | #7 | corpus | luecke | luecke_ok | ✅ ja |  |
| 10 | #8 | corpus | luecke | treu | ✅ ja |  |

---

## 1. Frage #19 · sections · mehrquellen · Kriterium `kernaussage_ok`

**Frage:** bin vor ner woche von monatlich auf jährlich umgestiegen, war doch ne blöde idee. kann ich zurück und krieg mein geld wieder?

**Antwort (Haiku 4.5):**

> Ich verstehe deine Frustration! Hier die gute Nachricht: Du kannst jederzeit zurück auf monatliche Zahlung wechseln.
>
> **Allerdings:** Der Wechsel von jährlich auf monatlich wird **erst zum Ende deines aktuellen Jahreszeitraums** wirksam. Das bedeutet, du behältst Pro bis dahin wie gewohnt, danach wird monatlich abgerechnet.
>
> Ob du für den bereits bezahlten Zeitraum Geld zurückbekommen kannst, richtet sich nach unseren allgemeinen Erstattungsrichtlinien – das kann ich dir aus den verfügbaren Infos leider nicht konkret sagen.
>
> **Meine Empfehlung:** Kontaktiere unseren Support direkt in der App (Einstellungen > Hilfe > Kontakt). Die können dir eine individuelle Lösung anbieten, besonders wenn du gerade erst umgestiegen bist.
>
> Quellen: tarif-wechseln.md

**Kernaussage (Goldset):** Ja, innerhalb von 14 Tagen wird der tatsächlich gezahlte Betrag erstattet, Pro endet dann sofort (danach neu monatlich abschließen); ein normaler Wechsel zurück auf monatlich greift erst zum Laufzeitende

**Kontext-Dateien:** tarif-wechseln.md; doppelte-abbuchung.md

**Urteil `kernaussage_ok`:** ❌ nein

**Begründung:** Die Antwort erklärt zwar korrekt den normalen Wechsel zurück auf monatlich (erst zum Jahresende), lässt aber die zentrale Aussage der Soll-Antwort – dass innerhalb von 14 Tagen eine Erstattung des gezahlten Betrags mit sofortiger Beendigung möglich ist – komplett aus und verweist stattdessen nur vage auf 'allgemeine Erstattungsrichtlinien' und den Support. Damit fehlt die Hauptaussage.

**Julian stimmt zu? (ja/nein):** 

---

## 2. Frage #20 · articles · aehnlich · Kriterium `kernaussage_ok`

**Frage:** Ich habe mein Abo im App Store gekündigt, aber in der App steht immer noch Pro aktiv bis 2027. Was gilt denn jetzt?

**Antwort (Haiku 4.5):**

> Das ist eine gute Frage, aber die genaue Situation nach einer Kündigung im App Store kann ich dir anhand der verfügbaren Informationen leider nicht vollständig beantworten.
>
> Was ich dir sagen kann: Nach einer Kündigung läuft dein Pro-Zugang normalerweise bis zum Ende des bereits bezahlten Zeitraums weiter – das ist das erwartete Verhalten. Ob es bei App-Store-Kündigungen Besonderheiten gibt, ist in meinen Unterlagen nicht dokumentiert.
>
> Da es um dein Abo geht, würde ich dir empfehlen, den Support zu kontaktieren. Du findest ihn in der App unter **Einstellungen > Hilfe > Kontakt**. Dort können sie dir genau sagen, welcher Status aktuell für dich gilt.
>
> Quellen: abo-kuendigen.md

**Kernaussage (Goldset):** Normal: Pro läuft bis zum Ende des bezahlten Zeitraums weiter, danach Free; keine weitere Abbuchung

**Kontext-Dateien:** abo-kuendigen.md; tarif-wechseln.md; erstattungen.md

**Urteil `kernaussage_ok`:** ✅ ja

**Begründung:** Die Antwort enthält die Kernaussage, dass Pro normalerweise bis zum Ende des bezahlten Zeitraums weiterläuft und danach auf Free umgestellt wird; die Erwähnung 'keine weitere Abbuchung' fehlt zwar, ist aber ein tolerierbarer Nebenpunkt.

**Julian stimmt zu? (ja/nein):** 

---

## 3. Frage #16 · sections · einfach · Kriterium `kernaussage_ok`

**Frage:** gibts eigentlich ein widget für android oder nur fürs iphone?

**Antwort (Haiku 4.5):**

> Es gibt Widgets für beide Plattformen! 📱
>
> **Android:** Widgets sind ab Android 10 verfügbar. Du kannst sie auf deinen Startbildschirm hinzufügen:
> 1. Halte eine freie Stelle auf dem Startbildschirm gedrückt und tippe auf „Widgets".
> 2. Suche „FocusFlow" und ziehe das gewünschte Widget auf den Startbildschirm.
>
> **iOS:** Hier gibt es Widgets für den Home-Bildschirm und sogar für den Sperrbildschirm (ab iOS 17).
>
> Falls dein Widget sich nicht aktualisiert, kann bei Android die Akku-Optimierung der Grund sein – nimm FocusFlow dann unter Einstellungen > Apps > FocusFlow > Akku von der Optimierung aus.
>
> Quellen: widgets.md

**Kernaussage (Goldset):** Ja, Android ab Version 10 (Startbildschirm); Timer-Widget nur mit Pro

**Kontext-Dateien:** widgets.md; roadmap-faq.md

**Urteil `kernaussage_ok`:** ✅ ja

**Begründung:** Die Antwort bestätigt, dass es Android-Widgets ab Android 10 gibt, was die Hauptaussage abdeckt. Der Nebenpunkt zum Timer-Widget nur mit Pro fehlt, ist aber laut Kriterien als fehlender Nebenpunkt tolerierbar.

**Julian stimmt zu? (ja/nein):** 

---

## 4. Frage #13 · contextual · einfach · Kriterium `treu`

**Frage:** doppelt abgebucht diesen monat!! 6,99 zweimal. bitte sofort erstatten

**Antwort (Haiku 4.5):**

> Ich verstehe deine Frustration! Lass mich dir helfen.
>
> **Erste Überprüfung:** Schau in deinem Bankkonto nach, ob eine der beiden Buchungen als „vorgemerkt" oder „ausstehend" angezeigt wird. Das ist oft nur eine vorübergehende Bankvormerkung und verschwindet von selbst innerhalb von 3–5 Werktagen.
>
> **Falls beide Buchungen nach 5 Werktagen noch da sind:**
>
> 1. Öffne in der App **Einstellungen > Hilfe > Kontakt**
> 2. Wähle „Zahlungsproblem melden"
> 3. Gib deine FocusFlow-E-Mail-Adresse an
> 4. Füge wenn möglich einen Screenshot beider Buchungen oder die Transaktionsnummern bei
>
> Wir prüfen dann deinen Fall und erstatten den doppelt belasteten Betrag vollständig auf dein ursprüngliches Zahlungsmittel. Dein Pro-Zugang bleibt davon unberührt.
>
> Quellen: bekannte-probleme.md; doppelte-abbuchung.md

**Kernaussage (Goldset):** Oft nur Vormerkung, verschwindet in 3–5 Werktagen; danach über Einstellungen > Hilfe > Kontakt "Zahlungsproblem melden", wird vollständig erstattet; Store-Abos an Apple/Google

**Kontext-Dateien:** bekannte-probleme.md; doppelte-abbuchung.md

**Urteil `treu`:** ✅ ja

**Begründung:** Alle genannten Fakten – Vormerkung, 3–5 Werktage, Meldeschritte über Einstellungen>Hilfe>Kontakt, vollständige Erstattung und unberührter Pro-Zugang – sind wortgetreu im Kontext belegt, keine zusätzlichen unbelegten Behauptungen.

**Julian stimmt zu? (ja/nein):** 

---

## 5. Frage #13 · articles · einfach · Kriterium `treu`

**Frage:** doppelt abgebucht diesen monat!! 6,99 zweimal. bitte sofort erstatten

**Antwort (Haiku 4.5):**

> Ich verstehe deine Frustration! Lass mich dir helfen.
>
> **Wichtig zuerst:** Prüfe in deinem Bankkonto, ob beide Buchungen als „vorgemerkt" oder „ausstehend" angezeigt werden. Das ist oft nur eine Autorisierung deiner Bank und verschwindet von selbst innerhalb von **3–5 Werktagen**. In diesem Fall musst du nichts tun.
>
> **Falls die Buchung nach 5 Werktagen noch da ist:**
>
> 1. Öffne in der App **Einstellungen > Hilfe > Kontakt**
> 2. Wähle „Zahlungsproblem melden"
> 3. Gib deine FocusFlow-E-Mail-Adresse an
> 4. Füge wenn möglich einen Screenshot beider Buchungen oder die Transaktionsnummern bei
>
> Wir prüfen das dann und erstatten den doppelt belasteten Betrag vollständig auf dein ursprüngliches Zahlungsmittel. Dein Pro-Zugang bleibt bestehen.
>
> Quellen: doppelte-abbuchung.md;bekannte-probleme.md

**Kernaussage (Goldset):** Oft nur Vormerkung, verschwindet in 3–5 Werktagen; danach über Einstellungen > Hilfe > Kontakt "Zahlungsproblem melden", wird vollständig erstattet; Store-Abos an Apple/Google

**Kontext-Dateien:** doppelte-abbuchung.md; bekannte-probleme.md; erstattungen.md

**Urteil `treu`:** ✅ ja

**Begründung:** Alle Aussagen (Vormerkung, 3-5 Werktage, Meldeweg, vollständige Erstattung, Pro-Zugang bleibt bestehen) sind wörtlich oder sinngemäß aus dem Kontext gedeckt.

**Julian stimmt zu? (ja/nein):** 

---

## 6. Frage #23 · sections · aehnlich · Kriterium `treu`

**Frage:** hab pro übers iphone gekauft. wenn ich jetzt mein konto lösche, hören die abbuchungen dann auf?

**Antwort (Haiku 4.5):**

> Gute Frage! Wenn du dein Konto löschst, **stoppt die Abbuchung nicht automatisch**. 
>
> Das ist wichtig zu wissen: Abos, die du über den App Store gekauft hast, werden bei einer Kontolöschung **nicht automatisch beendet**. Das bedeutet, dass weiterhin Geld abgebucht wird, auch wenn dein FocusFlow-Konto gelöscht ist.
>
> **Das solltest du vorher tun:**
> Kündige dein Pro-Abo im App Store, bevor du dein Konto löschst. Dann stoppt die Abbuchung und du vermeidest unnötige Kosten.
>
> Falls du nur nicht mehr für Pro bezahlen möchtest, ist eine Kontolöschung meist nicht nötig – eine normale Kündigung reicht aus. Dabei bleiben deine Daten erhalten und du kannst FocusFlow kostenlos weiternutzen.
>
> Quellen: konto-loeschen.md

**Kernaussage (Goldset):** Nein, Store-Abos werden nicht automatisch beendet; vorher im App Store kündigen, sonst wird weiter abgebucht

**Kontext-Dateien:** konto-loeschen.md; abo-kuendigen.md; erstattungen.md; pro-funktionen-und-preise.md

**Urteil `treu`:** ✅ ja

**Begründung:** Alle Behauptungen (keine automatische Beendigung des Store-Abos, vorherige Kündigung nötig, Hinweis auf Abo-Kündigen-Artikel mit Datenerhalt und kostenloser Weiternutzung) sind direkt durch den Kontext gedeckt.

**Julian stimmt zu? (ja/nein):** 

---

## 7. Frage #10 · contextual · mehrquellen · Kriterium `treu`

**Frage:** Ich will den Tarif wieder von Pro zu Free wechseln und hab Pro 7 Tage ausprobiert, was passiert mit Restguthaben

**Antwort (Haiku 4.5):**

> Gute Frage! Basierend auf den Informationen zur 7-tägigen Testphase:
>
> Wenn du Pro während der **kostenlosen 7-Tage-Testphase** kündigst, wird dir nichts berechnet – es gibt also kein Restguthaben, da du noch gar nicht bezahlt hast.
>
> Nach der Testphase beginnt dein gewähltes Abo automatisch. Falls du danach kündigst, läuft dein Pro-Zugang bis zum Ende des bereits bezahlten Zeitraums weiter, bevor dein Konto auf Free umgestellt wird. Eine Rückerstattung für den restlichen Zeitraum ist in den verfügbaren Informationen nicht erwähnt.
>
> Für spezifische Fragen zu Restguthaben oder Rückerstattungen empfehle ich dir, den Support zu kontaktieren – in der App unter **Einstellungen > Hilfe > Kontakt**.
>
> Quellen: pro-funktionen-und-preise.md; abo-kuendigen.md

**Kernaussage (Goldset):** Kündigen: Pro läuft bis Ende des bezahlten Zeitraums, keine weitere Abbuchung. Geld zurück nur beim Jahresabo innerhalb von 14 Tagen (dann endet Pro sofort); Monatsabo wird nie erstattet

**Kontext-Dateien:** erstattungen.md; pro-funktionen-und-preise.md; abo-kuendigen.md

**Urteil `treu`:** ✅ ja

**Begründung:** Alle genannten Fakten (Testphase ohne Berechnung, automatischer Abo-Start danach, Fortlaufen des Pro-Zugangs bis Periodenende) sind direkt durch die Quellen abo-kuendigen.md und pro-funktionen-und-preise.md gedeckt; die Aussage zum fehlenden Restguthaben während der Testphase ist eine logisch zwingende Folgerung, und der Verweis auf den Support ist vorgegeben zulässig.

**Julian stimmt zu? (ja/nein):** 

---

## 8. Frage #10 · articles · mehrquellen · Kriterium `kernaussage_ok`

**Frage:** Ich will den Tarif wieder von Pro zu Free wechseln und hab Pro 7 Tage ausprobiert, was passiert mit Restguthaben

**Antwort (Haiku 4.5):**

> Du möchtest von Pro zurück zu Free wechseln – das ist kein Problem! 
>
> **Zur Erstattung:** Das hängt davon ab, wie du Pro abgeschlossen hast:
>
> - **Jahresabo:** Du bekommst den vollen Betrag zurück, wenn du die Erstattung **innerhalb von 14 Tagen** beantragst (gerechnet ab Kauf). Da du erst 7 Tage dabei bist, passt das zeitlich perfekt. Es wird der Betrag erstattet, den du tatsächlich bezahlt hast.
>
> - **Monatsabo:** Bereits begonnene Monate werden leider nicht erstattet, auch nicht anteilig.
>
> **So beantragst du eine Erstattung:**
> - **Web-Abo:** Einstellungen > Hilfe > Kontakt > „Erstattung anfragen". Gib deine E-Mail-Adresse und das Kaufdatum an.
> - **App Store/Google Play:** Beantrage die Erstattung direkt bei Apple oder Google Play – wir können das technisch nicht selbst machen.
>
> Nach einer Erstattung wird dein Konto sofort auf Free umgestellt, deine Daten bleiben aber erhalten.
>
> Quellen: erstattungen.md

**Kernaussage (Goldset):** Kündigen: Pro läuft bis Ende des bezahlten Zeitraums, keine weitere Abbuchung. Geld zurück nur beim Jahresabo innerhalb von 14 Tagen (dann endet Pro sofort); Monatsabo wird nie erstattet

**Kontext-Dateien:** abo-kuendigen.md; tarif-wechseln.md; erstattungen.md

**Urteil `kernaussage_ok`:** ❌ nein

**Begründung:** Die Antwort behandelt nur die Erstattungsregeln, lässt aber den zentralen Punkt der Kündigung – dass Pro bis zum Ende des bezahlten Zeitraums weiterläuft und keine weitere Abbuchung erfolgt – komplett aus, obwohl dies laut Soll-Kernaussage ein Hauptbestandteil ist.

**Julian stimmt zu? (ja/nein):** 

---

## 9. Frage #7 · corpus · luecke · Kriterium `luecke_ok`

**Frage:** Gibt es Mengenrabatte

**Antwort (Haiku 4.5):**

> Ich kann deine Frage zu Mengenrabatten leider nicht aus den verfügbaren Hilfartikeln beantworten. Die Informationen dazu sind nicht in meinem Kontext enthalten.
>
> Bitte wende dich direkt an unseren Support: Öffne die App und gehe zu **Einstellungen > Hilfe > Kontakt**. Dort kannst du deine Frage stellen und erhältst eine persönliche Antwort.
>
> Quellen: keine

**Kernaussage (Goldset):** Dazu gibt es keine Information, Verweis an den Support

**Kontext-Dateien:** alle

**Urteil `luecke_ok`:** ✅ ja

**Begründung:** Die Antwort sagt klar, dass keine Information zu Mengenrabatten vorliegt, verweist an den Support und gibt keine inhaltliche Teilantwort oder Vermutung.

**Julian stimmt zu? (ja/nein):** 

---

## 10. Frage #8 · corpus · luecke · Kriterium `treu`

**Frage:** Kann ich Daten aus anderen Apps importieren

**Antwort (Haiku 4.5):**

> Ich kann deine Frage anhand der verfügbaren Hilfeartikel leider nicht beantworten. Der Kontext enthält keine Informationen zum Import von Daten aus anderen Apps.
>
> Für diese Frage empfehle ich dir, den Support zu kontaktieren: Öffne dazu in der App **Einstellungen > Hilfe > Kontakt** und stelle deine Frage dort.
>
> Quellen: keine

**Kernaussage (Goldset):** Dazu gibt es keine Information, Verweis an den Support

**Kontext-Dateien:** alle

**Urteil `treu`:** ✅ ja

**Begründung:** Die Antwort enthält keine inhaltlichen Behauptungen aus dem Kontext, sondern nur den vorgegebenen Support-Verweis, der immer als gedeckt gilt.

**Julian stimmt zu? (ja/nein):** 
