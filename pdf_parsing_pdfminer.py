import re
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal, LTTextLineHorizontal

# Function to determine if a line is a section header
def is_section_header(text):
    # Define a pattern to detect section/subsection headers (you can customize this)
    section_pattern = re.compile(r'^\d+(\.\d+)*\s')  # e.g., "1. ", "1.1 ", "2.3.4 "
    return bool(section_pattern.match(text.strip()))

# Function to extract the text and structure from the PDF
def extract_pdf_structure(pdf_path):
    document_structure = {}
    current_section = None
    current_sub_section = None

    # Loop through each page and extract the text content
    for page_layout in extract_pages(pdf_path):
        for element in page_layout:
            if isinstance(element, LTTextBoxHorizontal):
                for text_line in element:
                    if isinstance(text_line, LTTextLineHorizontal):
                        text = text_line.get_text().strip()

                        # Check if this line is a section or sub-section header
                        if is_section_header(text):
                            # Check the hierarchy of sections and subsections
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
                            # If it's not a section header, it's part of the text
                            if current_sub_section:
                                # Append text to the current sub-section
                                document_structure[current_section]['sub_sections'][current_sub_section]['text'] += ' ' + text
                            elif current_section:
                                # Append text to the current section
                                document_structure[current_section]['text'] += ' ' + text
                            else:
                                # Text outside of any section/sub-section (shouldn't happen often)
                                continue

    return document_structure

# Example usage
pdf_path = "path/to/your/document.pdf"
structure = extract_pdf_structure(pdf_path)

# Print the extracted structure
for section, content in structure.items():
    print(f"Section: {section}")
    print(f"Text: {content['text'][:200]}...")  # Print first 200 chars of the section text for preview
    if content['sub_sections']:
        for sub_section, sub_content in content['sub_sections'].items():
            print(f"  Sub-section: {sub_section}")
            print(f"  Text: {sub_content['text'][:200]}...")  # Print first 200 chars of the sub-section text

