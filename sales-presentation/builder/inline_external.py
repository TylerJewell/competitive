"""
inline_external.py — Extracts and scopes content from standalone HTML files
so they can be inlined into the presentation without CSS collisions.

Usage from build.py:
    from inline_external import process
    result = process(html_path, wrapper_id='s6-rf', root_id='root')
    # result.head_scripts  — list of <script src="..."> strings for <head>
    # result.css           — CSS scoped under #wrapper_id
    # result.html          — body HTML with root div renamed + wrapper div added
    # result.js            — JS with root ID patched, wrapped for Babel if needed
"""

import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class InlinedExternal:
    head_scripts: List[str] = field(default_factory=list)
    css:  str = ''
    html: str = ''
    js:   str = ''


# ── CSS scoping ───────────────────────────────────────────────────────────────

def scope_css(css: str, scope: str) -> str:
    """
    Prefix all CSS selectors with #scope so they only apply inside the wrapper.
    - :root {}  →  #scope {}  (so custom props are inherited from the wrapper)
    - body {}   →  #scope {}
    - *, *::before, *::after {}  →  #scope *, ... {}
    - @keyframes blocks  →  unchanged (they're globally named, no collision risk)
    - all other selectors  →  prefixed with #scope
    """

    # 1. Pull out @keyframes blocks so we don't accidentally mangle their contents
    keyframes: dict = {}
    kf_counter = [0]

    def stash_keyframe(m):
        key = f'__KF{kf_counter[0]}__'
        kf_counter[0] += 1
        keyframes[key] = m.group(0)
        return key

    css = re.sub(
        r'@keyframes\s+[\w-]+\s*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}',
        stash_keyframe, css
    )

    # 2. Scope :root and body (handle optional leading whitespace)
    css = re.sub(r'(\s*):root\s*\{', lambda m: m.group(1) + f'#{scope} {{', css)
    css = re.sub(r'^(\s*)body\s*\{', lambda m: m.group(1) + f'#{scope} {{',
                 css, flags=re.MULTILINE)

    # 3. Scope the universal selector reset  "*, *::before, *::after {"
    css = re.sub(
        r'^(\s*)\*\s*,\s*\*::before\s*,\s*\*::after\s*\{',
        lambda m: m.group(1) + f'#{scope} *, #{scope} *::before, #{scope} *::after {{',
        css, flags=re.MULTILINE
    )

    # 4. Scope all remaining selectors.
    #    Match lines that end with `{` — including indented ones.
    #    Skip: property lines (contain :), closing braces, stashed tokens, @ rules.
    def add_scope_prefix(m):
        indent   = m.group(1)   # leading whitespace
        selector = m.group(2).strip()
        # Skip already-scoped, CSS properties (contain : but not ::), comments, tokens
        if (selector.startswith(f'#{scope}')
                or selector.startswith('--')
                or selector.startswith('/*')
                or selector.startswith('__KF')
                or selector.startswith('@')):
            return m.group(0)
        # A CSS property looks like "property: value" — skip it
        # (has a colon not preceded by ::)
        if re.search(r'(?<!:):(?!:)', selector) and not selector.startswith(':'):
            return m.group(0)
        # Comma-separate → scope each part
        parts = [p.strip() for p in selector.split(',')]
        scoped_parts = []
        for p in parts:
            if p.startswith(f'#{scope}') or not p:
                scoped_parts.append(p)
            else:
                scoped_parts.append(f'#{scope} {p}')
        return indent + ', '.join(scoped_parts) + ' {'

    css = re.sub(r'^(\s*)([^\s{}\n][^{}\n]*)\s*\{', add_scope_prefix,
                 css, flags=re.MULTILINE)

    # 5. Restore @keyframes blocks
    for key, val in keyframes.items():
        css = css.replace(key, val)

    return css


# ── Main processor ────────────────────────────────────────────────────────────

def process(html_path: str, wrapper_id: str, root_id: str = 'root') -> InlinedExternal:
    """
    Parse a standalone HTML file and return everything needed to inline it.

    Parameters
    ----------
    html_path   : absolute path to the source HTML file
    wrapper_id  : ID for the scoping div (e.g. 's6-rf')
    root_id     : ID of the React/app root element inside the source (e.g. 'root')
    """
    with open(html_path, 'r', encoding='utf-8') as f:
        src = f.read()

    result = InlinedExternal()
    new_root_id = f'{wrapper_id}-root'

    # ── 1. CDN / external script tags from <head> ────────────────────────────
    head_match = re.search(r'<head>(.*?)</head>', src, re.DOTALL | re.IGNORECASE)
    if head_match:
        head_content = head_match.group(1)
        for tag in re.findall(r'<script\s+src=["\'][^"\']+["\'][^>]*></script>',
                              head_content, re.IGNORECASE):
            result.head_scripts.append(tag)

    # ── 2. CSS ───────────────────────────────────────────────────────────────
    style_match = re.search(r'<style>(.*?)</style>', src, re.DOTALL | re.IGNORECASE)
    if style_match:
        raw_css = style_match.group(1)
        result.css = scope_css(raw_css, wrapper_id)

    # ── 3. Body HTML + special script tags ───────────────────────────────────
    # Scripts with a special type (e.g. type="text/babel") must be emitted as
    # standalone <script> elements in the HTML body — NOT inside the shared
    # <script> block, which would produce invalid nested <script> tags and
    # break the entire page.  Plain JS (no type attr) goes into result.js.
    body_match = re.search(r'<body>(.*?)</body>', src, re.DOTALL | re.IGNORECASE)
    if body_match:
        body_content = body_match.group(1)

        # Collect all inline script blocks, patch root ID in each
        special_script_tags = []   # <script type="..."> → go into html
        plain_js_blocks     = []   # plain <script> → go into js

        for script_match in re.finditer(
                r'<script(\b[^>]*)>(.*?)</script>', body_content,
                re.DOTALL | re.IGNORECASE):
            attrs = script_match.group(1).strip()
            code  = script_match.group(2)
            if 'src=' in attrs:
                continue  # external scripts already in head_scripts
            # Patch root ID
            code = code.replace(
                f'getElementById("{root_id}")',
                f'getElementById("{new_root_id}")'
            ).replace(
                f"getElementById('{root_id}')",
                f"getElementById('{new_root_id}')"
            )
            if attrs:  # has type= or other attributes → must be a standalone tag
                special_script_tags.append(f'<script {attrs}>{code}</script>')
            else:
                plain_js_blocks.append(code)

        # Strip ALL inline scripts from body HTML
        body_html = re.sub(r'<script\b[^>]*>.*?</script>', '',
                           body_content, flags=re.DOTALL | re.IGNORECASE).strip()
        # Rename the root element
        body_html = body_html.replace(f'id="{root_id}"', f'id="{new_root_id}"')

        # Wrap in scoping div; append any special script tags as siblings
        result.html = (
            f'<div id="{wrapper_id}">\n'
            f'{body_html}\n'
            f'</div>'
        )
        if special_script_tags:
            result.html += '\n' + '\n'.join(special_script_tags)

        if plain_js_blocks:
            result.js = '\n'.join(plain_js_blocks)

    return result
