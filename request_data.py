import json
import requests

url = 'https://api.fda.gov/drug/label.json?' #search=openfda.generic_name:"amlodipine"
drugs = ['atorvastatin', 'levothyroxine', 'metformin', 'lisinopril', 'amlodipine', 'metoprolol', 'albuterol', 'omeprazole', 'losartan', 'gabapentin', 'hydrochlorothiazide', 'sertraline', 'simvastatin', 'montelukast', 'escitalopram', 'hydrocodone bitartrate and acetaminophen', 'rosuvastatin', 'bupropion', 'furosemide', 'pantoprazole', 'trazodone', 'dextroamphetamine saccharate, amphetamine aspartate, dextroamphetamine sulfate, amphetamine sulfate', 'fluticasone', 'tamsulosin', 'fluoxetine', 'carvedilol', 'duloxetine', 'meloxicam', 'clopidogrel', 'prednisone', 'citalopram', 'insulin glargine', 'potassium chloride', 'pravastatin', 'tramadol', 'aspirin (OTC)', 'alprazolam', 'ibuprofen (OTC)', 'cyclobenzaprine', 'amoxicillin', 'methylphenidate', 'allopurinol', 'venlafaxine', 'clonazepam', 'norethindrone and ethinyl estradiol', 'ergocalciferol', 'zolpidem', 'apixaban', 'glipizide', 'lisinopril and hydrochlorothiazide']
#list contains top 50 drugs including a few OTCs

SECTIONS = [ #different sections I need to look at that are very important
    "indications_and_usage",
    "dosage_and_administration",
    "contraindications",
    "warnings_and_cautions",
    "drug_interactions",
    "adverse_reactions",
    "use_in_specific_populations",
]

def get_data():
    dataset = []
    for drug in drugs: 
        try: 
            data = requests.get(f'{url}search=openfda.generic_name:"{drug}"&limit=1').json()
            dataset.append(data)
        except:
            print(drug, "did not go through.**********************")
    return dataset

print(get_data()[0])


