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
        
        # Configure sudo to use the same password
        conn.config.sudo.password = PASSWORD
        
        with conn.cd(PROJECT_DIR):
            # Pull latest code
            print("Pulling latest code...")
            conn.run('git pull origin dev')
                
            with conn.prefix('source ./venv/bin/activate'):  # Adjust path as needed
                # Update dependencies
                print("Installing dependencies...")
                conn.run('pip install -r requirements.txt')
            
                # Run migrations
                print("Running migrations...")
                conn.run('python ./src/manage.py migrate')
            
        # Restart Gunicorn
        print("Restarting roadflow...")
        conn.sudo('systemctl restart roadflow', pty=True)
        
        print("Deployment successful!")
            
    except Exception as e:
        print(f"Deployment failed: {str(e)}")
        raise Exit(f"Deployment failed: {str(e)}")

@task
def upload(ctx, filename, target_dir=None):
    """
    Upload file to the server
    Usage: fab upload file1 [target_dir=path]
    Example: fab upload .env
            fab upload .env target_dir=configs
    """
    conn = Connection(
        HOST,
        user=USER,
        connect_kwargs={
            "password": PASSWORD
        }
    )

    try:
        # Default target directory if none specified
        if target_dir is None:
            target_dir = f'{PROJECT_DIR}/src'
        else:
            target_dir = f'{PROJECT_DIR}/{target_dir}'
            
        with conn.cd(target_dir):
            print(f"Uploading {filename} to {target_dir}...")
            if os.path.exists(filename):
                conn.put(filename, target_dir)
                print(f"Successfully uploaded {filename}")
            else:
                print(f"Error: {filename} not found in local directory")
                    
    except Exception as e:
        print(f"Upload failed: {str(e)}")