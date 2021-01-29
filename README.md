# Production-like Airflow Development Environment on Minikube
This is a everything you need to deploy Airflow on minikube.

The default setup is using local logging with an NFS server.

Image names are: localhost:5000/base and localhost:5000/dag-img.

We are using local image registry.

The cli tool only helps with the AWS credentials setup and deployment related thing. For gcp auth there is a minikube add-on. Also the run minikube with local registry part should be done by you. After that open a new tab and run the following.

When you enable the registry addon you will get a message something like this:
```
Registry addon on with docker uses 55005 please use that instead of default 5000
```
In this case you should use the 55005 in the next command
```
docker run --rm -it --network=host alpine ash -c "apk add socat && socat TCP-LISTEN:5000,reuseaddr,fork TCP:$(minikube ip):paste-port-number-here"
```
Please note that this command should run in a separate terminal window in an interactive way !! Otherwise you won't be able to push images to this
local registry.

Airflow UI password can be found in helm/files/secrets/airflow/AFPW

## Run Minikube with local registry

Start Minikube in the default way
```
minikube start --insecure-registry "10.0.0.0/24"
```
Enable registry add-on
```
minikube addons enable registry
```

## From here you can copy files and set AWS creds manually or use the cli tool

### CLI Usage
Go to the airflow-on-minikube folder in the terminal and type
```
python main.py --help
```
With the help of the cli tool you can set aws creds, deploy everything with the base setup, copy dag/project/requirements files and change image on the cluster after you modified any of your project/dag files with only one command.

Important to check the copied files especially the dag files since this deployment created a namespace called development and deploys everything there. Which mean you have to change the namespace in the KubernetesPodOperator. Also now the image is called: localhost:5000/dag-img.


### Set up everyhting by hand

Go to the docker/base and build the base img after that go to docker/dag and build the dag image

Before you build the your dag image don't forget to add/change the first line to this: FROM localhost:5000/base
```
cd airflow-on-minikube/docker/base
docker build -t localhost:5000/base .
cd ../dag
docker build -t localhost:5000/dag-img .
```
After enabling the registry add-on you can see a port number that will be this var {coming from current setup}. Important note: this only works for mac. For windows please check out this page: https://minikube.sigs.k8s.io/docs/handbook/registry/
```
docker run --rm -it --network=host alpine ash -c "apk add socat && socat TCP-LISTEN:5000,reuseaddr,fork TCP:$(minikube ip):{coming from current setup}"
```
Push the images to the local registry
```
docker push localhost:5000/base
docker push localhost:5000/dag-img
```

## Create namespace for dev
```
kubectl create namespace development
```
Deploy the PostgreSQL service to create the metadat-databse for Airflow
```
kubectl apply -f postgres/ --namespace development
```

## Logging

Choose according to your preference. By default the local logging option is used since this is a development environment. In case you want to use Cloud logging please check the local-logging folder readme file to delete the mentioned code parts from the deployment.yml file and also modify the airflow.cfg file inside the docker/base folder.


### 1.) PersistentVolume logging
This is what we use by default. For the setup and the how to check the local-logging folder readme file.

### 2.) Cloud storage logging
Create the MyLogConn variable on the Airflow UI, use the same name what is inside the airflow.cfg file.
#### FOR AWS LOGGING ###
conn id: MyLogConn
conn type: S3
host: bucket name
login: AWS_ACCESS_KEY_ID
password: AWS_SECRET_ACCESS_KEY

#### FOR GCP
var name: MyLogConn
conn type: Google Cloud Platform
project id: gcp project name
scopes: https://www.googleapis.com/auth/cloud-platform
Keyfile JSON: the service_account.json  (upload the actual json file)

### 3.) Install Lens the Kubernetes IDE
With Lens you can connect to any of your Kubernetes clusters easily and you just have to click on the pod (Airflow task in this case) and click on the first icon from the left in the top right corner. After that in the built-in terminal you'll see the logs.

## The easy way to give cloud access to your scripts
### For GCP
There is an available add-on to help you setting up GCP auth. Here is the link: https://minikube.sigs.k8s.io/docs/handbook/addons/gcp-auth/

### For AWS
Add these to your dag files
```
secret_id = os.getenv("AWS_ACCESS_KEY_ID", None)
secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", None)

env_vars={
        'AWS_ACCESS_KEY_ID': variable_id,
        'AWS_SECRET_ACCESS_KEY': variable_secret_key}
```
And put your credentials into the helm/files/secrets/airflow appropriate files. (AWS_ACCESS_KEY_ID, AWS_SECRET_KEY)

## Deploy airflow
Based on the default settings deploy nfs server provisioner
```
helm install nfs-provisioner stable/nfs-server-provisioner --set persistence.enabled=true,persistence.size=5Gi --namespace development
```
Deploy Persistent volume Claim
```
kubectl apply -f local-logging/persistent-volume-claim.yml  --namespace development
```

cd into minikube-airflow/helm and run the following cmd
```
helm install airflow-minikube-dev . --namespace development
```

Run the following cmd and copy-paste the url to your browser
```
minikube service --url airflow --namespace development
```
Airflow UI password can be found in helm/files/secrets/airflow/AFPW

## Deploy new image to our cluster
### Helm upgrade
First you have to give some unique tag to your new dag image

Example:
```
docker build -t localhost:5000/dag-img:modified .
docker tag localhost:5000/dag-img:modified localhost:5000/dag-img:latest
docker push localhost:5000/dag-img:modified
docker push localhost:5000/dag-img:latest
```
After this you have to change the image in you cluster
```
helm upgrade airflow-minikube-dev helm/ --install --wait --atomic --set dags_image.tag=modified
```


## Clean up
```
helm uninstall airflow-minikube-dev --namespace development
helm uninstall nfs-provisioner --namespace development
kubectl delete namespace development
```
## In case of clean_up command doesn't work
It is possible the while deleting a namespace it's stuck at a terminating phase. When it happens just use run
```
kubectl get all --namespace development
```
adn use the pod/podname of the problematic pod and paste it
```
kubectl delete pod/podname --grace-period=0 --force --namespace development
```
