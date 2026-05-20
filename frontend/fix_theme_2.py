import re

file_path = 'lib/screens/results_screen.dart'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Make sure we have inal theme = Theme.of(context); in build
if 'final theme = Theme.of(context);' not in content.split('Widget build(BuildContext context) {')[1].split('return Scaffold')[0]:
    content = content.replace('Widget build(BuildContext context) {', 'Widget build(BuildContext context) {\n    final theme = Theme.of(context);')

content = content.replace('Color(0xFFF3F0FF)', 'theme.colorScheme.surface')
content = content.replace('theme.colorScheme.surface.withValues', 'theme.colorScheme.surfaceContainerHighest.withValues')
# Actually Colors.white was replaced by theme.colorScheme.surface. If it has .withValues on it, it should probably be surface. 

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
