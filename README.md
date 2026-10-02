# FK's Lab

Source for [fkslab.com](https://fkslab.com/) — a personal site for data projects built on the side of a full-time job: Power BI dashboards, automation, and analytics.

The current showcase is the **[VIE/BTS Aviation Tracker](https://fkslab.com/projekty/vie-bts-tracker/)**, which tracks how Vienna and Bratislava airports are trading passengers after Austria introduced an aviation tax in 2026. Every number comes straight from official airport press releases and [OpenSky Network](https://opensky-network.org) flight data — no estimates. The data pipeline behind it lives in a separate repo: [KaStihl/vie-bts-tracker](https://github.com/KaStihl/vie-bts-tracker).

## Built with

- [Hugo](https://gohugo.io/) — static site generator
- [PaperMod](https://github.com/adityatelange/hugo-PaperMod) theme (as a git submodule)
- Custom shortcodes for a Power BI dashboard embed, stat tiles, service cards, and a Netlify-powered contact form
- Deployed on [Netlify](https://www.netlify.com/)

## Languages

The site is fully trilingual — Slovak (default), English, and German — with every page and menu translated.

## Local development

Clone with submodules, since the theme is pulled in as one:

```bash
git clone --recurse-submodules https://github.com/KaStihl/fkslab-blog.git
cd fkslab-blog
```

If you already cloned without `--recurse-submodules`:

```bash
git submodule update --init --recursive
```

Then run the Hugo dev server:

```bash
hugo server -D
```

The site will be available at `http://localhost:1313/`.

## Project structure

```
content/       Page content, per language (.sk.md / .en.md / .de.md)
layouts/       Custom partials and shortcodes on top of PaperMod
static/        Images, logos, favicons
i18n/          UI string translations
hugo.toml      Site configuration, languages, and menus
```

## Contact

Questions, feedback, or spotted an error in the dashboard data? Reach out via the [contact page](https://fkslab.com/contact/) or [ferdinand.fojtlin@gmail.com](mailto:ferdinand.fojtlin@gmail.com).
