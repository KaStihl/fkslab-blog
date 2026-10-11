---
title: "Ich habe den VIE/BTS-Report neu gebaut: von der Tabelle zur Geschichte"
date: 2026-10-11
draft: false
description: "Die erste Version meines Power-BI-Reports zeigte Zahlen, erklärte aber nichts. Die neue Version hat eine Einleitung, den Vormonatsvergleich, rote Rückgänge und ergänzte fehlende Monate."
tags: ["Power BI", "Datenvisualisierung", "VIE", "BTS", "Eurostat"]
ShowToc: false
ShowReadingTime: true
---

{{< stats >}}
{{< stat value="3" suffix=" Seiten" label="Home, Trend und Source statt einer einzigen Seite" >}}
{{< stat value="5.1" suffix="×" label="so viel größer ist Wien als Bratislava (Juli 2026)" >}}
{{< stat value="184" suffix=" Monate" label="in den Daten, davon 55 durch Eurostat ergänzt" >}}
{{< /stats >}}

Als ich den Report zum ersten Mal Leuten gezeigt habe, bekam ich eine ehrliche Antwort: Die Zahlen sind da, aber es wird nicht klar, was man daraus ablesen soll. Sie hatten recht. Der Report war eine Sammlung aus Karten und Diagrammen, und die Geschichte zwischen Wien und Bratislava musste der Leser selbst erraten. Also habe ich ihn neu gebaut.

## Home: erst erklären, dann zeigen

Die erste Seite ist kein weiteres Zahlenpanel mehr. Sie ist eine Einleitung: worum es im Report geht, wie man ihn liest und wie weit man ihm vertrauen kann. Sie erklärt auch **pp** (Prozentpunkte), die Abkürzung, die in der ersten Version niemand verstanden hat: Der Abstand zwischen +76 % Wachstum und −7 % Rückgang beträgt 83 pp, nicht 83 %. Unten zeigt ein Schema, wie alles funktioniert, von den offiziellen Quellen über Scraper und Datenbank bis zum Report.

![Startseite des Reports mit Erklärung, wie er zu lesen ist](/images/vie-bts/home.png)

## Trend: jede Karte beantwortet eine Frage

- **Vorherige Meldung.** Jede Flughafenkarte zeigt den aktuellen Monat, die Veränderung zum Vorjahr und den Vormonat, sodass man sofort sieht, ob ein Trend schneller wird.
- **Rote Rückgänge.** Die Veränderung zum Vorjahr ist pro Flughafen ein eigenes Diagramm mit eigener Achse. Wachstum hat die Farbe des Flughafens, Rückgänge sind rot. Auf einer gemeinsamen Achse würde Wiens Rückgang (−5 bis −8 %) neben Bratislavas Wachstum (+76 %) verschwinden.
- **Wachstumsabstand.** Eine eigene Karte zeigt den Unterschied der Wachstumsraten in pp und das Größenverhältnis der beiden Flughäfen.
- **Zeitleiste.** Drei Ereignisse unter den Diagrammen erklären die Geschichte: Wizz Air eröffnet eine Basis in Bratislava, beendet den Betrieb in Wien, und Österreich führt die Flugabgabe ein.

![Trend-Seite mit Flughafenkarten und Diagrammen zur Veränderung zum Vorjahr](/images/vie-bts/trend.png)

## Source: woher die Zahlen kommen

Jede Quelle hat eine eigene Karte mit Link, und die Hinweise erklären, was passiert, wenn ein Wert fehlt. Das ist wichtig, weil offizielle Quellen nicht vollständig sind.

![Source-Seite mit den Quellen und Datenhinweisen](/images/vie-bts/source.png)

## Der fehlende Juli und was man damit macht

Bei der Prüfung habe ich festgestellt, dass der Juli 2026 in den Daten fehlt. Das ist kein Scraper-Fehler: Wien veröffentlicht für manche Monate keine Pressemitteilung (am häufigsten Juli, Oktober und Dezember), und Bratislava veröffentlicht unregelmäßig: Für 2025 hat die Datenbank nur 7 von 12 Monaten.

Ich habe etwas gefunden, das beide Probleme löst: **Eurostat** veröffentlicht monatliche Passagierzahlen für jeden Flughafen in der EU. Ich habe sie mit den Pressemitteilungen verglichen:

- **Bratislava:** Die Eurostat-Zahl stimmt mit der des Flughafens auf den Passagier genau überein (zum Beispiel Mai 2026: 398.639, August 2026: 625.742).
- **Wien:** Eurostat zählt anders und liegt 1 bis 3 % über den Zahlen der Flughafen Wien AG.

Deshalb wird Eurostat nur zur Ergänzung von Monaten verwendet, die der Flughafen nicht veröffentlicht hat, und im Report deutlich gekennzeichnet. Die Veränderung zum Vorjahr wird dabei innerhalb der Eurostat-Reihe berechnet, sodass nie zwei Methoden vermischt werden. Das Ergebnis für Juli 2026: Bratislava **619.902** Passagiere (+72,7 %), Wien **3.163.309** (−4,7 % nach Eurostat).

## Damit die Daten nicht veraltet sind

Die öffentliche Version des Reports zeigte immer noch Daten vom 2. Oktober. Der Grund war technisch: Der Power-BI-Dienst vertraut dem Zertifikat nicht, das Supabase bei direkten Datenbankverbindungen verwendet. Der Report liest die Daten jetzt über die öffentliche Schnittstelle von Supabase, die ein normales Zertifikat nutzt und nur lesen kann. Die Zeit der letzten Aktualisierung ist immer in UTC, damit sie in Desktop und im Dienst dasselbe zeigt.

## Behind the scenes

Die Farben habe ich nicht nach Gefühl gewählt. Ich habe sie für Farbenblinde und für den dunklen Hintergrund geprüft: Meine erste Palette war im dunklen Modus zu hell, also habe ich sie angepasst. Weißer Text auf den Karten hat ein Kontrastverhältnis von 15:1, gedämpfter Text 6,9:1 und Rot 6:1, alles über der Schwelle von 4,5:1. Der ganze Report ist ein Power-BI-Projekt (PBIP), das ein Skript erzeugt, also liegt er in Git und lässt sich reproduzieren.

{{< cta text="Zum Live-Dashboard" url="/dashboard/" >}}
