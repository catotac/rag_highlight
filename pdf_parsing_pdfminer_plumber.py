import fitz  # PyMuPDF
import re

# Function to determine if a line is a section header based on regex and font size
def is_section_header(text, font_size, min_font_size=10):
    # Define a pattern to detect section/subsection headers (you can customize this)
    section_pattern = re.compile(r'^\d+(\.\d+)*\s')  # e.g., "1. ", "1.1 ", "2.3 "
    
    # We assume that headers have larger font sizes
    return bool(section_pattern.match(text)) and font_size > min_font_size

# Function to extract the PDF structure (sections, sub-sections, and text) using PyMuPDF
def extract_pdf_structure_with_font_info(pdf_path):
    document_structure = {}
    current_section = None
    current_sub_section = None

    # Open the PDF using PyMuPDF
    doc = fitz.open(pdf_path)

    # Iterate through the pages
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]  # Get the page content as a dictionary
        
        # Iterate through the blocks of text
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    # Extract text and font size
                    text = ""
                    font_size = None
                    for span in line["spans"]:
                        text += span["text"]
                        font_size = span["size"]
                    
                    text = text.strip()

                    # Detect if this is a section header based on regex and font size
                    if is_section_header(text, font_size):
                        section_match = re.match(r'^(\d+(\.\d+)*)\s(.+)', text)
                        if section_match:
                            section_number = section_match.group(1)
                            section_title = section_match.group(3)

                            # Determine if it's a section or sub-section based on its numbering
                            if '.' in section_number:
                                # This is a sub-section
                                current_sub_section = section_number + ' ' + section_title
                                if current_section:
                                    if 'sub_sections' not in document_structure[current_section]:
                                        document_structure[current_section]['sub_sections'] = {}
                                    document_structure[current_section]['sub_sections'][current_sub_section] = {'text': ''}
                            else:
                                # This is a main section
                                current_section = section_number + ' ' + section_title
                                document_structure[current_section] = {'text': '', 'sub_sections': {}}
                                current_sub_section = None

                    else:
                        # If not a section header, treat it as body text
                        if current_sub_section:
                            # Append text to the current sub-section
                            document_structure[current_section]['sub_sections'][current_sub_section]['text'] += ' ' + text
                        elif current_section:
                            # Append text to the current section
                            document_structure[current_section]['text'] += ' ' + text

    return document_structure

# Example usage
pdf_path = "path/to/your/document.pdf"
structure = extract_pdf_structure_with_font_info(pdf_path)

# Print the extracted structure
for section, content in structure.items():
    print(f"Section: {section}")
    print(f"Text: {content['text'][:200]}...")  # Print first 200 chars of the section text for preview
    if content['sub_sections']:
        for sub_section, sub_content in content['sub_sections'].items():
            print(f"  Sub-section: {sub_section}")
            print(f"  Text: {sub_content['text'][:200]}...")  # Print first 200 chars of the sub-section text

