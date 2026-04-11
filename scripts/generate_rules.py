import os
import glob

# Paths
SRC_DIR = 'srcRules'
OUT_DIR = 'rules'

def main():
    # Ensure output directory exists
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)
        print(f"Created directory: {OUT_DIR}")

    # Find all .list files
    list_files = glob.glob(os.path.join(SRC_DIR, '*.list'))
    if not list_files:
        print(f"No .list files found in {SRC_DIR}")
        return

    print(f"Found {len(list_files)} .list files to process.")

    for list_path in list_files:
        base_name = os.path.basename(list_path)
        # Generate corresponding .txt filename
        name_without_ext = os.path.splitext(base_name)[0]
        txt_name = name_without_ext + '.txt'
        out_path = os.path.join(OUT_DIR, txt_name)

        print(f"Processing: {base_name} -> {txt_name}")

        try:
            with open(list_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Filter rules: remove empty lines and comments
            rules = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Basic rule extraction
                    rules.append(line)

            # Write to classical YAML format
            with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write('payload:\n')
                for rule in rules:
                    f.write(f'  - {rule}\n')

        except Exception as e:
            print(f"Error processing {base_name}: {e}")

    print("All files processed successfully.")

if __name__ == "__main__":
    main()
