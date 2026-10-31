# Optional thumbnail photos

The app works without any photos (it draws a colored placeholder from each post title).
Real thumbnails make the demo look better AND let Gemma analyse the image (Gemma 4 is multimodal).

**Where to put them:** `app/static/thumbs/`
**File name:** `<post_id>.jpg` (or `.png` / `.webp`), for example `app/static/thumbs/yt_zain_p1.jpg`
**Size:** 16:9 works best (e.g. 1280x720), under 1 MB each. No restart needed.

Accounts you add in the UI get generated post ids like `ig_yourhandle_p1` ... `ig_yourhandle_p5`; the same rule applies.

## Post ids of the 6 built-in demo accounts

- `yt_zain_p1`
- `yt_zain_p2`
- `yt_zain_p3`
- `yt_zain_p4`
- `yt_zain_p5`
- `yt_desi_p1`
- `yt_desi_p2`
- `yt_desi_p3`
- `yt_desi_p4`
- `yt_desi_p5`
- `ig_hira_p1`
- `ig_hira_p2`
- `ig_hira_p3`
- `ig_hira_p4`
- `ig_hira_p5`
- `ig_pindi_p1`
- `ig_pindi_p2`
- `ig_pindi_p3`
- `ig_pindi_p4`
- `ig_pindi_p5`
- `fb_cricket_p1`
- `fb_cricket_p2`
- `fb_cricket_p3`
- `fb_cricket_p4`
- `fb_cricket_p5`
- `fb_startup_p1`
- `fb_startup_p2`
- `fb_startup_p3`
- `fb_startup_p4`
- `fb_startup_p5`
