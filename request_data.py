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
    dataset = {}
    temp = {}
    drug = "atorvastatin"
#    for drug in drugs: 
    
    data = requests.get(f'{url}search=openfda.generic_name:"{drug}"&limit=1').json()
    for s in range (0, len(SECTIONS)):
        temp.add[data["results"][0][SECTIONS[s]]]
    dataset.append(temp)
    temp = {}
    
    return dataset


print(get_data())


