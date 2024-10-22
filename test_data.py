from app import create_app
from extensions import db
from models import User, Task, GeneratedEmail, EmailEvent
from datetime import datetime, timedelta
import random

def create_test_data():
    app = create_app()
    with app.app_context():
        # Create test user
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            test_user = User(username='testuser', email='test@example.com')
            test_user.set_password('testpass123')
            db.session.add(test_user)
            db.session.commit()

        # Create some test tasks
        tasks = []
        for i in range(5):
            task = Task(
                description=f'Test Task {i+1}',
                email=f'recipient{i+1}@example.com',
                recipient=f'Recipient {i+1}',
                user_id=test_user.id
            )
            db.session.add(task)
            db.session.commit()
            tasks.append(task)

        # Create test emails with varying metrics
        for i, task in enumerate(tasks):
            sent_date = datetime.utcnow() - timedelta(days=random.randint(0, 25))
            email = GeneratedEmail(
                task_id=task.id,
                content=f'Test email content {i+1}',
                user_id=test_user.id,
                subject=f'Test Email Subject {i+1}',
                status='sent',
                sent_at=sent_date,
                opens=random.randint(5, 20),
                clicks=random.randint(2, 10),
                replies=random.randint(0, 5),
                bounces=random.randint(0, 1)
            )
            db.session.add(email)
            
            # Add some email events
            for _ in range(email.opens):
                event = EmailEvent(
                    email_id=email.id,
                    event_type='open',
                    timestamp=sent_date + timedelta(hours=random.randint(1, 48)),
                    event_metadata={'device': random.choice(['mobile', 'desktop'])}
                )
                db.session.add(event)
            
            for _ in range(email.clicks):
                event = EmailEvent(
                    email_id=email.id,
                    event_type='click',
                    timestamp=sent_date + timedelta(hours=random.randint(1, 48)),
                    event_metadata={'link': f'http://example.com/link{random.randint(1,3)}'}
                )
                db.session.add(event)
            
            db.session.commit()

if __name__ == '__main__':
    create_test_data()
