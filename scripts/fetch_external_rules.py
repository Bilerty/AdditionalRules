import re
import urllib.request
import os
import json

# Paths
JSON_CONFIG = 'subConvRules/external_rules.json'
OUT_DIR = 'subConvRules/externalList'

def fetch_and_convert(name, url):
    """
    Fetches raw rule file and converts it to standard .list format (TYPE,CONTENT).
    """
    print(f"--- Processing {name} ---")
    print(f"URL: {url}")
    try:
        # User-Agent is sometimes required by GitHub/JsDelivr
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8')
        
        rules = []
        is_payload = False
        
        # Determine if it's likely a 'domain' or 'ipcidr' shorthand list
        is_domain_shorthand = 'Loyalsoldier' in url and any(x in url for x in ['reject', 'icloud', 'apple', 'google', 'proxy', 'direct', 'private', 'gfw', 'tld-not-cn'])
        is_ipcidr_shorthand = 'Loyalsoldier' in url and any(x in url for x in ['telegramcidr', 'cncidr', 'lancidr'])

        for line in content.splitlines():
            line = line.strip()
            
            # Start of Clash payload
            if line.startswith('payload:'):
                is_payload = True
                continue
            
            if is_payload:
                if line.startswith('-'):
                    # Rule entry found
                    rule = line[1:].strip().strip("'").strip('"')
                    
                    # Conversion logic
                    if ',' in rule:
                        # Already in TYPE,CONTENT or it's a metadata rule
                        rules.append(rule)
                    elif is_domain_shorthand:
                        if rule.startswith('+.'):
                            rules.append(f"DOMAIN-SUFFIX,{rule[2:]}")
                        else:
                            rules.append(f"DOMAIN,{rule}")
                    elif is_ipcidr_shorthand:
                        rules.append(f"IP-CIDR,{rule}")
                    else:
                        # Fallback for other formats
                        rules.append(rule)
                elif line and not line.startswith('#') and ':' in line:
                    # Likely end of payload if not indented
                    pass
            else:
                # Handle non-payload raw lists (if any)
                if line and not line.startswith('#') and not line.startswith('---'):
                    if ',' in line:
                        rules.append(line)
        
        if rules:
            os.makedirs(OUT_DIR, exist_ok=True)
            out_file = os.path.join(OUT_DIR, f"{name}.list")
            with open(out_file, 'w', encoding='utf-8', newline='\n') as f:
                f.write('\n'.join(rules) + '\n')
            print(f"Successfully saved {len(rules)} rules to {out_file}")
            return True
        else:
            print(f"No rules extracted from {name}")
            return False

    except Exception as e:
        print(f"Error processing {name}: {e}")
        return False

def main():
    if not os.path.exists(JSON_CONFIG):
        print(f"Error: {JSON_CONFIG} not found.")
        return

    with open(JSON_CONFIG, 'r', encoding='utf-8') as f:
        try:
            external_rules = json.load(f)
        except Exception as e:
            print(f"Error: Failed to parse {JSON_CONFIG}: {e}")
            return

    if not external_rules:
        print(f"No rules found in {JSON_CONFIG}.")
        return

    print(f"Found {len(external_rules)} external rule providers in JSON config.")
    
    for name, url in external_rules.items():
        fetch_and_convert(name, url)
    
    print("\nAll external rules processed.")

if __name__ == "__main__":
    main()
