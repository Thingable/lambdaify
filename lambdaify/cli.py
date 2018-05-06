import os
import subprocess
import click

@click.group()
#@click.option('--verbose', '-v', is_flag=True, help="Enables verbose output (not implemented)")
def main():
    pass

@main.command()
@click.option('--project', '-p', default="lambdaify-project", help="Name of the project. (Default: 'Lambdaify')")
@click.option('--project_directory', '-d', default='./', help="Directory to create project")
@click.option('--virtual_directory', '-v', default='./', help="Directory to create virtual environment")
@click.option('--python', default='/usr/local/bin/python3', help="Path to python executable for virtualenv (Default: /usr/local/bin/python3')")
@click.pass_context
def start(ctx, project, project_directory, python, virtual_directory):
    """Create a project and a virtual environment"""
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(os.path.dirname(abspath))
    try:
        os.mkdir(project)
        subprocess.call('cp -r {}/project-template/ {}/{}'.format(dname, project_directory, project), shell=True)
        ctx.forward(virtualify)
        click.echo("Created the project '{}' and its {} environment. Standing by to Lambdaify.".format(project, python))
    except Exception as err:
        click.echo('Failed to startify {}: {}'.format(project, err))

    os.chdir('./{}'.format(project))
    print(os.getcwd())
    os.putenv('LLAMBDAIFY_PROJECT', project)
    os.putenv('LAMBDAIFY_PROJECT_DIR', os.getcwd())

@main.command()
@click.option('--virtual_directory', '-v', default='./', help="Directory to create virtual environment")
@click.option('--python', default='/usr/local/bin/python3', help="Path to python executable for virtualenv (Default: /usr/local/bin/python3)")
def virtualify(virtual_directory, python, project='', project_directory=''):
    """Create a virtualenv for a current project"""
    os.mkdir('{}{}_venv'.format(virtual_directory, project))
    subprocess.call('virtualenv --python={} {}{}_venv'.format(python, virtual_directory, project), shell=True)
    click.echo("Run 'source {}{}_venv/bin/activate' to use {}'s virtualenv".format(virtual_directory, project, project))

@main.command()
def stage():
    """Create a staging directory in the virtual env"""
    click.echo('Stagifying project.')
    virtual_directory = os.environ['VIRTUAL_ENV']
    project_directory = os.environ['PWD']
    os.chdir(virtual_directory)
    subprocess.call('rm -rf stageify', shell=True)
    os.mkdir('stageify')
    subprocess.call('cp -r {}/lib/python3.6/site-packages/ ./stageify/'.format(virtual_directory), shell=True)
    subprocess.call('cp -r {}/ ./stageify/'.format(project_directory), shell=True)
    click.echo('Hunting for eggs.')
    stage_dir_items = os.listdir('./stageify')
    #os.chdir('./stageify')
    eggs = [item for item in stage_dir_items if item.endswith('egg-link')]
    egg_links = []
    for egg in eggs:
        print(egg)
        f = open('./stageify/{}'.format(egg), 'r')
        egg_links.append(f.readline().rstrip('\n'))
        f.close()
    for link in egg_links:
        egg_info = [item for item in os.listdir('{}'.format(link)) if item.endswith('egg-info')]
        f = open('{}/{}/top_level.txt'.format(link, egg_info[0]), 'r')
        top_level_files = f.readlines()
        f.close()
        for file in top_level_files:
            file = file.rstrip('\n')
            print('cp -r {}/{} ./stageify/'.format(link, file))
            subprocess.call('cp -r {}/{} ./stageify/'.format(link, file), shell=True)




@main.command()
@click.option('--lambda_handler', '-h', default='app.lambda_handler', help='The handler to be called (Default: app.lambda_handler)')
def test(lambda_handler):
    """Test your project in a lambda docker clone"""
    subprocess.call('docker run --rm -v "$VIRTUAL_ENV/stageify":/var/task lambci/lambda:python3.6 {}'.format(lambda_handler), shell=True)

@main.command()
def zip():
    """Create a zip file to upload to lambda"""
    venv = os.environ['VIRTUAL_ENV']
    current_directory = os.getcwd()
    os.chdir('{}/stageify/'.format(venv))
    subprocess.call('zip -r {}/lambdaify.zip .'.format(current_directory), shell=True)


