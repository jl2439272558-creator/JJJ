from .database import get_db
from .models import WorkLog, Note
from sqlalchemy import func
import datetime

class StatisticsManager:
    def get_total_work_time(self, days=7):
        db = next(get_db())
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        result = db.query(func.sum(WorkLog.duration_minutes)).filter(WorkLog.date >= cutoff).scalar()
        return result if result else 0

    def get_notes_count(self):
        db = next(get_db())
        return db.query(Note).filter(Note.is_deleted == False).count()
        
    def get_weekly_stats(self):
        # Placeholder for more complex stats
        return {
            "total_time": self.get_total_work_time(7),
            "notes_count": self.get_notes_count()
        }
