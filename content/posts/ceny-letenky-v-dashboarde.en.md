---
title: "Airfares in the dashboard: what I added and what came out"
date: 2026-11-11
draft: false
description: "Passenger counts can't tell whether low-cost airlines made tickets cheaper. I added Eurostat's airfare price index to the report: how it works, why it is noisy and what it shows for September 2026."
tags: ["Power BI", "airfares", "Eurostat", "data visualization", "VIE", "BTS"]
ShowToc: false
ShowReadingTime: true
---

{{< stats >}}
{{< stat value="−55.8" suffix=" %" label="airfares in Slovakia, September 2026 (year over year)" >}}
{{< stat value="+12" suffix=" %" label="airfares in Austria, September 2026 (year over year)" >}}
{{< stat value="+5.6" suffix=" %" label="EU average, September 2026 (year over year)" >}}
{{< /stats >}}

For a long time the report only answered "how many people fly". When low-cost airlines moved capacity from Vienna to Bratislava, a second question came up: **did tickets get cheaper?** Passenger counts can't say. So I added a new page to the report: **Prices**.

## Where the numbers come from

The source is Eurostat: the harmonised index of consumer prices (HICP), item "Passenger transport by air". Every month it says by how many percent air tickets are more or less expensive than in the same month a year earlier, for each EU country. I collect Slovakia, Austria, Czechia, Hungary, Belgium and the EU average.

I checked them against another source: a press article quoting Eurostat gave −53.0 %, −48.2 % and −45.1 % for Slovakia in April to June 2026. The Eurostat data match to the tenth of a percent.

## How it works in the pipeline

- A Python scraper downloads the data from Eurostat's public API and stores it in a Supabase table, like all the other data.
- Power BI reads it through the same public, read-only interface.
- The table creates itself on the first run. Until then the page is simply empty and nothing fails.

## Three design decisions

1. **A three-month average next to the latest month.** The index is very volatile. Slovakia moved between −23 % and +40 % during 2025, and Belgium jumped from +43 % in March 2026 to −4 % in September. One month proves nothing; a run of three months does.
2. **No red and no green.** A lower price is good for the traveller and bad for the airline, so colour must not judge anything. Slovakia and Austria keep their airports' colours, and the EU average is a neutral grey.
3. **Text that doesn't assume a cause.** Under the chart it says that the index covers prices in a country's consumer basket, not flights from one airport, and that a fall does not prove its cause.

## What September 2026 shows

| | September | Last three months (average) |
|---|---|---|
| Slovakia | −55.8 % | −53.5 % |
| Austria | +12.0 % | +11.5 % |
| EU average | +5.6 % | +2.6 % |

Slovak tickets are more than half as expensive as a year ago, while Austrian ones cost 12 % more. That fits the move of low-cost routes, but the index alone doesn't prove it: flight and passenger counts speak about the move. And prices can move for other reasons too (fuel, demand, season).

<!-- ![The Prices page of the report](/images/vie-bts/prices.png) -->

## Behind the scenes

Testing turned up two bugs nobody would notice at first glance. Vienna's "versus previous release" card compared August from the airport's figures with July from Eurostat (which counts 1 to 3 % higher), so it showed +0.3 % instead of the real +12 %. And an unneeded Eurostat column slipped into the model through the connection. Both fixes are in the repository, with tests.

{{< cta text="See the live dashboard" url="/dashboard/" >}}
