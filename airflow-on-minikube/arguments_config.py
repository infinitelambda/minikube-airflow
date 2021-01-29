ARGUMENTS = [
    {
        "command": "--deploy",
        "help": "Runs the deployment script",
        "action": "store_true",
    },
    {
        "command": "--helm_update",
        "help": "Rebuilds the dag img and change the image on the cluster.",
        "action": "store_true",
    },
    {
        "command": "--set_aws_access_id",
        "help": "Sets the AWS access key id.",
        "type": str,
        "action": "store",
    },
    {
        "command": "--set_aws_secret_key",
        "help": "Set the AWS secret access key.",
        "type": str,
        "action": "store",
    },
    {
        "command": "--path_local_dags",
        "help": "The absolute path to your DAGs which which you want to copy into the image.",
        "type": str,
        "action": "store",
    },
    {
        "command": "--path_project_folder",
        "help": "The absolute path to your local project folder which you want to copy into the image.",
        "type": str,
        "action": "store",
    },
    {
        "command": "--path_local_requirements",
        "help": "The absolute path to your requirements which you want to copy into the image.",
        "type": str,
        "action": "store",
    },
    {
        "command": "--clean_up",
        "help": "Deletes all the Kubernetes objects inside the development namspace.",
        "type": str,
        "action": "store_true",
    }
]