# Influencer Engagement and Sponsorship Coordinating Platform

## Description
It's a platform to connect Sponsors and Influencers so that sponsors can get their product/service advertised and influencers can get monetary benefit.

## Frameworks used
- Flask for application code
- Jinja2 templates + Bootstrap for HTML generation and styling
- SQLite for data storage

## How to run the application

1. Clone the repository
2. Create a virtual environment
3. Install the dependencies 
```bash
pip install -r requirements.txt
```

4. Export .env variables
```bash
source .env
```

5. Init the database (For first time only)
```bash
flask init-db
```

6. Run the migration (For first time only)
```bash
flask db migrate
flask db upgrade
```

7. Run the application
```bash
python manage.py run
```

8. Create admin user
```bash
python manage.py create-admin
```

9. Open the browser and go to `http://localhost:5000`
