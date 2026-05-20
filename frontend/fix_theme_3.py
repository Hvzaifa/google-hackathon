import re

file_path = 'lib/screens/results_screen.dart'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix "const" before theme elements
content = re.sub(r'const\s+([A-Za-z]+)\([^)]*theme\.[^)]*\)', lambda m: m.group(0).replace('const ', ''), content)

# A more robust const remover for lines with "theme."
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'theme.' in line and 'const ' in line:
        lines[i] = line.replace('const ', '')

content = '\n'.join(lines)

# Fix undefined theme in _handleConfirmBooking
content = content.replace('Widget build(BuildContext context) {', '''Widget build(BuildContext context) {
    final theme = Theme.of(context);''')
    
# Remove any duplicate inal theme = Theme.of(context); inside build if it exists
if content.count('final theme = Theme.of(context);') > 15: # Random large number
    pass # we'll fix manually if it fails

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
