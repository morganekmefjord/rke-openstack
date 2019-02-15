import sys
import os
import subprocess
import click
import docker
import logging
from distutils import dir_util
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from os import walk
from pkg_resources import iter_entry_points
from click_plugins import with_plugins
from distutils import dir_util

logging.basicConfig(level=logging.INFO)

DEFAULT_IMAGE = 'novella/rega:latest'

@click.group()
def main():
    """REGA is a tool for provisioning RKE clusters."""

@main.command('init')
@click.argument('dir')
@click.option('-I','--image', default=DEFAULT_IMAGE, envvar='REGA_PROVISIONER_IMG')
def init(dir,image):
    logging.info("""Initilaizing a new environment in {}""".format(dir))
    client = docker.from_env()
    client.images.pull(image)
    check_init_dir()
    create_deployment(dir)

@main.command('version')
@click.option('-I','--image', default=DEFAULT_IMAGE, envvar='REGA_PROVISIONER_IMG')
def version(image):
    logging.info("""REGA provisioner version is {}""".format(image))

@main.command('apply')
@click.option('-I','--image', default=DEFAULT_IMAGE, envvar='REGA_PROVISIONER_IMG',\
help='Applies the Terraform plan to spawn the desired resources')
def apply(image):
    #client.images.pull(image)
    logging.info("""Applying setup""")
    check_environment()

    run_in_container(['terraform init -plugin-dir=/terraform_plugins'
                      'terraform apply -auto-approve'], image)


@main.command('destroy')
@click.option('-I','--image', default=DEFAULT_IMAGE, envvar='REGA_PROVISIONER_IMG',\
help='Releses all resources available in the Terraform state')
def destroy(image):
    #client.images.pull(image)
    logging.info("""Destroying the infrastructure""")
    check_environment()

    run_in_container(['terraform destroy -force'], image)

@main.command('terraform')
@click.argument('extra_args')
@click.option('-I','--image', default=DEFAULT_IMAGE, envvar='REGA_PROVISIONER_IMG',\
help='Executes the terraform command in the provisioner container with the provided args')
def terraform(extra_args,image):
    #client.images.pull(image)
    logging.info("""Running terraform with arguments: {}""".format(extra_args))
    check_environment()

    run_in_container(['terraform {}'.format(extra_args)], image)


@main.command('openstack')
@click.argument('extra_args')
@click.option('-I','--image', default=DEFAULT_IMAGE, envvar='REGA_PROVISIONER_IMG',\
help='Executes the openstack command in the provisioner container with the provided args')
def openstack(extra_args,image):
    #client.images.pull(image)
    logging.info("""Running openstack with arguments: {}""".format(extra_args))

    run_in_container(['openstack {}'.format(extra_args)], image)


def run_in_container(commands, image, detach=True):
    client = docker.from_env()
    env    = list(filter_vars(os.environ))
    volume_mount = {os.getcwd(): {'bind': '/mnt/deployment/', 'mode': 'rw'}}
    container_wd = '/mnt/deployment/'

    assert type(commands) == type(list()), "First argument should be a list"

    commands_as_string = " && ".join(commands)
    runner = client.containers.run(
            image,
            volumes     = volume_mount,
            environment = env,
            working_dir = container_wd,
            entrypoint  = ['bash', '-c'],
            command     = f'"{commands}"',
            detach      = detach
    )

    for line in runner:
        print(line.decode())

def create_deployment(dir):
    """copy relevant files to new folder"""
    if os.path.exists('deployment-template'):
        dir_util.mkpath(dir)
        subprocess.call('cp -r deployment-template/* ./{}/'.format(dir), shell=True)
    else:
        sys.stderr.write("Error: deployment-template folder not found. Are you in the right directory?\n")
        sys.exit(1)

    if not os.path.isfile(dir + '/ssh_key.pub'):
        pu, pv = create_key_pair()
        with open(dir + '/ssh_key.pub', 'w') as key:
            key.write(pu)
        with open(dir + '/ssh_key', 'w') as key:
            key.write(pv)

def check_environment():
    if not os.environ.get('OS_AUTH_URL', False):
        sys.stderr.write("Error: You need to source the openstack credentials file\n")
        sys.exit(1)

    if not os.path.isfile('ssh_key.pub'):
        sys.stderr.write("Error: ssh_key not found. Are you in the right directory?\n")
        sys.exit(1)

    if not os.path.isfile('terraform.tfvars'):
        sys.stderr.write("Error: terraform.tfvars not found. Are you in the right directory?\n")
        sys.exit(1)

def check_init_dir():
    if not os.path.exists('deployment-template'):
        sys.stderr.write("Error: deployment-template folder not found. Are you in the right directory?\n")
        sys.exit(1)

def create_key_pair():
    key = rsa.generate_private_key(
        backend=crypto_default_backend(),
        public_exponent=65537,
        key_size=2048
    )
    private_key = key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.TraditionalOpenSSL,
        crypto_serialization.NoEncryption())
    public_key = key.public_key().public_bytes(
        crypto_serialization.Encoding.OpenSSH,
        crypto_serialization.PublicFormat.OpenSSH
    )
    return (public_key.decode('utf-8'), private_key.decode('utf-8'))

def filter_vars(seq):
   for key, val in seq.items():
       if key.startswith('TF_'): yield key+'='+val
       elif key.startswith('OS_'): yield key+'='+val
