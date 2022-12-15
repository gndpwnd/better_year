[Reference](https://docs.digitalocean.com/tutorials/app-deploy-flask-app/)

Env Vars

```bash
cat ~/Documents/env_vars/betteryear.txt
```

Build Command

```bash
gunicorn --worker-tmp-dir /dev/shm app:app
```