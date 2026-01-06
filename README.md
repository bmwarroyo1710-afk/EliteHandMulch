# Elite Hand Mulch — Invoice App

Quick steps to set up and run the Streamlit invoice app in this workspace.

1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. Run the app

```bash
streamlit run invoice_app.py
```

The app will open at http://localhost:8501 by default.

If you add or change dependencies, regenerate `requirements.txt` with:

```bash
pip freeze > requirements.txt
```

## Deploy to Streamlit Community Cloud

1. Push this repository to GitHub (ensure `requirements.txt` is committed).

```bash
git add .
git commit -m "Prepare repo for Streamlit deployment"
git push origin main
```

2. On https://share.streamlit.io connect your GitHub account and choose this repository.
3. Select branch `main` and set the start file to `invoice_app.py`.
4. Streamlit will build the app automatically using `requirements.txt`. Visit the URL provided by Streamlit after deployment.

If you want, I can help push the repo to GitHub or add a `Dockerfile`/CI for other hosts.
