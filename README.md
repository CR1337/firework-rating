# Firework Rating

This app scrapes products from [Pyroland](https://pyroland.de) and stores them i a database. The user is then able to inspect the products in detail and to rate them. After rating the user profits from a powerful search engine that enables complex search queries against the database.

## Installation

1. Clone this repository.
```bash
git clone https://github.com/CR1337/firework-rating.git
```

2. `cd` into the directory.
```bash
cd firework-rating
```

3. Create virtual environment and activate it.
```bash
python3 -m venv .venv
source .venv/bin/activate
```

4. Install python dependencies.
```bash
pip3 install -r requirements.txt
```

5. Install node dependencies.
```bash
cd frontend
npm install
cd ..
```

6. Install ffmpeg (for the product videos).
```bash
apt update
apt install ffmpeg
```

## Usage

1. Scrape [Pyroland](https://pyroland.de) to get new products and update already scraped products.
```bash
bin/scrape
```

2. Create product plots. These show product statistics in comparisons to other products.
```bash
bin/create_plots
```

3. Download product videos. This enables playback of highest quality videos. An embedded youtube doesn't play on highest quality. Depending on YouTubes rate limiting the download may get stuck some times. Just restart until all videos are downloaded.
```bash
bin/download_videos
```

4. Start the app.
```bash
bin/run
```

5. Open the app at [http://localhost:5173](http://localhost:5173).