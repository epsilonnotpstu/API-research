from jsonschema import Draft202012Validator

def check(title, schema, cases):
    print(f"── {title} ──")
    v = Draft202012Validator(schema)
    for label, data in cases.items():
        errs = list(v.iter_errors(data))
        if errs:
            print(f"❌ {label}: {errs[0].message[:90]}")
        else:
            print(f"✅ {label}")
    print()

# A. null
check("A. null", {
    "type": "object",
    "properties": {"nickname": {"type": ["string", "null"]}}
}, {
    "string":   {"nickname": "Pranto"},
    "null":     {"nickname": None},
    "missing":  {},
    "number":   {"nickname": 5},
})

# B. additionalProperties
base = {"type": "object", "properties": {"name": {"type": "string"}}}
strict = {**base, "additionalProperties": False}
leak = {"name": "Afridi", "passwordHash": "a9f3...", "isAdmin": True}
check("B1. additionalProperties default", base,   {"leaky_response": leak})
check("B2. additionalProperties false",   strict, {"leaky_response": leak})

# C. oneOf বনাম anyOf ফাঁদ
overlap = [{"type": "number"}, {"type": "integer"}]
check("C1. oneOf",  {"oneOf": overlap}, {"5.5": 5.5, "5": 5})
check("C2. anyOf",  {"anyOf": overlap}, {"5.5": 5.5, "5": 5})

# D. payment oneOf
payment = {"oneOf": [
    {"properties": {"cardNumber": {"type": "string"}}, "required": ["cardNumber"]},
    {"properties": {"phone": {"type": "string"}}, "required": ["phone"]},
]}
check("D. payment", payment, {
    "card_only":  {"cardNumber": "1234"},
    "bkash_only": {"phone": "01700000000"},
    "both":       {"cardNumber": "1234", "phone": "01700000000"},
    "neither":    {"amount": 500},
})

# E. $ref + allOf
check("E. $ref + allOf", {
    "$defs": {
        "Person": {"type": "object",
                   "properties": {"name": {"type": "string"}},
                   "required": ["name"]}
    },
    "allOf": [
        {"$ref": "#/$defs/Person"},
        {"properties": {"studentId": {"type": "string"}}, "required": ["studentId"]}
    ]
}, {
    "full":       {"name": "Afridi", "studentId": "2102027"},
    "no_id":      {"name": "Afridi"},
    "no_name":    {"studentId": "2102027"},
})