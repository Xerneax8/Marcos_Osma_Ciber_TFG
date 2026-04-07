import re
from pathlib import Path
import os


# Configurable penalty weights for easier maintenance
PENALTIES = {
    'html': {
        'missing_alt': 10,
        'inline_styles': 5,
        'missing_lang': 10,
        'obsolete_tags': 5
    },
    'css': {
        'important': 10,
        'id_selectors': 5,
        'import_usage': 10,
        'deep_nesting': 2
    },
    'js': {
        'console_logs': 5,
        'eval_usage': 20,
        'var_usage': 2,
        'debugger': 10
    }
}

# Analyze the code retrieved from the LLM with a punctuation from 0 to 100
def analyze_web_code(file_path):
    path = Path(file_path)

    print(f"\n{'=' * 40}\nAnalysis for: {path.name}\n{'=' * 40}")

    if not path.exists():
        error = {"Error": f"File '{path}' not found."}
        print(error["Error"])
        return error

    try:
        raw_content = path.read_text(encoding='utf-8', errors='ignore')
        lines = raw_content.split('\n')
    except Exception as e:
        error = {"Error": f"Could not read file: {e}"}
        print(error["Error"])
        return error

    # Basic structural metrics
    total_lines = len(lines)
    empty_lines = sum(1 for line in lines if not line.strip())
    size_kb = os.path.getsize(path) / 1024

    metrics = {
        "File Name": path.name,
        "Size (KB)": round(size_kb, 2),
        "Total Lines": total_lines,
        "Empty Lines": empty_lines,
    }

    ext = path.suffix.lower()
    score = 100

    # 1. HTML Analysis
    if ext in ['.htm', '.html']:
        clean_content = re.sub(r'', '', raw_content, flags=re.DOTALL)

        missing_alt = len(re.findall(r'<img(?![^>]*\balt=)[^>]*>', clean_content, re.IGNORECASE))
        inline_styles = len(re.findall(r'<[^>]+style\s*=', clean_content, re.IGNORECASE))
        missing_lang = 1 if not re.search(r'<html[^>]*\blang=', clean_content, re.IGNORECASE) else 0
        obsolete_tags = len(re.findall(r'</?(center|font|marquee|blink|strike|u)\b', clean_content, re.IGNORECASE))

        metrics.update({
            'Missing Alt on Images': missing_alt,
            'Inline Styles Used': inline_styles,
            'Missing <html lang="">': missing_lang,
            'Obsolete Tags Used': obsolete_tags
        })

        score -= (
                (missing_alt * PENALTIES['html']['missing_alt']) +
                (inline_styles * PENALTIES['html']['inline_styles']) +
                (missing_lang * PENALTIES['html']['missing_lang']) +
                (obsolete_tags * PENALTIES['html']['obsolete_tags'])
        )

    # 2. CSS Analysis
    elif ext == '.css':
        clean_content = re.sub(r'/\*.*?\*/', '', raw_content, flags=re.DOTALL)

        important_flags = len(re.findall(r'!important\b', clean_content, re.IGNORECASE))
        id_selectors = len(re.findall(r'#[a-zA-Z0-9_-]+\s*[,{>+~]', clean_content))
        import_usage = len(re.findall(r'@import\b', clean_content, re.IGNORECASE))
        deep_nesting = len(re.findall(r'(?:[\w.#:-]+\s+){3,}[\w.#:-]+\s*\{', clean_content))

        metrics.update({
            'Use of !important': important_flags,
            'ID Selectors Used': id_selectors,
            '@import Used': import_usage,
            'Deeply Nested Selectors': deep_nesting
        })

        score -= (
                (important_flags * PENALTIES['css']['important']) +
                (id_selectors * PENALTIES['css']['id_selectors']) +
                (import_usage * PENALTIES['css']['import_usage']) +
                (deep_nesting * PENALTIES['css']['deep_nesting'])
        )

    # 3. JavaScript Analysis
    elif ext == '.js':
        clean_content = re.sub(r'/\*.*?\*/|//.*', '', raw_content, flags=re.DOTALL)

        console_logs = len(re.findall(r'console\.(log|warn|error|info|table)\s*\(', clean_content))
        eval_usage = len(re.findall(r'\beval\s*\(', clean_content))
        var_usage = len(re.findall(r'\bvar\s+\w+', clean_content))
        debugger_usage = len(re.findall(r'\bdebugger\s*;?', clean_content))

        metrics.update({
            'Console Logs': console_logs,
            'Dangerous eval() usage': eval_usage,
            'Outdated var usage': var_usage,
            'Leftover debugger tags': debugger_usage
        })

        score -= (
                (console_logs * PENALTIES['js']['console_logs']) +
                (eval_usage * PENALTIES['js']['eval_usage']) +
                (var_usage * PENALTIES['js']['var_usage']) +
                (debugger_usage * PENALTIES['js']['debugger'])
        )

    else:
        error = {"Error": f"Unsupported file type: {ext}"}
        print(error["Error"])
        return error

    metrics['Quality Score'] = max(0, score)

    # Print the results directly inside the function
    print(f"OVERALL QUALITY SCORE: {metrics['Quality Score']}/100\n")
    for key, value in metrics.items():
        if key != 'Quality Score':
            print(f"  {key:<25} | {value}")