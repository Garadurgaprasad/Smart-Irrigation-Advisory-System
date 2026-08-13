import re
with open('requirements.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

lines = [l for l in lines if 'firebase-functions' not in l]

with open('requirements.txt', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Updated requirements.txt")
