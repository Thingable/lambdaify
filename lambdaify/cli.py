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
@click.option('--virtual_directory', '-v', help="Directory to create virtual environment (Default: Project dir")
@click.option('--python', default='/usr/local/bin/python3', help="Path to python executable for virtualenv (Default: /usr/local/bin/python3')")
@click.pass_context
def start(ctx, project, project_directory, python, virtual_directory):
    """Create a project and a virtual environment"""
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(os.path.dirname(abspath))
    try:
        os.mkdir(project)
        subprocess.call('cp -r {}/project-template/ {}/{}'.format(dname, project_directory, project), shell=True)

        if not virtual_directory:
            virtual_directory = './{}'.format(project)
        ctx.invoke(virtualify, virtual_directory=virtual_directory, project=project)

        os.chdir('./{}'.format(project))
        print(os.getcwd())
        os.putenv('LAMBDAIFY_PROJECT', project)
        os.putenv('LAMBDAIFY_PROJECT_DIR', os.getcwd())

        click.echo("Created the project '{}' and its {} environment. Standing by to Lambdaify.".format(project, python))
    except Exception as err:
        click.echo('Failed to startify {}: {}'.format(project, err))


@main.command()
@click.option('--virtual_directory', '-v', default='./', help="Directory to create virtual environment")
@click.option('--python', default='/usr/local/bin/python3', help="Path to python executable for virtualenv (Default: /usr/local/bin/python3)")
def virtualify(virtual_directory, python, project=''):
    """Create a virtualenv for a current project"""
    subprocess.call('virtualenv --python={} {}/.{}_venv'.format(python, virtual_directory, project), shell=True)
    click.echo("Run 'source {}{}venv/bin/activate' to use {}'s virtualenv".format(virtual_directory, project, project))

@main.command()
def stage():
    """Create a staging directory in the virtual env"""
    click.echo('Stagifying project.')
    virtual_directory = os.environ['VIRTUAL_ENV']
    project_directory = os.environ['PWD']

    click.echo('\tShipping the packages')
    os.chdir(virtual_directory)
    subprocess.call('rm -rf stageify', shell=True)
    os.mkdir('stageify')
    subprocess.call('cp -r {}/lib/python3.6/site-packages/ ./stageify/'.format(virtual_directory), shell=True)

    click.echo('\tHunting for eggs.')
    stage_dir_items = os.listdir('./stageify')
    eggs = [item for item in stage_dir_items if item.endswith('egg-link')]
    egg_links = []
    for egg in eggs:
        click.echo('\t\t{}'.format(egg))
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
            subprocess.call('cp -r {}/{} ./stageify/'.format(link, file), shell=True)
            click.echo('\t\t- Copied {}/{} to staging area'.format(link, file))

    click.echo('\tArming your lasers.')
    os.chdir(project_directory)
    subprocess.call('find . -name {} -prune -o -print0 | cpio -pmd0 {}/stageify/'.format(os.path.basename(virtual_directory), virtual_directory), shell=True)

    click.echo('Staging complete.')

@main.command()
@click.option('--lambda_handler', '-h', default='app.lambda_handler', help='The handler to be called (Default: app.lambda_handler)')
@click.option('--detail', '-d', help='A JSON string to be sent to the event parameter')
def test(lambda_handler, detail):
    """Test your project in a lambda docker clone"""
    subprocess.call('docker run --rm -v "$VIRTUAL_ENV/stageify":/var/task lambci/lambda:python3.6 {} \'{}\''.format(lambda_handler, detail), shell=True)

@main.command()
def zip():
    """Create a zip file to upload to lambda"""
    venv = os.environ['VIRTUAL_ENV']
    current_directory = os.getcwd()
    os.chdir('{}/stageify/'.format(venv))
    subprocess.call('zip -r {}/lambdaify.zip .'.format(current_directory), shell=True)


