---
title: "VIE/BTS Aviation Tracker"
date: 2026-08-02
draft: false
ShowToc: false
ShowReadingTime: false
---

I live in Bratislava, and lately it's hard to miss how much is being written about our airport — record passenger growth month after month. In parallel, another story played out: both Wizz Air and Ryanair significantly scaled back their presence in Vienna in March 2026, after Austria introduced an aviation tax that Slovakia doesn't have.

These two stories are really one. The neighboring airport is picking up exactly what the other is losing.

I work as a BI consultant, and it struck me as odd that nobody was tracking this systematically in numbers — only in headlines. So I built my own data pipeline for it.

{{< route from="VIE" to="BTS" >}}

{{< stats >}}
{{< stat value="2" label="airports compared live" >}}
{{< stat value="3" label="primary data sources" >}}
{{< stat value="7" label="automated jobs in the pipeline" >}}
{{< stat value="0" label="estimates" >}}
{{< /stats >}}

## What this project does

Every month I automatically pull official press releases from Vienna Airport and Bratislava Airport and extract passenger numbers, year-over-year change, and capacity. No estimates, no secondary sources — straight from the figures the airports publish themselves.

## Methodology and transparency

The full code is open and public on GitHub: [github.com/KaStihl/vie-bts-tracker](https://github.com/KaStihl/vie-bts-tracker).

Vienna's data is parsed fully automatically. Bratislava's data goes through a short manual check, since its press releases aren't as consistently formatted — accuracy matters more to me than speed.

Questions, observations, or spotted an error in the data? Write to me.
