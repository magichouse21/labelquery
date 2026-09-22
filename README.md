# rxcite

A retrieval-augmented generation (RAG) pipeline that answers drug information
questions from FDA labels and shows which label section each answer came from.

**Stack:** Python · Ollama · bge-base-en-v1.5 (embeddings) · Llama 3.2 (generation) · openFDA API

## What it can answer

- **Side effects** — "What are the common side effects of sertraline?"
- **Dosing** — "What's the typical starting dose of lisinopril?"
- **Boxed warnings** — "Does fluoxetine have a boxed warning?"
- **Interactions and contraindications** — "Who shouldn't take metformin?"

Answers are drawn only from the retrieved label text, covering 50 commonly
prescribed drugs.

## Limitations

This is a retrieval tool for finding information in FDA labels, not clinical
decision support. It does not replace a pharmacist or prescriber.