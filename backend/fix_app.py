import re
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace FRONTEND_DIR logic
pattern = re.compile(r'FRONTEND_DIR = os\.path\.join\(os\.path\.dirname\(os\.path\.dirname\(__file__\)\), "frontend", "dist"\)\s*if os\.path\.isdir\(FRONTEND_DIR\):', re.DOTALL)

replacement = '''FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")

if True:'''

content = pattern.sub(replacement, content)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated app.py")
