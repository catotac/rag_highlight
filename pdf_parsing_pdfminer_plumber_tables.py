import fitz  # PyMuPDF
import pdfplumber
import re

# Function to determine if a line is a section header
def is_section_header(text, font_size, min_font_size=10):
    section_pattern = re.compile(r'^\d+(\.\d+)*\s')  # e.g., "1. ", "1.1 ", "2.3 "
    return bool(section_pattern.match(text)) and font_size > min_font_size

# Function to extract the PDF structure along with tables and images
def extract_pdf_structure_with_tables_and_figures(pdf_path):
    document_structure = {}
    current_section = None
    current_sub_section = None
    table_count = 0
    figure_count = 0

    # Open the PDF using PyMuPDF
    doc = fitz.open(pdf_path)

    # Extract tables using pdfplumber
    with pdfplumber.open(pdf_path) as plumber_doc:
        tables = {page_num: page.extract_tables() for page_num, page in enumerate(plumber_doc.pages)}

    # Iterate through the pages
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    text = ""
                    font_size = None
                    for span in line["spans"]:
                        text += span["text"]
                        font_size = span["size"]

                    text = text.strip()

                    # Detect if this is a section header
                    if is_section_header(text, font_size):
                        section_match = re.match(r'^(\d+(\.\d+)*)\s(.+)', text)
                        if section_match:
                            section_number = section_match.group(1)
                            section_title = section_match.group(3)

                            # If there's a period in the number, it's a sub-section
                            if '.' in section_number:
                                current_sub_section = section_number + ' ' + section_title
                                if current_section:
                                    if 'sub_sections' not in document_structure[current_section]:
                                        document_structure[current_section]['sub_sections'] = {}
                                    document_structure[current_section]['sub_sections'][current_sub_section] = {
                                        'text': '', 'tables': [], 'figures': []
                                    }
                            else:
                                # It's a main section
                                current_section = section_number + ' ' + section_title
                                document_structure[current_section] = {'text': '', 'sub_sections': {}, 'tables': [], 'figures': []}
                                current_sub_section = None
                    else:
                        # Handle normal text
                        if current_sub_section:
                            document_structure[current_section]['sub_sections'][current_sub_section]['text'] += ' ' + text
                        elif current_section:
                            document_structure[current_section]['text'] += ' ' + text

        # Extract images (figures) on the page
        images = page.get_images(full=True)
        for image_index, img in enumerate(images):
            img_data = page.get_image_bbox(img[0])
            figure_info = {
                'figure_id': f'Figure_{figure_count+1}',
                'bbox': img_data,
                'page': page_num
            }
            if current_sub_section:
                document_structure[current_section]['sub_sections'][current_sub_section]['figures'].append(figure_info)
            elif current_section:
                document_structure[current_section]['figures'].append(figure_info)
            figure_count += 1

        # Extract tables from the current page using pdfplumber
        if page_num in tables and tables[page_num]:
            for table in tables[page_num]:
                table_info = {
                    'table_id': f'Table_{table_count+1}',
                    'table_data': table,
                    'page': page_num
                }
                if current_sub_section:
                    document_structure[current_section]['sub_sections'][current_sub_section]['tables'].append(table_info)
                elif current_section:
                    document_structure[current_section]['tables'].append(table_info)
                table_count += 1

    return document_structure

# Example usage
pdf_path = "path/to/your/document.pdf"
structure = extract_pdf_structure_with_tables_and_figures(pdf_path)

# Print the structure with sections, tables, and figures
for section, content in structure.items():
    print(f"Section: {section}")
    print(f"Text: {content['text'][:200]}...")  # First 200 chars of section text
    print(f"Tables: {[table['table_id'] for table in content['tables']]}")
    print(f"Figures: {[figure['figure_id'] for figure in content['figures']]}")
    if content['sub_sections']:
        for sub_section, sub_content in content['sub_sections'].items():
            print(f"  Sub-section: {sub_section}")
            print(f"  Text: {sub_content['text'][:200]}...")
            print(f"  Tables: {[table['table_id'] for table in sub_content['tables']]}")
            print(f"  Figures: {[figure['figure_id'] for figure in sub_content['figures']]}")

