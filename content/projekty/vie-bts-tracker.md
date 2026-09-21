---
title: "VIE/BTS Aviation Tracker"
date: 2026-08-02
draft: false
ShowToc: false
ShowReadingTime: false
---

Bývam v Bratislave a v poslednom čase si nedá nevšimnúť, že sa o našom letisku veľa píše — rekordný rast pasažierov mesiac čo mesiac. Paralelne sa odohral iný príbeh: Wizz Air aj Ryanair v marci 2026 výrazne znížili svoju prítomnosť vo Viedni, po tom čo Rakúsko zaviedlo letiskovú daň, ktorú Slovensko nemá.

Tieto dva príbehy sú vlastne jeden. Susedné letisko naberá presne to, čo druhé stráca.

Pracujem ako BI konzultant a prišlo mi zvláštne, že to niekto nesleduje systematicky v číslach — len v novinových titulkoch. Tak som si na to postavil vlastný dátový pipeline.

{{< route from="VIE" to="BTS" >}}

{{< stats >}}
{{< stat value="2" label="letiská porovnávané naživo" >}}
{{< stat value="3" label="primárne zdroje dát" >}}
{{< stat value="7" label="automatizovaných úloh v pipeline" >}}
{{< stat value="0" label="odhadov" >}}
{{< /stats >}}

## Čo tento projekt robí

Každý mesiac automaticky sťahujem oficiálne tlačové správy z Vienna Airport a Bratislava Airport a extrahujem z nich čísla o počte pasažierov, medziročnej zmene a kapacite. Žiadne odhady ani sekundárne zdroje — priamo z čísel, ktoré letiská samé publikujú.

## Metodológia a transparentnosť

Celý kód je otvorený a verejný na GitHube: [github.com/KaStihl/vie-bts-tracker](https://github.com/KaStihl/vie-bts-tracker).

Dáta z Viedne sa parsujú plne automaticky. Dáta z Bratislavy prechádzajú krátkou manuálnou kontrolou, keďže tamojšie tlačové správy nemajú taký jednotný formát — presnosť je pre mňa dôležitejšia než rýchlosť.

Otázky, postrehy alebo si všimol chybu v dátach? Napíš mi.