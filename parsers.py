import re


# Detect if the code is an specific language
def detect_language(line, patterns):
    for lang, pattern in patterns.items():
        if pattern.match(line):
            return lang
    return None


# Check if the function is a healthcheck, do not include it
def contain_exclude(block):
    content = ''.join(block).lower()
    return 'healthcheck' in content or 'health' in content


# Parse Java code
def parse_java(i, total_lines, lines, result):
    actual_block = []
    # Capture Spring Boot annotations
    while i < total_lines and lines[i].strip().startswith('@'):
        actual_block.append(lines[i])
        i += 1

    # Detect method signature
    while i < total_lines and not lines[i].strip().startswith("public"):
        actual_block.append(lines[i])
        i += 1

    # Add the signature
    if i < total_lines and lines[i].strip().startswith("public"):
        actual_block.append(lines[i])
        brace_count = lines[i].count('{') - lines[i].count('}')
        i += 1

        # Capture body function by brace balancing
        while i < total_lines and brace_count > 0:
            actual_block.append(lines[i])
            brace_count += lines[i].count('{') - lines[i].count('}')
            i += 1

        if not contain_exclude(actual_block):
            result.append(''.join(actual_block))

    return result, i


# Parse Python code
def parse_python(i, total_lines, lines, result):
    actual_block = []
    indent_level = None

    # Look for def
    while i < total_lines:
        actual_block.append(lines[i])
        if lines[i].strip().startswith("def "):
            indent_level = len(lines[i]) - len(lines[i].lstrip())
            i += 1
            break
        i += 1

    # Add indented body
    while i < total_lines:
        line_indent = len(lines[i]) - len(lines[i].lstrip())
        if line_indent > indent_level or not lines[i].strip():
            actual_block.append(lines[i])
            i += 1
        else:
            break

    if not contain_exclude(actual_block):
        result.append(''.join(actual_block))

    return result, i


# Parse JavaScript code
def parse_javascript(i, total_lines, lines, result):
    actual_block = [lines[i]]
    brace_count = lines[i].count('{') - lines[i].count('}')
    i += 1

    while i < total_lines and brace_count > 0:
        actual_block.append(lines[i])
        brace_count += lines[i].count('{') - lines[i].count('}')
        i += 1

    if not contain_exclude(actual_block):
        result.append(''.join(actual_block))

    return result, i


# Parse read code, reducing the number of tokens
def parse_code(source_code):
    print("Parsing read code...")
    lines = source_code.splitlines(keepends=True)
    result = []
    i = 0
    total_lines = len(lines)

    # Patterns to look for in each language for a web challenge
    patterns = {
        'python': re.compile(r'^\s*@app\.route'),
        'java': re.compile(r'^\s*@(?:Get|Post|Put|Delete|Request)Mapping'),
        'js': re.compile(r'^\s*app\.(get|post|put|delete)\s*\(.*')
    }

    while i < total_lines:
        line = lines[i]
        language = detect_language(line, patterns)

        # Java language
        if language == 'java':
            result, i = parse_java(i, total_lines, lines, result)
            continue

        # Python language
        elif language == 'python':
            result, i = parse_python(i, total_lines, lines, result)
            continue

        # JavaScript language
        elif language == 'js':
            result, i = parse_javascript(i, total_lines, lines, result)
            continue

        else:
            i += 1

    return result
