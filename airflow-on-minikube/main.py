#!/usr/bin/python3
import os, sys
import argparse
from arguments_config import ARGUMENTS
from run_shell_cmd import run_shell_command


def get_random_tag_name():
    first_group=('magic','fantastic','funny', 'smart', 'lazy', 'big')
    last_group=('-unicorn','-duck','-giraffe', '-bear', '-lama', 'lion')

    group=random.choice(first_group) + random.choice(last_group)
    return group



def deploy_airflow():
    """
    Creates development namespace
    Build images
    Deploy psql db, nfs server and volume claim
    Deploy airflow chart
    """
    create_namespace = "kubectl create namespace development"
    build_base = "docker build --no-cache -t localhost:5000/base ."
    build_dag = "docker build --no-cache -t localhost:5000/dag-img ."
    push_base = "docker push localhost:5000/base"
    push_dag = "docker push localhost:5000/dag-img"
    deploy_psql = "kubectl apply -f postgres/ --namespace development"
    deploy_nfs = "helm install nfs-provisioner stable/nfs-server-provisioner --set persistence.enabled=true,persistence.size=5Gi --namespace development"
    deploy_pvc = "kubectl apply -f local-logging/persistent-volume-claim.yml  --namespace development"
    deploy_airflow_chart = "helm install airflow-minikube-dev .  --namespace development"
    print("=====================================================================================")
    print("###  CREATING NEMASPACE DEVELOPMENT  ###")
    print("=====================================================================================")
    run_shell_command(create_namespace)
    print("=====================================================================================")
    print("###  BUILDING BASE DOCKER IMAGE  ###")
    print("=====================================================================================")
    run_shell_command("cd docker/base", build_base)
    print("=====================================================================================")
    print("###  BUILDING DAG DOCKER IMAGE  ###")
    print("=====================================================================================")
    run_shell_command("cd docker/dag", build_dag)
    print("=====================================================================================")
    print("###  PUSH BASE IMAGE TO LOCAL REGISTRY  ###")
    print("=====================================================================================")
    run_shell_command(push_base)
    print("=====================================================================================")
    print("###  PUSH DAG IMAGE TO LOCAL REGISTRY  ###")
    print("=====================================================================================")
    run_shell_command(push_dag)
    print("=====================================================================================")
    print("###  DEPLOY POSTGRESQL DB  ###")
    print("=====================================================================================")
    run_shell_command(deploy_psql)
    print("=====================================================================================")
    print("###  DEPLOY NFS SERVER PROVISONER  ###")
    print("=====================================================================================")
    run_shell_command(deploy_nfs)
    print("=====================================================================================")
    print("###  DEPLOY PERSISTENT VOLUME CLAIM  ###")
    print("=====================================================================================")
    run_shell_command(deploy_pvc)
    print("=====================================================================================")
    print("###  DEPLOY CUSTOM AIRFLOW HELM CHART  ###")
    print("=====================================================================================")
    run_shell_command("cd helm", deploy_airflow_chart)


def delete_namespace():
    """
    Deletes everything inside the development namespace
    A quick clean up.
    """
    helm_uninstall_airflow = "helm uninstall airflow-minikube-dev  --namespace development"
    helm_uninstall_nfs = "helm uninstall nfs-provisioner --namespace development"
    delete = "kubectl delete namespace development"
    print("=====================================================================================")
    print("###  DELETE DEVELOPMENT NAMESPACE AND EVERY OBJECT IN IT  ###")
    print("###  CLEANING UP THE ENVIRONMENT  ###")
    print("=====================================================================================")
    run_shell_command(helm_uninstall_airflow)
    run_shell_command(helm_uninstall_nfs)
    run_shell_command(delete)


def set_aws_secret_id(access_id):
    """
    This function sets the AWS secret id for cloud auth.
    :param access_id: str
    :return:
    """
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, "helm/files/secrets/airflow/AWS_ACCESS_KEY_ID")
    with open(path, "w") as file:
        file.write(access_id)
    file.close()


def set_aws_secret_key(secret_key):
    """
    This function sets the AWS secret id for cloud auth.
    :param secret_id: the actual aws secret id
    :param secret_key: str
    :return:
    """
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, "/helm/files/secrets/airflow/AWS_SECRET_KEY")
    with open(path, "w") as file:
        file.write(secret_key)
    file.close()


def update_helm_chart():
    """
    Rebuilds the dag image and after pushing it to local registry
    it changes the image in the minikube cluster
    """
    # generate unique tag
    tag = get_random_tag_name()

    build = "docker build -t localhost:5000/dag-img:{tag} .".format(tag=tag)
    tag_with_latest = "docker tag localhost:5000/dag-img:{tag} localhost:5000/dag-img:latest".format(tag=tag)
    push_new_tag = "docker push localhost:5000/dag-img:{tag}".format(tag=tag)
    push_latest_tag = "docker push localhost:5000/dag-img:latest"
    update = "helm upgrade airflow-minikube-dev helm/ --install --atomic --namespace development --set dags_image.tag={tag}".format(tag=tag)
    print("=====================================================================================")
    print("###  REBUILD DAG IMAGE WITH TAG {tag}  ###".format(tag=tag))
    print("=====================================================================================")
    run_shell_command("cd docker/dag", build)
    run_shell_command(tag_with_latest)
    print("=====================================================================================")
    print("###  PUSH DAG IMAGE WITH TAG {tag} TO LOCAL REGISTRY ###".format(tag=tag))
    print("=====================================================================================")
    run_shell_command(push_new_tag)
    run_shell_command(push_latest_tag)
    print("=====================================================================================")
    print("###  CHANGE IMAGE IN THE CLUSTER TO DAG IMAGE WITH TAG {tag}  ###".format(tag=tag))
    print("=====================================================================================")
    run_shell_command(update)


def copy_project_files(local_path):
    """
    Copies the whole content of the given local folder
    into the minikube project folder
    :param local_path: str
    :return:
    """
    my_path = os.path.abspath(os.path.dirname(__file__))
    dags_path = my_path + "/docker/dag/project/"
    cmd = "cp -a {local_path}/ {my_path}".format(local_path=local_path, my_path=dags_path)
    run_shell_command(cmd)
    print("=====================================================================================")
    print("###  LOCAL PROJECT FILES COPIED INTO airflow-on-minikube/docker/dag/project/  ###")
    print("=====================================================================================")


def copy_dag_files(local_path):
    """
    Copies the whole content of the given local DAGs folder
    into the minikube airflow_dags folder
    :param local_path: str
    :return:
    """
    my_path = os.path.abspath(os.path.dirname(__file__))
    dags_path = my_path + "/docker/dag/airflow_dags/"
    cmd = "cp -a {local_path} {my_path}".format(local_path=local_path, my_path=dags_path)
    run_shell_command(cmd)
    print("=====================================================================================")
    print("###  LOCAL DAG FILES COPIED INTO airflow-on-minikube/docker/dag/airflow_dags/  ###")
    print("###  CHECK YOUR DAG FILES THEY MAY NEED SOME MODIFICATION (image_name, namespace ...)")
    print("=====================================================================================")


def append_to_requirements(local_path):
    """
    Appends the local project requirements to the
    minikube dpeloyment requirements
    :param local_path: str
    :return:
    """
    my_path = os.path.abspath(os.path.dirname(__file__))
    requirements_path = my_path + "/docker/dag/requirements.txt"
    minikube_requirement = open(requirements_path, 'a+')
    local_requirement = open(local_path, 'r')

    # appending the contents of the second file to the first file
    minikube_requirement.write(local_requirement.read())
    minikube_requirement.close()
    local_requirement.close()
    print("=====================================================================================")
    print("Note that your requirements were now appended to the default one.")
    print("Check the requirements file in airflow-on-minikube-docker-dag.")
    print("To avoid any duplications or conflicts.")
    print("=====================================================================================")


def mini_deployer():
    # Define the program description
    description = "This is MiniDeployer - it will automatize your Apache Airflow DEV deployment"

    # Setup Argument Parser which will handle parsing any incoming commands and values
    parser = argparse.ArgumentParser(description=description)

    for argument in ARGUMENTS:
        parser.add_argument(
            argument["command"], help=argument["help"], action=argument["action"]
        )

    args = parser.parse_args()

    if args.set_aws_access_id:
        set_aws_secret_id(args.set_aws_access_id)
    elif args.set_aws_secret_key:
        set_aws_secret_key(args.set_aws_secret_key)
    elif args.helm_update:
        update_helm_chart()
    elif args.deploy:
        deploy_airflow()
    elif args.path_project_folder:
        copy_project_files(args.path_project_folder)
    elif args.path_local_dags:
        copy_dag_files(args.path_local_dags)
    elif args.path_local_requirements:
        append_to_requirements(args.path_local_requirements)
    elif args.clean_up:
        delete_namespace()


if __name__ == "__main__":
    mini_deployer()
