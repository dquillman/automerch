#!/usr/bin/env python3
"""Script to add version display to all HTML pages."""

import re
from pathlib import Path

# Find all HTML files in automerch/ui
ui_dir = Path(__file__).parent / "automerch" / "ui"
html_files = list(ui_dir.rglob("*.html"))

# Version span to add (before dark mode button)
version_span = """            <div style="display: flex; align-items: center; gap: 16px;">
                <span style="color: #999; font-size: 12px; opacity: 0.7;">v<span id="app-version">-</span></span>
                <button onclick="toggleDarkMode()" id="dark-toggle" style="background: #495057; color: #fff; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">🌙 Dark</button>
            </div>"""

# Version loading script
version_script = """
        // Load version
        fetch('/version')
            .then(r => r.json())
            .then(data => {
                const versionEl = document.getElementById('app-version');
                if (versionEl && data.version) {
                    versionEl.textContent = data.version;
                }
            })
            .catch(() => {
                const versionEl = document.getElementById('app-version');
                if (versionEl) versionEl.textContent = '1.0.0';
            });"""

for html_file in html_files:
    if 'shared' in str(html_file) or 'drafts_queue' in str(html_file):
        continue  # Skip shared components and drafts queue (they're handled separately)
    
    content = html_file.read_text(encoding='utf-8')
    original = content
    
    # Check if version already added
    if 'id="app-version"' in content:
        print(f"✓ {html_file.name} already has version")
        continue
    
    # Find dark mode button and replace with version + button
    # Pattern: button with toggleDarkMode and dark-toggle or dark-mode
    pattern1 = r'(\s+)<button onclick="toggleDarkMode\(\)" id="dark-toggle[^"]*"[^>]*>🌙 Dark</button>'
    if re.search(pattern1, content):
        content = re.sub(
            pattern1,
            r'\1' + version_span.replace('\n', '\n' + r'\1'),
            content,
            flags=re.MULTILINE
        )
    else:
        # Try alternative pattern
        pattern2 = r'(\s+)<button[^>]*onclick="toggleDarkMode\(\)"[^>]*>🌙 Dark</button>'
        if re.search(pattern2, content):
            content = re.sub(
                pattern2,
                r'\1' + version_span.replace('\n', '\n' + r'\1'),
                content,
                flags=re.MULTILINE
            )
    
    # Add version loading script before closing script tag or before DOMContentLoaded
    if '<script>' in content and 'fetch(\'/version\')' not in content:
        # Try to add before DOMContentLoaded
        if 'DOMContentLoaded' in content:
            content = re.sub(
                r'(document\.addEventListener\([\'"]DOMContentLoaded[\'"]',
                version_script + r'\n\n        \1',
                content,
                count=1
            )
        elif '</script>' in content:
            # Add before last </script> tag
            scripts = content.split('</script>')
            if len(scripts) > 1:
                scripts[-2] += version_script
                content = '</script>'.join(scripts)
    
    if content != original:
        html_file.write_text(content, encoding='utf-8')
        print(f"✓ Updated {html_file.name}")
    else:
        print(f"  {html_file.name} - no changes needed or pattern not found")

print("\nDone! Check the files above.")

