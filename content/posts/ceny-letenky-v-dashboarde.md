---
title: "Ceny letenky v dashboarde: čo som pridal a čo z toho vyšlo"
date: 2026-11-11
draft: false
description: "Počty pasažierov nepovedia, či lacné aerolinky zlacnili letenky. Pridal som do reportu index cien letenky od Eurostatu: ako funguje, prečo je hlučný a čo ukazuje za september 2026."
tags: ["Power BI", "ceny letenky", "Eurostat", "dátová vizualizácia", "VIE", "BTS"]
ShowToc: false
ShowReadingTime: true
---

{{< stats >}}
{{< stat value="−55.8" suffix=" %" label="letenky na Slovensku, september 2026 (medziročne)" >}}
{{< stat value="+12" suffix=" %" label="letenky v Rakúsku, september 2026 (medziročne)" >}}
{{< stat value="+5.6" suffix=" %" label="priemer EÚ, september 2026 (medziročne)" >}}
{{< /stats >}}

Report dlho odpovedal len na otázku „koľko ľudí lieta“. Keď lacné aerolinky presunuli kapacitu z Viedne do Bratislavy, napadla ma druhá: **zlacneli letenky?** Počty pasažierov to nepovedia. Tak som do reportu pridal novú stránku **Prices**.

## Odkiaľ čísla pochádzajú

Zdrojom je Eurostat: harmonizovaný index spotrebiteľských cien (HICP), položka „Passenger transport by air“. Každý mesiac udáva, o koľko percent sú letenky drahšie alebo lacnejšie než v rovnakom mesiaci pred rokom, pre každú krajinu EÚ. Zbieram Slovensko, Rakúsko, Česko, Maďarsko, Belgicko a priemer EÚ.

Skontroloval som ich proti inému zdroju: tlačová správa citujúca Eurostat uvádzala pre Slovensko −53,0 %, −48,2 % a −45,1 % v apríli až júni 2026. Údaje z Eurostatu sedia na desatinu percenta.

## Ako to funguje v pipeline

- Python scraper stiahne údaje z verejného API Eurostatu a uloží ich do tabuľky v Supabase (rovnako ako ostatné údaje).
- Power BI ich číta cez to isté verejné rozhranie, len na čítanie.
- Tabuľka sa vytvorí pri prvom behu sama. Dovtedy je stránka prázdna a nič nezlyhá.

## Tri rozhodnutia pri návrhu

1. **Trojmesačný priemer popri poslednom mesiaci.** Index je veľmi kolísavý. Slovensko sa v roku 2025 pohybovalo medzi −23 % a +40 %, Belgicko skočilo z +43 % v marci 2026 na −4 % v septembri. Jeden mesiac nič nedokazuje, trojmesačný beh áno.
2. **Žiadna červená ani zelená.** Nižšia cena je pre cestujúceho dobrá a pre aerolinku zlá, tak farba nesmie nič hodnotiť. Slovensko a Rakúsko majú farby svojich letísk a priemer EÚ je neutrálne sivý.
3. **Text, ktorý nepripúšťa príčinu.** Pod grafom stojí, že index pokrýva ceny v spotrebiteľskom koši krajiny, nie lety z jedného letiska, a že pokles príčinu nedokazuje.

## Čo ukazuje september 2026

| | September | Posledné tri mesiace (priemer) |
|---|---|---|
| Slovensko | −55,8 % | −53,5 % |
| Rakúsko | +12,0 % | +11,5 % |
| Priemer EÚ | +5,6 % | +2,6 % |

Slovenské letenky sú o viac než polovicu lacnejšie než pred rokom a rakúske o 12 % drahšie. Zhoduje sa to s presunom nízkonákladových liniek, ale index sám o sebe to nedokazuje: o presune hovoria počty letov a pasažierov. A ceny sa môžu hýbať aj z iných dôvodov (palivo, dopyt, sezóna).

<!-- ![Stránka Prices v reporte](/images/vie-bts/prices.png) -->

## Behind the scenes

Pri testoch som narazil na dve chyby, ktoré by na prvý pohľad nikto nevidel. Karta Viedne „oproti predchádzajúcemu vydaniu“ porovnávala august z údajov letiska s júlom z Eurostatu (ten počíta o 1 až 3 % vyššie), takže ukazovala +0,3 % namiesto skutočných +12 %. A do modelu sa cez pripojenie dostal nepotrebný stĺpec z Eurostatu. Obe opravy sú v repozitári aj s testami.

{{< cta text="Pozrieť živý dashboard" url="/dashboard/" >}}
