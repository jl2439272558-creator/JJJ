from .database import get_db
from .models import Note, OperationLog
from sqlalchemy.orm import Session
from datetime import datetime

class NoteManager:
    def get_all_notes(self):
        db = next(get_db())
        try:
            # Sort by color (completed #e0e0e0 should be last) and then by created_at DESC
            # Since we can't easily sort by color value in SQL portably/cleanly for "completed last",
            # we will fetch all and sort in Python or do two queries.
            # Python sorting is easier for custom logic.
            notes = db.query(Note).filter(Note.is_deleted == False).all()
            
            # Detach first
            for note in notes:
                db.expunge(note)
                
            # Sort logic:
            # 1. Uncompleted first (color != #e0e0e0)
            # 2. Within each group, Created At DESC (Newest first)
            
            def sort_key(n):
                is_completed = (n.color == "#e0e0e0")
                # Tuple comparison: False (0) comes before True (1)
                # Timestamp: negate timestamp for descending order (or reverse whole list)
                return (is_completed, -n.created_at.timestamp())
            
            notes.sort(key=sort_key)
            
            return notes
        finally:
            db.close()

    def get_note(self, note_id):
        db = next(get_db())
        try:
            note = db.query(Note).filter(Note.id == note_id).first()
            if note:
                db.expunge(note)
            return note
        finally:
            db.close()

    def create_note(self, title, content, color="#FFF9E6"):
        db = next(get_db())
        try:
            new_note = Note(title=title, content=content, color=color)
            db.add(new_note)
            db.commit()
            db.refresh(new_note)
            
            # Log creation
            self.log_action(db, "create", title or "New Note")
            
            # Expunge to detach from session so it can be used after session closes
            db.expunge(new_note)
            return new_note
        finally:
            db.close()

    def update_note(self, note_id, title=None, content=None, color=None):
        db = next(get_db())
        try:
            note = db.query(Note).filter(Note.id == note_id).first()
            if note:
                old_color = note.color
                
                if title: note.title = title
                if content: note.content = content
                if color: note.color = color
                note.updated_at = datetime.now()
                db.commit()
                db.refresh(note)
                
                # Log completion (hacky check based on color change to grey)
                if color == "#e0e0e0" and old_color != "#e0e0e0":
                    self.log_action(db, "complete", note.title)
                # Log update (if not completion and title changed)
                elif title and title != "New Note" and color != "#e0e0e0":
                    # Only log significant updates if needed, maybe skip to avoid spam
                    pass
                
                db.expunge(note)
            return note
        finally:
            db.close()

    def delete_note(self, note_id):
        db = next(get_db())
        try:
            note = db.query(Note).filter(Note.id == note_id).first()
            if note:
                # Hard delete as requested for robust removal
                title = note.title
                db.delete(note)
                db.commit()
                
                self.log_action(db, "delete", title)
                return True
            return False
        except Exception as e:
            print(f"Error deleting note: {e}")
            db.rollback()
            return False
        finally:
            db.close()
        
    def restore_note(self, note_id):
        db = next(get_db())
        note = db.query(Note).filter(Note.id == note_id).first()
        if note:
            note.is_deleted = False
            db.commit()
            
            self.log_action(db, "restore", note.title)
            
            return True
        return False

    def permanent_delete_note(self, note_id):
        db = next(get_db())
        note = db.query(Note).filter(Note.id == note_id).first()
        if note:
            db.delete(note)
            db.commit()
            return True
        return False

    def log_action(self, db, action_type, content):
        if not content:
            content = "Empty Note"
        # Use local time for created_at to ensure UI shows correct Beijing Time (or system time)
        log = OperationLog(action_type=action_type, note_content=content, created_at=datetime.now())
        db.add(log)
        db.commit()

    def clear_all_logs(self):
        db = next(get_db())
        try:
            # Delete all logs
            db.query(OperationLog).delete()
            db.commit()
            return True
        except Exception as e:
            print(f"Error clearing logs: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    def get_logs(self):
        db = next(get_db())
        try:
            return db.query(OperationLog).order_by(OperationLog.created_at.desc()).all()
        finally:
            db.close()

    def get_logs_by_date(self, date_obj):
        db = next(get_db())
        try:
            # Filter by date range for the specific day
            start = datetime.combine(date_obj, datetime.min.time())
            end = datetime.combine(date_obj, datetime.max.time())
            return db.query(OperationLog).filter(
                OperationLog.created_at >= start,
                OperationLog.created_at <= end
            ).order_by(OperationLog.created_at.desc()).all()
        finally:
            db.close()
