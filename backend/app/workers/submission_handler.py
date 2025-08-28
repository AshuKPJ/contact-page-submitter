from datetime import datetime


class SubmissionHandler:
    def __init__(self, db):
        self.db = db

    def update(self, submission, status, **kwargs):
        submission.status = status
        submission.processed_at = datetime.utcnow()

        for key, value in kwargs.items():
            if hasattr(submission, key):
                setattr(submission, key, value)

        self.db.commit()
