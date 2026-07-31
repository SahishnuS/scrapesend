import os
import re

def replace_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        return # Skip binary files

    # Remove the " AI" and "-ai" parts
    new_content = re.sub(r'InternHunt\s+AI', 'InternHunt', content, flags=re.IGNORECASE)
    new_content = re.sub(r'InternHunt-ai', 'InternHunt', new_content, flags=re.IGNORECASE)
    new_content = re.sub(r'internhunt-ai', 'internhunt', new_content, flags=re.IGNORECASE)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated: {filepath}")

def main():
    root_dir = '/home/sweetpotato/scrapesend'
    
    # Replace contents in all files
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Exclude hidden directories, node_modules, and venv
        dirnames[:] = [d for d in dirnames if not d.startswith('.') and d not in ('node_modules', '.venv', '__pycache__')]
        
        for filename in filenames:
            if filename.startswith('.'):
                if filename not in ('.gitignore', '.env.example', '.env'):
                    continue
            
            filepath = os.path.join(dirpath, filename)
            # Skip this script itself
            if filename == 'rename_project.py':
                continue
                
            replace_in_file(filepath)
            
    print("\n✅ Clean up complete! All ' AI' and '-ai' suffixes have been completely stripped. The project is strictly 'InternHunt'.")

if __name__ == '__main__':
    main()
