import os
import re
import csv
import io
import html
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Ensure NLTK datasets are downloaded silently
def setup_nltk():
    nltk_data = ['stopwords', 'wordnet', 'omw-1.4', 'punkt']
    for data in nltk_data:
        try:
            nltk.download(data, quiet=True)
        except Exception as e:
            pass

setup_nltk()

lemmatizer = WordNetLemmatizer()
try:
    stop_words = set(stopwords.words('english'))
except Exception:
    stop_words = set()

def clean_text(text):
    """
    Dataset preprocessing:
    - Remove punctuation and special characters
    - Convert to lower case
    - Remove stopwords
    - Apply lemmatization
    """
    if not isinstance(text, str):
        return ""
    
    # Remove HTML tags & non-alphabet characters
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    
    # Convert to lowercase & tokenize
    words = text.lower().split()
    
    # Remove stopwords and apply lemmatization
    cleaned_words = [
        lemmatizer.lemmatize(word)
        for word in words
        if word not in stop_words and len(word) > 2
    ]
    
    return " ".join(cleaned_words)

def analyze_text_metadata(content):
    """Computes basic text statistics like word count, char count, reading time."""
    words = content.split()
    word_count = len(words)
    char_count = len(content)
    reading_time_min = max(1, round(word_count / 200, 1))
    
    return {
        'word_count': word_count,
        'char_count': char_count,
        'reading_time': reading_time_min
    }

def generate_pdf_report(prediction_record):
    """Generates a styled PDF report for a given prediction record."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0f172a'),
        alignment=1, # Center
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'SubTitleStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#64748b'),
        alignment=1,
        spaceAfter=25
    )

    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155')
    )

    story = []
    
    # Header
    story.append(Paragraph("VeriNews - Fake News Analysis Report", title_style))
    story.append(Paragraph("Machine Learning Verification & Credibility Assessment Certificate", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2563eb'), spaceAfter=20))
    
    # Result Highlight Table
    is_real = prediction_record.prediction == 'REAL NEWS'
    status_bg = colors.HexColor('#16a34a') if is_real else colors.HexColor('#dc2626')
    
    summary_data = [
        [
            Paragraph("<b>Report ID:</b>", body_style),
            Paragraph(f"VN-{prediction_record.id:06d}", body_style),
            Paragraph("<b>Timestamp:</b>", body_style),
            Paragraph(prediction_record.created_at.strftime('%B %d, %Y %H:%M UTC'), body_style)
        ],
        [
            Paragraph("<b>Prediction Result:</b>", body_style),
            Paragraph(f"<font color='{'#16a34a' if is_real else '#dc2626'}'><b>{prediction_record.prediction}</b></font>", body_style),
            Paragraph("<b>Confidence Level:</b>", body_style),
            Paragraph(f"<b>{prediction_record.confidence:.1f}%</b>", body_style)
        ],
        [
            Paragraph("<b>Model Used:</b>", body_style),
            Paragraph(prediction_record.model_used, body_style),
            Paragraph("<b>Word Count:</b>", body_style),
            Paragraph(str(prediction_record.word_count), body_style)
        ]
    ]
    
    t = Table(summary_data, colWidths=[110, 150, 110, 160])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))
    
    # Article Headline & Content section
    story.append(Paragraph("<b>Article Headline:</b>", styles['Heading3']))
    raw_title = prediction_record.news_title if prediction_record.news_title else "No Title Provided"
    headline_text = html.escape(raw_title)
    story.append(Paragraph(headline_text, body_style))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("<b>Article Excerpt / Full Text:</b>", styles['Heading3']))
    content_text = html.escape(prediction_record.news_content).replace('\n', '<br/>')
    story.append(Paragraph(content_text, body_style))
    story.append(Spacer(1, 25))
    
    # Disclaimer
    disclaimer_style = ParagraphStyle('Disc', parent=styles['Italic'], fontSize=8, textColor=colors.HexColor('#94a3b8'), alignment=1)
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceAfter=10))
    story.append(Paragraph("Disclaimer: This report was automatically generated by VeriNews AI using natural language processing and TF-IDF statistical modeling. It should be used as an assistive verification tool rather than an absolute source of truth.", disclaimer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_csv_export(records):
    """Generates a CSV file buffer from prediction records."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Date', 'News Title', 'News Content Snippet', 'Prediction', 'Confidence (%)', 'Model Used', 'Word Count'])
    
    for r in records:
        writer.writerow([
            r.id,
            r.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            r.news_title or 'Untitled',
            r.news_content[:200].replace('\n', ' '),
            r.prediction,
            f"{r.confidence:.1f}",
            r.model_used,
            r.word_count
        ])
        
    return output.getvalue()
