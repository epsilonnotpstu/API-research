from jsonschema import Draft202012Validator

schema = {
    "type": "object",
    "properties": {
        "name":       {"type": "string", "minLength": 1},
        "age":        {"type": "integer", "minimum": 16},
        "department": {"type": "string", "enum": ["CSE", "EEE", "ME"]},
        "studentId":  {"type": "string", "pattern": "^[0-9]{7}$"},
        "email": {"type":"string", "format":"email"},
        "skills": {
            "type": "array",
            "items": {"type": "string"},
            "uniqueItems": True
        }
    },
    "required": ["name", "age", "studentId"]
}

test_cases = {
    "valid":           {"name": "Afridi", "age": 24, "studentId": "2102027"},
    "age_as_string":   {"name": "Afridi", "age":  '24', "studentId": "2102027"},
    "missing_id":      {"name": "Afridi", "age": 24},
    "bad_department":  {"name": "Afridi", "age": 24, "studentId": "2102027", "department": "cse"},
    "short_id":        {"name": "Afridi", "age": 24, "studentId": "21020"},
    "duplicate_skill": {"name": "Afridi", "age": 24, "studentId": "2102027", "skills": ["C", "C"]},
    "empty_name":      {"name": "", "age": 24, "studentId": "2102027"},
    "email_cheek":     {"name": "Afridi", "age": 24, "studentId": "2102027","email":"not_valied"},
}

validator = Draft202012Validator(schema)

for label, data in test_cases.items():
    errors = list(validator.iter_errors(data))
    if not errors:
        print(f"✅ {label}: valid")
    else:
        for e in errors:
            path = "/".join(str(p) for p in e.path) or "(root)"
            print(f"❌ {label}: [{path}] {e.message}")