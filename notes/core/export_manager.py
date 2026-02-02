import json
import csv
from .database import get_db
from .models import Note, WorkLog
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import pandas as pd
import os

class ExportManager:
    def export_notes_json(self, filepath):
        db = next(get_db())
        notes = db.query(Note).filter(Note.is_deleted == False).all()
        data = [{"id": n.id, "title": n.title, "content": n.content, "created_at": str(n.created_at)} for n in notes]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            
    def export_notes_pdf(self, filepath):
        db = next(get_db())
        notes = db.query(Note).filter(Note.is_deleted == False).all()
        c = canvas.Canvas(filepath, pagesize=letter)
        y = 750
        c.setFont("Helvetica", 12)
        c.drawString(100, y, "Notes Export")
        y -= 30
        
        for note in notes:
            if y < 100:
                c.showPage()
                y = 750
            c.drawString(100, y, f"Title: {note.title}")
            y -= 20
            c.drawString(100, y, f"Content: {note.content[:50]}...")
            y -= 40
            
        c.save()

    def export_logs_excel(self, filepath):
        db = next(get_db())
        logs = db.query(WorkLog).all()
        data = [{"Date": l.date, "Title": l.title, "Content": l.content, "Duration": l.duration_minutes} for l in logs]
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False)
