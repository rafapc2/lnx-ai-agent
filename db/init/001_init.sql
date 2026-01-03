-- Enable pgvector (already installed in the image, but extension needs to be created per DB)
CREATE EXTENSION IF NOT EXISTS vector;

-- Snapshots (versioned)
CREATE TABLE IF NOT EXISTS initiative_snapshots (
  id              BIGSERIAL PRIMARY KEY,
  initiative_id   TEXT NOT NULL,
  snapshot        JSONB NOT NULL,
  quality         JSONB NOT NULL,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_initiative_snapshots_initiative_id
  ON initiative_snapshots(initiative_id);

CREATE INDEX IF NOT EXISTS idx_initiative_snapshots_created_at
  ON initiative_snapshots(created_at);

-- (Opcional) tabla para documentos RAG (si luego quieres indexar contenido)
CREATE TABLE IF NOT EXISTS rag_documents (
  id          BIGSERIAL PRIMARY KEY,
  source      TEXT NOT NULL,
  doc_id      TEXT NOT NULL,
  chunk_id    TEXT NOT NULL,
  content     TEXT NOT NULL,
  metadata    JSONB NOT NULL DEFAULT '{}'::jsonb,
  embedding   vector(1536)  -- ajusta a tu modelo de embeddings
);

CREATE INDEX IF NOT EXISTS idx_rag_documents_source_doc
  ON rag_documents(source, doc_id);
