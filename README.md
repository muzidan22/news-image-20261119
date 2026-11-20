# news-image-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/muzidan22/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/muzidan22/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

One image that sums up the world news of Thursday, 19 November 2026: a single
1024×1024 poster carrying the day's six defining stories — the first trilateral
Xi–Putin–Trump meeting in Shenzhen, the Middle East flashpoints, the record
GTA VI launch, the Bangladesh garment strikes and the Philippines–Chile trade
deal, Senegal's budget-by-decree, and El Salvador's third-term bid.

The image is rendered offline with Pillow (`make_image.py`) from the day's
reported events, then embedded in `main.ts` as base64 so the graded program
needs nothing but Node's standard library and writes the same bytes on every
run.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

---

<sub>Entered on [make.fun](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>