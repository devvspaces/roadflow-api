import os

from decouple import config
from fabric import Connection, task
from invoke import Exit

# You can set these as environment variables for security
HOST = config('SERVER_HOST')
USER = config('SERVER_USER')
PROJECT_DIR = f'/home/{USER}/roadflow-api'
PASSWORD = config('SERVER_PASS')

@task
def deploy(ctx):
    """
    Deploy the latest changes to the server
    """
    try:
        # Create connection
        conn = Connection(
            HOST,
            user=USER,
            connect_kwargs={
                "password": PASSWORD
            }
        )
        
        with conn.cd(PROJECT_DIR):
            
            # Update dependencies
            print("Updating dependencies...")
            with conn.prefix('source ./venv/bin/activate'):  # Adjust path as needed
                
                print("Installing dependencies...")
                conn.run('pip install -r requirements.txt')
                
                # Backup database (optional)
                print("Creating database backup...")
                conn.run('python ./src/manage.py dumpdata > backup.json')
                
                
                # Pull latest code
                print("Pulling latest code...")
                conn.run('git pull origin dev')
            
                
                # Collect static files
                print("Collecting static files...")
                conn.run('python ./src/manage.py collectstatic --noinput')
                
                # Run migrations
                print("Running migrations...")
                conn.run('python ./src/manage.py migrate')
            
            # Restart Gunicorn
            print("Restarting Gunicorn...")
            conn.sudo('systemctl restart roadflow')
            
            print("Deployment successful!")
            
    except Exception as e:
        print(f"Deployment failed: {str(e)}")
        raise Exit(f"Deployment failed: {str(e)}")

@task
def rollback(ctx):
    """
    Rollback to the previous version if something goes wrong
    """
    conn = Connection(host=HOST, user=USER)
    with conn.cd(PROJECT_DIR):
        conn.run('git reset --hard HEAD^')
        with conn.prefix('source ../venv/bin/activate'):
            conn.run('python manage.py migrate')
        conn.sudo('systemctl restart gunicorn')