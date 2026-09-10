import json
import requests
import ollama

url = 'https://api.fda.gov/drug/label.json?' #pulls data from 
drugs = ["tadalafil", "phentermine", "sildenafil", "amlodipine", "atorvastatin", "lisinopril", "hydrocodone", "levothyroxine", "escitalopram", "fluoxetine", "losartan", "sertraline", "gabapentin", "amoxicillin", "benzonatate", "pantoprazole", "omeprazole", "rosuvastatin", "dextroamphetamine", "metoprolol succinate", "vitamin d", "metformin", "prednisone", "bupropion", "albuterol", "ibuprofen", "finasteride", "zolpidem", "cyclobenzaprine", "trazodone", "estradiol", "famotidine", "ondansetron", "alprazolam", "azithromycin", "tretinoin", "doxycycline", "hydrochlorothiazide", "cephalexin", "hydroxyzine", "folic acid", "methylprednisolone", "spironolactone", "valacyclovir", "meloxicam", "progesterone", "tamsulosin", "methocarbamol", "duloxetine", "venlafaxine"]
#list contains top 50 drugs                                                                     

SECTIONS = [ #different sections I need to look at that are very important
    "indications_and_usage",
    "dosage_and_administration",
    "contraindications",
    "boxed_warning",
    "drug_interactions",
    "adverse_reactions",
    "use_in_specific_populations",
]

def parse_drug_label(drug_name):  #pulls the data for a specific drug
    data = requests.get(f'{url}search=openfda.generic_name:"{drug_name}"').json()
    try: 
        result = data["results"][0]
        return {
                drug_name: {
                    section: result.get(section, ["N/A"]) for section in SECTIONS
                }
            }
    except (KeyError, IndexError):
        print("No Data Found for:", drug_name)
        return {drug_name: None}  # None is easier to check than ["N/A"]

def embed_drug(drug_name, sections):
    embeddings = []
    
    for section, content in sections.items():
        if content is None:
            continue
        
        # flatten the list to a string
        text = f"{drug_name} {section}: {' '.join(content)}"
        
        response = ollama.embed(
            model="nomic-embed-text",  # best embedding model on ollama
            input=text
        )
        
        embeddings.append({
            "drug": drug_name,
            "section": section,
            "text": text,
            "embedding": response["embeddings"][0]
        })
    
    return embeddings

def main():
    embedded_data = []
    for drug in drugs:
        data = parse_drug_label(drug)
        sections = data.get(drug)

        if not sections or isinstance(sections, list):
            continue
        
        embedded_data.append(embed_drug(drug, sections))

main()