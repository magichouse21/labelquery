import json
import os

import requests
import ollama

EMBEDDING_MODEL = 'hf.co/CompendiumLabs/bge-base-en-v1.5-gguf'
LANGUAGE_MODEL = 'hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF'
URL = 'https://api.fda.gov/drug/label.json'
CACHE_FILE = 'embeddings_cache.json'

# roughly 1000 characters per chunk with a little overlap so a sentence
# split across a boundary still shows up whole in one of the two chunks
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

drugs = [
    "tadalafil", "phentermine", "sildenafil", "amlodipine", "atorvastatin",
    "lisinopril", "hydrocodone", "levothyroxine", "escitalopram", "fluoxetine",
    "losartan", "sertraline", "gabapentin", "amoxicillin", "benzonatate",
    "pantoprazole", "omeprazole", "rosuvastatin", "dextroamphetamine",
    "metoprolol succinate", "vitamin d", "metformin", "prednisone", "bupropion",
    "albuterol", "ibuprofen", "finasteride", "zolpidem", "cyclobenzaprine",
    "trazodone", "estradiol", "famotidine", "ondansetron", "alprazolam",
    "azithromycin", "tretinoin", "doxycycline", "hydrochlorothiazide",
    "cephalexin", "hydroxyzine", "folic acid", "methylprednisolone",
    "spironolactone", "valacyclovir", "meloxicam", "progesterone", "tamsulosin",
    "methocarbamol", "duloxetine", "venlafaxine",
]

SECTIONS = [
    "indications_and_usage",
    "dosage_and_administration",
    "contraindications",
    "boxed_warning",
    "drug_interactions",
    "adverse_reactions",
    "use_in_specific_populations",
]

MISSING = ["N/A"]


def parse_drug_label(drug_name):
    """Fetch one drug's label. Returns a {section: [text, ...]} dict, or None."""
    try:
        response = requests.get(
            URL,
            params={'search': f'openfda.generic_name:"{drug_name}"', 'limit': 1},
            timeout=20,
        )
        response.raise_for_status()
        result = response.json()["results"][0]
    except (requests.RequestException, ValueError, KeyError, IndexError):
        print("No data found for:", drug_name)
        return None

    return {section: result.get(section, MISSING) for section in SECTIONS}


def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split a long string into overlapping windows."""
    if len(text) <= size:
        return [text]

    chunks = []
    start = 0
    step = size - overlap
    while start < len(text):
        chunks.append(text[start:start + size])
        start += step
    return chunks


def embed_drug(drug_name, sections):
    """Turn one drug's sections into a list of embedded chunk records."""
    records = []

    for section, content in sections.items():
        if not content or content == MISSING:
            continue

        body = ' '.join(content)
        for piece in chunk_text(body):
            # the drug and section names go in the embedded text so a query
            # like "sertraline side effects" can match on them directly
            text = f"{drug_name} {section}: {piece}"
            response = ollama.embed(model=EMBEDDING_MODEL, input=text)
            records.append({
                "drug": drug_name,
                "section": section,
                "text": text,
                "embedding": response["embeddings"][0],
            })

    return records


def build_index():
    """Embed every drug label, or load a previously built index from disk."""
    if os.path.exists(CACHE_FILE):
        print("Loading cached embeddings...")
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    embedded_data = []
    for drug in drugs:
        print("Embedding:", drug)
        sections = parse_drug_label(drug)
        if not sections:
            continue
        embedded_data.extend(embed_drug(drug, sections))

    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(embedded_data, f)

    print(f"Indexed {len(embedded_data)} chunks.")
    return embedded_data


def cosine_similarity(a, b):
    if len(a) != len(b):
        raise ValueError(f"Dimension mismatch: {len(a)} vs {len(b)}")

    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x ** 2 for x in a) ** 0.5
    norm_b = sum(x ** 2 for x in b) ** 0.5

    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


def retrieve(data, query, top_n=3):
    query_embedding = ollama.embed(model=EMBEDDING_MODEL, input=query)['embeddings'][0]

    scored = [
        (item["drug"], item["section"], item["text"],
         cosine_similarity(query_embedding, item["embedding"]))
        for item in data
    ]
    scored.sort(key=lambda x: x[3], reverse=True)
    return scored[:top_n]


def main():
    embedded_data = build_index()
    if not embedded_data:
        print("Nothing indexed, exiting.")
        return

    input_query = input('Ask me a question: ')
    retrieved_knowledge = retrieve(embedded_data, input_query)

    print('\nRetrieved knowledge:')
    for drug, section, text, score in retrieved_knowledge:
        preview = text[:200].replace('\n', ' ')
        print(f' - (similarity: {score:.2f}) [{drug} / {section}] {preview}...')

    # built outside the f-string: backslashes in f-string expressions are a
    # SyntaxError before Python 3.12
    context = '\n'.join(f' - {text}' for _, _, text, _ in retrieved_knowledge)

    instruction_prompt = f'''You are a helpful chatbot.
Use only the following pieces of context to answer the question. Don't make up any new information:
{context}
'''

    stream = ollama.chat(
        model=LANGUAGE_MODEL,
        messages=[
            {'role': 'system', 'content': instruction_prompt},
            {'role': 'user', 'content': input_query},
        ],
        stream=True,
    )

    print('\nChatbot response:')
    for chunk in stream:
        print(chunk['message']['content'], end='', flush=True)
    print()

main()