from fabric.api import local, env, run, cd

env.hosts = ['fitmarkers@fitmarkers.com']
run_tests_command = 'python manage.py test fitmarkers'


def deploy(environment='production'):
    app_dir = '~/apps/fitmarkers'
    activate_venv = 'source venv/bin/activate && source .env && '

    local(run_tests_command)

    with cd(app_dir):
        run('git fetch')
        run('git reset --hard origin/master')
        run(activate_venv + 'pip install -r requirements.txt')
        run(activate_venv + run_tests_command)
        run(activate_venv + 'python manage.py collectstatic --noinput')
        run('sudo supervisorctl restart fitmarkers_web')
        run('sudo supervisorctl restart fitmarkers_celery')

def test():
    local(run_tests_command)
