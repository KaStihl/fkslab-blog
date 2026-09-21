---
title: "VIE/BTS Aviation Tracker"
date: 2026-08-02
draft: false
ShowToc: false
ShowReadingTime: false
---

Ich wohne in Bratislava, und in letzter Zeit lässt sich kaum übersehen, wie viel über unseren Flughafen geschrieben wird — Rekordwachstum bei den Passagierzahlen, Monat für Monat. Parallel dazu spielte sich eine andere Geschichte ab: Sowohl Wizz Air als auch Ryanair haben im März 2026 ihre Präsenz in Wien deutlich reduziert, nachdem Österreich eine Flugticketsteuer eingeführt hat, die es in der Slowakei nicht gibt.

Diese beiden Geschichten sind eigentlich eine. Der Nachbarflughafen gewinnt genau das, was der andere verliert.

Ich arbeite als BI-Berater, und es kam mir seltsam vor, dass das niemand systematisch in Zahlen verfolgt — nur in Schlagzeilen. Also habe ich mir dafür eine eigene Datenpipeline gebaut.

{{< route from="VIE" to="BTS" >}}

{{< stats >}}
{{< stat value="2" label="live verglichene Flughäfen" >}}
{{< stat value="3" label="primäre Datenquellen" >}}
{{< stat value="7" label="automatisierte Aufgaben in der Pipeline" >}}
{{< stat value="0" label="Schätzungen" >}}
{{< /stats >}}

## Was dieses Projekt macht

Jeden Monat lade ich automatisch die offiziellen Pressemitteilungen von Vienna Airport und Bratislava Airport herunter und extrahiere daraus Passagierzahlen, Veränderung zum Vorjahr und Kapazität. Keine Schätzungen, keine Sekundärquellen — direkt aus den Zahlen, die die Flughäfen selbst veröffentlichen.

## Methodik und Transparenz

Der gesamte Code ist offen und öffentlich auf GitHub: [github.com/KaStihl/vie-bts-tracker](https://github.com/KaStihl/vie-bts-tracker).

Die Wiener Daten werden vollautomatisch geparst. Die Bratislavaer Daten durchlaufen eine kurze manuelle Kontrolle, da die dortigen Pressemitteilungen weniger einheitlich formatiert sind — Genauigkeit ist mir wichtiger als Geschwindigkeit.

Fragen, Anmerkungen oder einen Fehler in den Daten entdeckt? Schreiben Sie mir.
