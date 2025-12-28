#!/usr/bin/env python3
"""
Extract stylized facts from LaTeX file and create CSV files per section.
"""

import re
import csv
from pathlib import Path

def extract_sections_and_facts(tex_file):
    """
    Extract section names and their associated stylized facts from LaTeX file.
    Returns a dictionary with section names as keys and lists of facts as values.
    """
    with open(tex_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    sections = {}
    current_section = None
    
    # Pattern to match section headers
    section_pattern = r'\\section\{([^}]+)\}'
    
    # Pattern to match fact entries (number & fact text & & & \\)
    # This captures the number and the fact text between & symbols
    fact_pattern = r'(\d+)\s+&\s+([^&]+?)&\s+&\s+&\s+\\\\'
    
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        # Check for section header
        section_match = re.search(section_pattern, line)
        if section_match:
            current_section = section_match.group(1)
            sections[current_section] = []
            continue
        
        # Check for fact entry
        if current_section:
            fact_match = re.search(fact_pattern, line)
            if fact_match:
                fact_number = int(fact_match.group(1))
                fact_text = fact_match.group(2).strip()
                sections[current_section].append({
                    'Number': fact_number,
                    'DEB Stylized Fact': fact_text
                })
    
    return sections

def sanitize_filename(section_name):
    """Convert section name to valid filename."""
    # Remove special characters and replace spaces with underscores
    filename = re.sub(r'[^\w\s-]', '', section_name)
    filename = re.sub(r'[-\s]+', '_', filename)
    return filename.lower()

def create_csv_files(sections, output_dir='.'):
    """Create CSV files for each section."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    created_files = []
    
    for section_name, facts in sections.items():
        if not facts:  # Skip empty sections
            continue
        
        filename = sanitize_filename(section_name) + '.csv'
        filepath = output_path / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Number', 'DEB Stylized Fact', 'Accuracy', 'I have an explanation', 'Importance']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for fact in facts:
                writer.writerow({
                    'Number': fact['Number'],
                    'DEB Stylized Fact': fact['DEB Stylized Fact'],
                    'Accuracy': '',
                    'I have an explanation': '',
                    'Importance': ''
                })
        
        created_files.append(filepath)
        print(f"Created: {filepath} ({len(facts)} facts)")
    
    return created_files

def main():
    tex_file = 'Material_2.tex'
    
    print(f"Reading {tex_file}...")
    sections = extract_sections_and_facts(tex_file)
    
    print(f"\nFound {len(sections)} sections:")
    for section_name, facts in sections.items():
        print(f"  - {section_name}: {len(facts)} facts")
    
    print("\nCreating CSV files...")
    created_files = create_csv_files(sections)
    
    print(f"\nSuccessfully created {len(created_files)} CSV files!")
    
    # Summary
    total_facts = sum(len(facts) for facts in sections.values())
    print(f"\nSummary:")
    print(f"  Total sections: {len(sections)}")
    print(f"  Total stylized facts: {total_facts}")

if __name__ == '__main__':
    main()
