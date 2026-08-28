# 100% FREE Cloud Deployment Guide ($0/month, No Credit Card Required)

This guide shows you how to host your **Enterprise Multi-Vector Hybrid RAG Search Engine** completely **FREE** using:
1. **Vercel** (Free): For hosting the React Frontend.
2. **Render (Free Tier) or Hugging Face Spaces (Free)**: For hosting the Python FastAPI Backend API.
3. **Supabase or Neon.tech** (Free): For managed PostgreSQL with pre-installed `pgvector` extension.
4. **Built-in Async Background Engine** ($0): Uses FastAPI `BackgroundTasks` (No paid Redis or Celery worker required!).

---

## 🏗️ 100% Free Architecture Overview

```
                      ┌─────────────────────────────────┐
                      │    Vercel (Free CDN Hosting)    │
                      │   React 18 + Vite Web App       │
                      └────────────────┬────────────────┘
                                       │
                          HTTPS Calls /api/v1/query
                                       │
                                       ▼
                      ┌─────────────────────────────────┐
                      │ Render Free Web Service (Python)│
                      │ FastAPI + Async BackgroundTasks │
                      └────────────────┬────────────────┘
                                       │
                        SQL Queries / pgvector
                                       │
                                       ▼
                      ┌─────────────────────────────────┐
                      │   Supabase / Neon (Free Tier)   │
                      │    PostgreSQL + pgvector DB     │
                      └─────────────────────────────────┘
```

---

## Step 1: Create a Free PostgreSQL + `pgvector` Database ($0)

### Option A: Supabase (Recommended — Free Forever)
1. Sign up for free at [Supabase.com](https://supabase.com/).
2. Click **New Project** -> name it `hybrid-rag` and set a database password.
3. In the Supabase Dashboard, click **SQL Editor** on the left menu, paste the following SQL, and click **Run**:
   ```sql
   -- Enable pgvector and uuid extensions
   CREATE EXTENSION IF NOT EXISTS vector;
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

   -- Create Documents Table
   CREATE TABLE IF NOT EXISTS documents (
       id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
       filename VARCHAR(255) NOT NULL,
       mime_type VARCHAR(100) NOT NULL,
       file_size_bytes BIGINT NOT NULL,
       global_context TEXT,
       uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
       processing_status VARCHAR(50) DEFAULT 'PENDING',
       error_message TEXT
   );

   -- Create Document Chunks Table
   CREATE TABLE IF NOT EXISTS document_chunks (
       id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
       document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
       chunk_index INT NOT NULL,
       raw_content TEXT NOT NULL,
       contextualized_content TEXT NOT NULL,
       dense_embedding vector(768),
       metadata JSONB DEFAULT '{}'::jsonb,
       tsv_content tsvector
   );

   CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON document_chunks(document_id);
   ```
4. Go to **Project Settings** -> **Database** -> Copy your **URI Connection String** (e.g., `postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres`).

---

## Step 2: Deploy Backend API on Render (Free Web Service — $0)

1. Sign up for free at [Render.com](https://render.com/).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Fill in the deployment details:
   - **Name**: `enterprise-rag-api`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Select **Free** ($0/mo)
5. Add **Environment Variables** under the **Environment** tab:
   - `DATABASE_URL`: Your Supabase connection string from Step 1.
   - `USE_CELERY`: `False` *(Uses built-in FastAPI Async Background Tasks for 100% free document ingestion!)*
   - `GEMINI_API_KEY`: Your Google Gemini API key.
   - `CORS_ORIGINS`: `*` (or your Vercel URL).
6. Click **Create Web Service**.
7. Copy your backend URL: `https://enterprise-rag-api.onrender.com`.

---

## Step 3: Deploy Frontend on Vercel (Free — $0)

1. Sign up for free at [Vercel.com](https://vercel.com/).
2. Click **Add New...** -> **Project** -> Import your GitHub repository.
3. Configure the project settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add **Environment Variable**:
   - `VITE_API_BASE_URL`: `https://enterprise-rag-api.onrender.com/api/v1`
5. Click **Deploy**.

---

## 🎉 Done! Your App is Live for $0/month

- **Frontend Application**: `https://your-app.vercel.app`
- **Backend API Docs**: `https://enterprise-rag-api.onrender.com/docs`
- **Total Cost**: **$0.00 / month forever**
