# AI Research Paper Assistant

Streamlit app to upload research PDFs, extract text/tables, summarize with NLP models, and (optionally) run **RAG-style retrieval** over the PDF using either:

- **FAISS (local, in-memory)** — default
- **Postgres + pgvector (persistent, DBaaS-friendly)** — set `VECTOR_BACKEND=pgvector`

## Cloud service models (how this project “covers” them)

- **SaaS**: This Streamlit web app is the *software* users interact with (the “product” layer).
- **DBaaS**: Use a managed Postgres provider (Neon/Supabase/AWS RDS/Azure Database for PostgreSQL, etc.) and set `DATABASE_URL`. The app creates a **`users`** table for **registration / login** (passwords are hashed). With `VECTOR_BACKEND=pgvector`, PDF chunks + embeddings are stored in Postgres too.
- **PaaS**: Deploy the container/app to a managed platform (Render/Fly.io/Azure App Service/Google Cloud Run/etc.). The platform runs your app and handles scaling/HTTPS.
- **IaaS**: Run the same container (or python process) on a VM you manage (AWS EC2/Azure VM/GCE). You handle OS patches, firewall, process manager, etc.

## Run locally (no DB)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Without `DATABASE_URL`, the app does **not** require sign-in. With `DATABASE_URL` (e.g. Supabase), you get **Log in** and **Register** tabs first; accounts are saved in Postgres.

## Authentication (Supabase / any Postgres)

1. Set `DATABASE_URL` (SQLAlchemy URI), e.g. `postgresql+psycopg2://...?sslmode=require` for Supabase.
2. On first register or login, the app creates the **`users`** table if needed (passwords are hashed; plain passwords are never stored).
3. Enable the `vector` extension only if you use `VECTOR_BACKEND=pgvector` (see below).
4. Optional: `SKIP_AUTH=1` skips the gate for local demos only (not for production).

**Supabase + `public.users` missing:** The transaction pooler (often port **6543**) may not create tables reliably. Either run **`scripts/create_users_table.sql`** once in **Supabase → SQL Editor**, or put the **direct** Postgres URL (port **5432**) in `DATABASE_URL` for local development.

## Run locally with “DBaaS-style” persistence (Docker + Postgres/pgvector)

```bash
docker compose up --build
```

Open the app at `http://localhost:8501`.

## Enable pgvector on a managed Postgres (DBaaS)

1. Provision Postgres (Neon/Supabase/RDS/etc.)
2. Enable the `vector` extension (provider UI or SQL):

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

3. Set environment variables:

- `VECTOR_BACKEND=pgvector`
- `DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST:5432/DBNAME` (add `?sslmode=require` on Supabase if needed)

## PaaS deployment (recommended)

Deploy as a container (Cloud Run / Render / Fly.io / App Service):

- Build from `Dockerfile`
- Expose port **8501**
- Configure env vars:
  - `VECTOR_BACKEND=faiss` (simplest) **or** `pgvector` (persistent)
  - `DATABASE_URL=...` (required for **login/register**; also required if using `pgvector`)

Pair with DBaaS Postgres for persistence.

## IaaS deployment (VM)

On a VM (Ubuntu example):

- Install Docker
- Copy project to the VM
- Run `docker compose up --build`
- Open firewall for port **8501** (or put Nginx in front and serve via 443)

## Notes

- If you use `VECTOR_BACKEND=pgvector`, the “Ask (RAG)” tab stores PDF chunks/embeddings in Postgres so retrieval survives app restarts.

## Deploy (you can deploy now)

**Order:** Almost every free host needs your code on **GitHub** first (**push**), then you connect the repo in the host’s UI. Deploying **before** a successful push only works if you use **Docker on your own machine/VM** or a CLI like **Fly.io** from a local folder.

### Option A — Streamlit Community Cloud (simplest UI)

1. Push the repo to **GitHub** (keep **`.env` out of git**; use `.gitignore` for `.env`).
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app** → pick repo, main file **`app.py`**.
3. Under **App settings → Secrets**, paste TOML like `.streamlit/secrets.toml.example` with your real **`DATABASE_URL`** (and optional `VECTOR_BACKEND`).
4. **Advanced settings**: Python **3.11** if offered; first boot may take **several minutes** (`torch` / `sentence-transformers` are large; free tier may be tight on RAM).

The app copies **`st.secrets`** into **`os.environ`** at startup so **`DATABASE_URL`** works the same as locally.

### Option B — Docker on a PaaS (Render, Fly.io, Railway, Azure, etc.)

1. Build from the repo **`Dockerfile`** (port **8501**).
2. Set environment variables on the platform (**`DATABASE_URL`**, optional **`VECTOR_BACKEND`**, **`SKIP_AUTH`** not recommended in production).
3. Ensure **`scripts/create_users_table.sql`** has been run on Supabase if the pooler blocks DDL.

### Option C — Your own VM (IaaS)

1. Install Docker on the VM, copy the project, run **`docker compose up --build`** or **`docker run -p 8501:8501 -e DATABASE_URL=...`** from the built image.
2. Open firewall / reverse proxy for HTTPS as needed.

### Before go-live checklist

- [ ] Supabase: run **`scripts/create_users_table.sql`** (and `create extension vector` if using **`pgvector`**).
- [ ] **`DATABASE_URL`** uses **`postgresql+psycopg2://`** and **`?sslmode=require`** if required.
- [ ] Never commit **`.env`** or Streamlit secrets with real passwords.

