---
title: "Prerobil som VIE/BTS report: z tabuľky na príbeh"
date: 2026-10-11
draft: false
description: "Prvá verzia môjho Power BI reportu ukazovala čísla, ale nič nevysvetľovala. Nová verzia má úvod, mesačné porovnanie, červené poklesy a doplnené chýbajúce mesiace."
tags: ["Power BI", "dátová vizualizácia", "VIE", "BTS", "Eurostat"]
ShowToc: false
ShowReadingTime: true
---

{{< stats >}}
{{< stat value="3" suffix=" strany" label="Home, Trend a Source namiesto jednej stránky" >}}
{{< stat value="5.1" suffix="×" label="o koľko je Viedeň väčšia ako Bratislava (júl 2026)" >}}
{{< stat value="97" suffix=" → 184" label="mesačných údajov po doplnení z Eurostatu" >}}
{{< /stats >}}

Keď som report po prvý raz ukázal ľuďom, dostal som úprimnú odpoveď: čísla tam sú, ale nie je z toho jasné, čo z nich mám vyčítať. Mali pravdu. Report bol zbierkou kariet a grafov a o príbehu medzi Viedňou a Bratislavou musel čitateľ hádať sám. Tak som ho prerobil.

## Home: najprv vysvetliť, potom ukázať

Prvá stránka už nie je ďalší panel s číslami. Je to úvod: o čom report je, ako ho čítať a ako dobre mu môžete veriť. Vysvetľuje aj skratku **pp** (percentuálne body), ktorá v prvej verzii nikomu nič nehovorila: rozdiel medzi rastom +76 % a poklesom −7 % je 83 pp, nie 83 %. Dole je schéma „ako to funguje“, od oficiálnych zdrojov cez scrapery a databázu až po report.

![Úvodná stránka reportu s vysvetlením, ako report čítať](/images/vie-bts/home.png)

## Trend: každá karta odpovedá na jednu otázku

- **Predchádzajúce vydanie.** Každá karta letiska ukazuje aktuálny mesiac, medziročnú zmenu aj predchádzajúci mesiac, takže hneď vidno, či sa trend zrýchľuje.
- **Červené poklesy.** Medziročná zmena je pre každé letisko vlastný graf s vlastnou osou. Rast je vo farbe letiska, pokles červený. Pri spoločnej osi by sa pokles Viedne (−5 až −8 %) strácal vedľa rastu Bratislavy (+76 %).
- **Rozdiel v rastoch.** Samostatná karta ukáže rozdiel v rastoch v pp a pomer veľkosti letísk.
- **Časová os.** Pod grafmi sú tri udalosti, ktoré príbeh vysvetľujú: Wizz Air otvára základňu v Bratislave, končí vo Viedni a Rakúsko zavádza leteckú daň.

![Stránka Trend s kartami letísk a grafmi medziročnej zmeny](/images/vie-bts/trend.png)

## Source: odkiaľ čísla pochádzajú

Každý zdroj má vlastnú kartu s odkazom a poznámky vysvetľujú, čo sa stane, keď údaj chýba. Je to dôležité, lebo oficiálne zdroje nie sú úplné.

![Stránka Source so zoznamom zdrojov a poznámkami k dátam](/images/vie-bts/source.png)

## Chýbajúci júl a čo s ním

Pri kontrole som zistil, že v dátach chýba júl 2026. Nie je to chyba scrapera: Viedeň tlačové správy o výsledkoch za niektoré mesiace (najčastejšie júl, október a december) nezverejňuje a Bratislava ich zverejňuje nepravidelne: za rok 2025 mám v databáze len jediný mesiac.

Našiel som to, čo oba problémy rieši: **Eurostat** zverejňuje mesačné počty pasažierov pre každé letisko v EÚ. Porovnal som ich s tlačovými správami:

- **Bratislava:** číslo z Eurostatu sa zhoduje s číslom letiska na pasažiera presne (napríklad máj 2026: 398 639, august 2026: 625 742).
- **Viedeň:** Eurostat počíta inak a vychádza o 1 až 3 % vyššie než Flughafen Wien.

Preto sa Eurostat používa len na doplnenie mesiacov, ktoré letisko nezverejnilo, a v reporte je viditeľne označený. Medziročná zmena sa pri ňom počíta v rámci samotného Eurostatu, takže sa nikdy nemiešajú dve metodiky. Výsledok pre júl 2026: Bratislava **619 902** pasažierov (+72,7 %), Viedeň **3 163 309** (−4,7 % podľa Eurostatu).

## Aby dáta neboli staré

Verejná verzia reportu ukazovala stále údaje z 2. októbra. Dôvod bol technický: Power BI Service nedôveruje certifikátu, ktorým je Supabase chránené pri priamom pripojení k databáze. Report teraz číta dáta cez verejné rozhranie Supabase, ktoré používa bežný certifikát, a len na čítanie. Čas poslednej aktualizácie je navyše vždy v UTC, aby ukazoval to isté v Desktope aj v službe.

## Behind the scenes

Farby som nevyberal od oka. Overil som ich validátorom pre farboslepých a pre tmavé pozadie: úvodná paleta bola v tmavom režime príliš svetlá, tak som ju upravil. Biely text na kartách má kontrast 15:1, tlmený 6,9:1 a červená 6:1, všetko nad hranicou 4,5:1. Celý report je v Power BI Projekte (PBIP) a generuje ho skript, takže je v Gite a dá sa zopakovať.

{{< cta text="Pozrieť živý dashboard" url="/dashboard/" >}}
