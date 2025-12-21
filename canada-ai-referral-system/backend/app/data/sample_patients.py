"""Sample patients dataset for local development.
Each entry is a dict matching the patient shape returned by `/api/dashboard/patients`.
Generated deterministically for reproducibility.
"""
patients = [
]

def _make_patient(i):
    # Cycle through some diseases and provinces
    diseases = ['Cardiology', 'Orthopedics', 'Neurology', 'Respiratory', 'Gastroenterology']
    provinces = ['ON', 'BC', 'AB', 'QC', 'NS']
    priorities = ['High','Medium','Low']
    base_age = 20 + (i % 70)
    disease = diseases[i % len(diseases)]
    province = provinces[i % len(provinces)]
    priority = priorities[i % len(priorities)]
    return {
        'id': f'p{i+1}',
        'name': f'Patient {i+1}',
        'age': base_age,
        'priority': priority,
        'province': province,
        'notes': f'Sample notes for patient {i+1} ({disease})',
        'disease': disease
    }

for idx in range(50):
    patients.append(_make_patient(idx))

detail_map = {}
for p in patients:
    detail_map[p['id']] = {
        'id': p['id'],
        'name': p['name'],
        'age': p['age'],
        'priority': p['priority'],
        'province': p['province'],
        'notes': p['notes'],
        'details': {
            'dob': f'19{50 + (int(p["id"].lstrip("p")) % 50):02d}-01-01',
            'postal': f'A1A1A{(int(p["id"].lstrip("p"))%10)}',
            'contact': f'555-{1000 + int(p["id"].lstrip("p"))}',
            'medical_history': 'None documented' if (int(p['id'].lstrip('p')) % 3) else 'Hypertension'
        }
    }
