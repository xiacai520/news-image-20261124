# news-image-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/xiacai520/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/xiacai520/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

A single 1024×1024 poster that sums up the world news of **24 November 2026** in six
stories: a projectile striking Riyadh's PIF Tower for the second time in a week,
Israeli strikes killing Hamas's security chief in Gaza, a deadly Russian strike
on Zaporizhzhia, global landmine casualties hitting a five-year high, Iran's
rial collapsing to a record low after fresh US sanctions, and Nvidia chief
Jensen Huang apologising to staff a day after his reinstatement as CEO.

## Run it

```sh
python3 main.py
```

The script is pure Python standard library — it ships its own PNG encoder
(`zlib` + `struct`) and its own hand-drawn 5×7 bitmap font, so it needs no
third-party packages and no network access. It writes the poster to
`/output/entry.png` (1024×1024, deterministic: identical bytes on every run).

## The six stories

| # | Story | Source |
|---|-------|--------|
| 01 | Riyadh's PIF Tower hit again; 11 injured, Houthis blamed | Reuters / AFP |
| 02 | Hamas security chief Naeem Abu Nahel killed in Gaza strike | AP / AFP |
| 03 | Russian strike on Zaporizhzhia kills 2, wounds 40 | AP |
| 04 | Landmine casualties hit five-year high: 6,929 in 2025 | ICBL / Al Jazeera |
| 05 | Rial hits record low of 2.82m per dollar after US sanctions | Al Arabiya / Gulf Times |
| 06 | Nvidia's Jensen Huang apologises, says he is in therapy | CNN / WSJ |

---

<sub>Entered on [make.fun](https://make.fun/?ref=noble-panda-29&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>
