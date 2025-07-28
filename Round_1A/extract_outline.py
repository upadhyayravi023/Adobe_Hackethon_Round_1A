import os
import glob
import fitz
import json

def extract_text_blocks(pdf_path):
    doc = fitz.open(pdf_path)
    text_blocks = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if text:
                        text_blocks.append({
                            "text": text,
                            "font_size": span["size"],
                            "font_flags": span["flags"],
                            "page": page_num + 1
                        })
    doc.close()
    return text_blocks

def detect_headings(blocks):
    if not blocks:
        return "Unknown Title", []
    
    # Sort by font size to determine hierarchy
    font_sizes = sorted(set(b["font_size"] for b in blocks), reverse=True)
    size_thresholds = font_sizes[:3] if len(font_sizes) >= 3 else font_sizes + [0] * (3 - len(font_sizes))
    
    title = blocks[0]["text"] if blocks else "Unknown Title"
    headings = []
    
    for block in blocks:
        size = block["font_size"]
        is_bold = block["font_flags"] & 2  # Bold flag
        text = block["text"]
        page = block["page"]
        
        # Skip long text (likely not a heading)
        if len(text.split()) > 10:
            continue
            
        if size >= size_thresholds[0]:
            level = "H1"
        elif size >= size_thresholds[1]:
            level = "H2"
        elif size >= size_thresholds[2]:
            level = "H3"
        else:
            continue
            
        if is_bold or size > sum(size_thresholds) / len(size_thresholds):
            headings.append({"level": level, "text": text, "page": page})
    
    return title, headings

def process_pdf(pdf_path, output_dir):
    text_blocks = extract_text_blocks(pdf_path)
    title, headings = detect_headings(text_blocks)
    output_data = {"title": title, "outline": headings}
    
    filename = os.path.basename(pdf_path).replace(".pdf", ".json")
    output_path = os.path.join(output_dir, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

def main():
    input_dir = "/app/input"
    output_dir = "/app/output"
    os.makedirs(output_dir, exist_ok=True)
    
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
    for pdf_path in pdf_files:
        process_pdf(pdf_path, output_dir)

if __name__ == "__main__":
    main()
