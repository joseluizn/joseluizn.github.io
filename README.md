# José Luiz Nunes — Academic Website

Personal academic website built with [Astro](https://astro.build/).

## Development

```sh
npm install
npm run dev       # Start dev server at http://localhost:4321
npm run build     # Build static site to ./dist
npm run preview   # Preview the build locally
```

## Updating Publications

The publication list is stored in `src/data/publications.json` and rendered by `src/pages/publications.astro`.

To regenerate from Google Scholar using the SerpAPI:

```sh
export SERPAPI_KEY="your-api-key"
pip install -r requirements.txt
python code/generate_publication.py
```

## Deployment

Automatically deployed to GitHub Pages via GitHub Actions on push to `main`.
