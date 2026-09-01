with open('app/services/document_service.py', 'r') as f:
    content = f.read()
content = content.replace('"revision": doc.revision,\n    )', '"revision": doc.revision,\n    }')
with open('app/services/document_service.py', 'w') as f:
    f.write(content)
