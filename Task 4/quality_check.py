import re, sys

mapped_regex = re.compile(r"\d+\s\+\s\d+\smapped\s\((\d{1,2}\.\d{1,2})%")
with open('resources/alignment2.txt', 'r') as f:
    for line in f:
        result = mapped_regex.match(line)
        if result is None:
            continue
        
        quality_fp = float(result.group(1).strip())
        if quality_fp < 90:
            print("[BAD]: Quality of mapping < 90%", file=sys.stderr)
            exit(1)
        else:
            print(f"[GOOD]: Quality of mapping is {result.group(1)}%")
            exit(0)
        
    print('Unable to parse resources/alignment2.txt', file=sys.stderr)
    exit(1)