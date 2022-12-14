
[Reference](https://docs.digitalocean.com/tutorials/app-deploy-flask-app/)

Build Command

```bash
gunicorn --worker-tmp-dir /dev/shm app:app
```