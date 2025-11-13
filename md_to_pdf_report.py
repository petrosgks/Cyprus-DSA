from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, ListFlowable, ListItem
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import markdown
from bs4 import BeautifulSoup
from reportlab.platypus import PageBreak
import re


def md_to_pdf(input_file, output_file):
    
    with open(input_file, encoding="utf-8") as f:
        md_text = f.read()

    
    md_text = md_text.replace('►', u'\u2022')
    
    
    md_text = md_text.replace('<!-- pagebreak -->', '<div style="page-break-after: always;"></div>')

    
    html_text = markdown.markdown(md_text, extensions=["tables", "fenced_code"])
    soup = BeautifulSoup(html_text, "html.parser")

    
    styles = getSampleStyleSheet()
    
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles["Normal"],
        fontSize=16,  # ΜΕΓΑΛΥΤΕΡΟ γράμμα
        leading=18    # leading = fontSize + 4
    )
    
    
    table_text_style = ParagraphStyle(
        'CustomTableText',
        parent=styles["Normal"], 
        fontSize=14,  
        leading=14    
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles["Heading1"],
        fontSize=25,
        spaceBefore=5,
        spaceAfter=5,
        leading=25
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles["Heading2"],
        fontSize=25,
        spaceBefore=5,
        spaceAfter=5,
        leading=22
    )
    
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles["Heading3"],
        fontSize=14,
        spaceBefore=10,
        spaceAfter=10,
        leading=19
    )

    
    heading4_style = ParagraphStyle(
        name="CustomHeading4",
        parent=styles["Heading3"],
        fontSize=12,
        spaceBefore=12,
        spaceAfter=6,
        leading=16,
        textColor=colors.black
    )

    heading5_style = ParagraphStyle(
        name="CustomHeading5",
        parent=styles["Normal"],
        fontSize=11,
        spaceBefore=10,
        spaceAfter=5,
        leading=15,
        textColor=colors.darkgray
    )

    heading6_style = ParagraphStyle(
        name="CustomHeading6", 
        parent=styles["Normal"],
        fontSize=10,
        spaceBefore=8,
        spaceAfter=4,
        leading=14,
        textColor=colors.gray
    )

    
    header_style = ParagraphStyle(
        'TableHeader',
        parent=styles["Normal"],
        fontSize=12,           
        fontName='Helvetica-Bold',
        alignment=1,  # CENTER
        wordWrap='CJK',
        leading=14
    )

    
    doc = SimpleDocTemplate(
        output_file, 
        pagesize=landscape(A4),
        topMargin=15,    
        bottomMargin=15, 
        leftMargin=20,
        rightMargin=20
    )
    
    story = []

    def extract_color_from_style(style_attr):
        
        if not style_attr:
            return None
        
        
        color_match = re.search(r'color\s*:\s*([^;]+)', style_attr)
        if color_match:
            color_value = color_match.group(1).strip()
            return color_value
        return None

    def clean_html(elem):
        
        
        if hasattr(elem, 'get') and elem.get('style') and 'page-break-after' in elem.get('style'):
            return "PAGE_BREAK"
        
        
        if not hasattr(elem, 'children'):
            return str(elem)
        
        result = ""
        
        
        if elem.name == "span" and elem.get('style'):
            color = extract_color_from_style(elem.get('style'))
            if color:
                
                result += f"<font color='{color}'>{elem.get_text()}</font>"
                return result
        
        for child in elem.children:
            if hasattr(child, "name"):  
                if child.name in ["b", "strong"]:
                    result += f"<b>{clean_html(child)}</b>"
                elif child.name in ["i", "em"]:
                    result += f"<i>{clean_html(child)}</i>"
                elif child.name == "u":
                    result += f"<u>{clean_html(child)}</u>"
                elif child.name == "br":
                    result += "<br/>"
                elif child.name == "code":
                    result += f"<font face='Courier'>{child.get_text()}</font>"
                elif child.name == "span":
                    
                    span_result = clean_html(child)
                    if span_result != "PAGE_BREAK":
                        result += span_result
                else:
                    child_result = clean_html(child)
                    if child_result != "PAGE_BREAK":
                        result += child_result
            else:
                
                result += str(child)
        return result

    def process_element(elem):
        
        if elem.name == "div" and elem.get('style') and 'page-break-after' in elem.get('style'):
            story.append(PageBreak())
            return
        
        if elem.name == "h1":
            story.append(Paragraph(clean_html(elem), heading1_style))
            story.append(Spacer(1, 20))
        elif elem.name == "h2":
            story.append(Paragraph(clean_html(elem), heading2_style))
            story.append(Spacer(1, 15))
        elif elem.name == "h3":
            story.append(Paragraph(clean_html(elem), heading3_style))
            story.append(Spacer(1, 10))
        elif elem.name == "h4":
            story.append(Paragraph(clean_html(elem), heading4_style))
            story.append(Spacer(1, 8))
        elif elem.name == "h5":
            story.append(Paragraph(clean_html(elem), heading5_style))
            story.append(Spacer(1, 6))
        elif elem.name == "h6":
            story.append(Paragraph(clean_html(elem), heading6_style))
            story.append(Spacer(1, 4))
        elif elem.name == "p":
            cleaned_text = clean_html(elem)
            if cleaned_text != "PAGE_BREAK":
                story.append(Paragraph(cleaned_text, normal_style))
        elif elem.name == "ul":
            items = []
            for li in elem.find_all("li"):
                cleaned_text = clean_html(li)
                if cleaned_text != "PAGE_BREAK":
                    items.append(ListItem(Paragraph(cleaned_text, normal_style)))
            if items:
                story.append(ListFlowable(items, bulletType="bullet"))
        elif elem.name == "ol":
            items = []
            for li in elem.find_all("li"):
                cleaned_text = clean_html(li)
                if cleaned_text != "PAGE_BREAK":
                    items.append(ListItem(Paragraph(cleaned_text, normal_style)))
            if items:
                story.append(ListFlowable(items, bulletType="1"))
        elif elem.name == "table":
            rows = []
            for i, tr in enumerate(elem.find_all("tr")):
                row_elems = tr.find_all(["td","th"])
                if i == 0:  # header
                    row = [Paragraph(clean_html(td), header_style) for td in row_elems]  
                else:
                    row = [Paragraph(clean_html(td), table_text_style) for td in row_elems]  
                rows.append(row)

            
            col_n1 = 0      
            col_desc = 1    
            last_n1 = ""
            last_desc = ""
            for r in range(1, len(rows)):
                n1_text = rows[r][col_n1].getPlainText().strip()
                desc_text = rows[r][col_desc].getPlainText().strip()
                if n1_text != "":
                    last_n1 = n1_text
                    last_desc = desc_text
                else:
                    rows[r][col_n1] = Paragraph("", table_text_style)
                    rows[r][col_desc] = Paragraph("", table_text_style)

            
            num_cols = len(rows[0])
            col_widths = []
            for c in range(num_cols):
                if c == 0:
                    col_widths.append(130)
                elif c == 1:
                    col_widths.append(170)
                elif c == 2:
                    col_widths.append(270)    
                else:
                    col_widths.append(170)

            
            table = Table(rows, colWidths=col_widths, hAlign="CENTER", repeatRows=1)
            style = TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#d3d3d3")),
                ("TEXTCOLOR", (0,0), (-1,0), colors.black),
                ("ALIGN", (0,0), (-1,-1), "CENTER"),
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
                ("LEFTPADDING", (0,0), (-1,-1), 8),
                ("RIGHTPADDING", (0,0), (-1,-1), 8),
                ("TOPPADDING", (0,0), (-1,-1), 4),
                ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ])
            for i in range(1, len(rows)):
                if i % 2 == 0:
                    style.add("BACKGROUND", (0,i), (-1,i), colors.whitesmoke)
            table.setStyle(style)
            story.append(table)

        story.append(Spacer(1, 12))

    
    for elem in soup.contents:
        if hasattr(elem, 'name'):  
            process_element(elem)

    doc.build(story)
    print(f"Pdf final report sucessfully saved as: {output_file}")



