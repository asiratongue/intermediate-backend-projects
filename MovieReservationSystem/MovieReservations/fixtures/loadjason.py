import json

# Read the file in binary mode
with open('test_fixtures.json', 'rb') as file:
    content = file.read()
    
# Try different encodings if UTF-8 fails
try:
    decoded = content.decode('utf-8-sig')  # Handles BOM
except UnicodeDecodeError:
    try:
        decoded = content.decode('utf-16')
    except UnicodeDecodeError:
        decoded = content.decode('latin-1')

# Write back as proper UTF-8
with open('test_fixtures.json', 'w', encoding='utf-8') as file:
    json.dump(json.loads(decoded), file, ensure_ascii=False, indent=2)
    print("dumped successfully")