# Hugging Face Spaces (Docker SDK) image for the Metro Cebu valuation app.
# One process serves the static frontend at / and the FastAPI inference at /api,
# on port 7860 (the HF Spaces default declared in README.md).
FROM python:3.12-slim

ENV WEBAPP_API=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

# Minimal thesis subtree (lib + deployed models + ABT + LGU boundaries + built
# frontend). The directory layout is preserved so the library's relative paths
# resolve unchanged inside the container.
COPY thesis_main/ ./thesis_main/

EXPOSE 7860

# main.py sets WEBAPP_API and adds thesis_main/app to sys.path; --app-dir lets
# uvicorn import it as `main`. Static dist is mounted by main.py when present.
CMD ["uvicorn", "main:app", "--app-dir", "thesis_main/webapp/api", "--host", "0.0.0.0", "--port", "7860"]
