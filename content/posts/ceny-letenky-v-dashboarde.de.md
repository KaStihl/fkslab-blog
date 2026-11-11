---
title: "Flugpreise im Dashboard: was ich ergänzt habe und was dabei herauskam"
date: 2026-11-11
draft: false
description: "Passagierzahlen sagen nicht, ob Billigairlines Tickets günstiger gemacht haben. Ich habe den Flugpreisindex von Eurostat in den Report aufgenommen: wie er funktioniert, warum er schwankt und was er für September 2026 zeigt."
tags: ["Power BI", "Flugpreise", "Eurostat", "Datenvisualisierung", "VIE", "BTS"]
ShowToc: false
ShowReadingTime: true
---

{{< stats >}}
{{< stat value="−55.8" suffix=" %" label="Flugpreise in der Slowakei, September 2026 (zum Vorjahr)" >}}
{{< stat value="+12" suffix=" %" label="Flugpreise in Österreich, September 2026 (zum Vorjahr)" >}}
{{< stat value="+5.6" suffix=" %" label="EU-Durchschnitt, September 2026 (zum Vorjahr)" >}}
{{< /stats >}}

Lange beantwortete der Report nur die Frage „wie viele Menschen fliegen“. Als Billigairlines Kapazität von Wien nach Bratislava verlagerten, kam eine zweite Frage auf: **Sind die Tickets günstiger geworden?** Passagierzahlen können das nicht sagen. Also habe ich dem Report eine neue Seite hinzugefügt: **Prices**.

## Woher die Zahlen kommen

Die Quelle ist Eurostat: der harmonisierte Verbraucherpreisindex (HICP), Position „Passenger transport by air“. Er gibt jeden Monat an, um wie viel Prozent Flugtickets teurer oder günstiger sind als im selben Monat des Vorjahres, für jedes EU-Land. Ich erfasse die Slowakei, Österreich, Tschechien, Ungarn, Belgien und den EU-Durchschnitt.

Ich habe die Werte mit einer anderen Quelle verglichen: Ein Presseartikel mit Eurostat-Zitat nannte für die Slowakei −53,0 %, −48,2 % und −45,1 % von April bis Juni 2026. Die Eurostat-Daten stimmen auf ein Zehntelprozent.

## Wie es in der Pipeline funktioniert

- Ein Python-Scraper lädt die Daten aus der öffentlichen Eurostat-API und speichert sie in einer Supabase-Tabelle, wie alle anderen Daten auch.
- Power BI liest sie über dieselbe öffentliche, schreibgeschützte Schnittstelle.
- Die Tabelle legt sich beim ersten Lauf selbst an. Bis dahin ist die Seite einfach leer, und nichts schlägt fehl.

## Drei Designentscheidungen

1. **Ein Dreimonatsdurchschnitt neben dem letzten Monat.** Der Index schwankt stark. Die Slowakei bewegte sich 2025 zwischen −23 % und +40 %, und Belgien sprang von +43 % im März 2026 auf −4 % im September. Ein Monat beweist nichts, eine Reihe von drei Monaten schon eher.
2. **Weder Rot noch Grün.** Ein niedrigerer Preis ist für Reisende gut und für die Airline schlecht, also darf die Farbe nichts bewerten. Die Slowakei und Österreich behalten die Farben ihrer Flughäfen, der EU-Durchschnitt ist neutral grau.
3. **Ein Text, der keine Ursache unterstellt.** Unter dem Diagramm steht, dass der Index Preise im Warenkorb eines Landes abbildet und nicht Flüge eines einzelnen Flughafens, und dass ein Rückgang seine Ursache nicht beweist.

## Was der September 2026 zeigt

| | September | Letzte drei Monate (Durchschnitt) |
|---|---|---|
| Slowakei | −55,8 % | −53,5 % |
| Österreich | +12,0 % | +11,5 % |
| EU-Durchschnitt | +5,6 % | +2,6 % |

Slowakische Tickets sind um mehr als die Hälfte günstiger als vor einem Jahr, österreichische um 12 % teurer. Das passt zur Verlagerung von Billigstrecken, aber der Index allein beweist es nicht: Über die Verlagerung sagen die Flug- und Passagierzahlen etwas aus. Und Preise können sich auch aus anderen Gründen bewegen (Treibstoff, Nachfrage, Saison).

<!-- ![Die Seite Prices im Report](/images/vie-bts/prices.png) -->

## Behind the scenes

Beim Testen sind mir zwei Fehler aufgefallen, die man auf den ersten Blick nicht sieht. Die Karte „gegenüber der vorherigen Meldung“ für Wien verglich den August aus den Flughafenzahlen mit dem Juli von Eurostat (das 1 bis 3 % höher zählt) und zeigte +0,3 % statt der tatsächlichen +12 %. Und eine unnötige Eurostat-Spalte gelangte über die Verbindung ins Modell. Beide Korrekturen liegen im Repository, mit Tests.

{{< cta text="Zum Live-Dashboard" url="/dashboard/" >}}
