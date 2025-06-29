# Static Export Guide

This project includes utilities to generate a static version of the Flask site for deployment on services like Netlify.

## Requirements

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Exporting the Site

Run the export script from the repository root:

```bash
python export_static.py
```

This will create a `static_export/` folder containing HTML files and a copy of the `static/` directory. Any binary files (e.g. videos) are moved to `static_export/bin/` and references inside the pages are updated automatically.

If a route contains a form, the script will warn that form submissions will not work in the static build.

## Testing the Export

After exporting, verify the output with:

```bash
python test_static_export.py
```

The tests ensure that all routes render, asset links resolve, and binary files are correctly placed.

## Deploying to Netlify

Upload the contents of `static_export/` directly to Netlify. The site will work without running a Flask server.

