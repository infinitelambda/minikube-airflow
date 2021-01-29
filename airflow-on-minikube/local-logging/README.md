# How to set up nfs logging

With this setup we create an NFS server and update our deployment.yml file
to make sure we mount the appropriate volumes to the scheduler and the web server.
Also in the dag docker image now we are exposing the log server port which allow us to read the logs.


These are the modifications what we had to apply to enable local logging.
We added the following code to the webserver and scheduler definition
in the deployment.yml file
```
volumeMounts:
  - name: pv-storage
    mountPath: /usr/local/airflow/logs
```

Added the following code snippet to the deployment.yml file.
After the scheduler container definition. (Right after the volumeMounts section)
```
volumes:
  - name: logs-persistent-storage
  persistentVolumeClaim:
    claimName: test-dynamic-volume-claim
```

## Deploy an NFS Server Provisioner
We need this to make sure we'll have our own nfs server which we can use
to create PersistentVolumeClaims
```
helm install stable/nfs-server-provisioner --set persistence.enabled=true,persistence.size=5Gi --generate-name
```

## Deploy the PersistentVolumeClaims
In the deployment script we are using a persistentVolumeClaim but to use that volume claim first we need to create it.
```
kubectl apply -f logging/persistent-volume-claim.yml
```