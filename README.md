## This is a test assigment 
- I've overridden the resolve_user method in the Query class to include a check for user permissions when viewing the user field.
- I've also customized the default GraphQL schema by adding a resolver that checks user permissions, ensuring only accessible fields are shown.

### Steps to launch tests: 

1. Create virtualenv

        python3 -m venv env
        source env/bin/activate 

2. Install requirements 
        
        pip install -r requirements.txt

3. Run tests

        python manage.py test
