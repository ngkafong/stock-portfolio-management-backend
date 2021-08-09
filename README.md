### run dev:
```
uvicorn main:app --reload --port 8080
```
### run prod:
systemctl start backend
systemctl enable backend
systemctl start nginx
systemctl enable nginx

### setup nginx

```
# /etc/nginx/nginx.conf

user    root;
worker_processes  1;

events {
    worker_connections  1024;
}


http {
    include       mime.types;
    default_type  application/octet-stream;

    sendfile        on;

    keepalive_timeout  65;


    server {
        server_name  backend.ngkafong.nets.hk backend.ngkafong.tk;

        location /api/ {
            proxy_pass http://unix:/root/richardng/stock-portfolio-management-backend/backend.sock:/;
        }
                # redirect server error pages to the static page /50x.html
        #

        error_page   500 502 503 504  /50x.html;

        location = /50x.html {
            root   html;
        }
    }
}
```

```
# /etc/systemd/system/backend.service
[Unit]
Description=Gunicorn daemon to serve backend
After=network.target

[Service]
WorkingDirectory=/root/richardng/stock-portfolio-management-backend/
ExecStart=/usr/local/bin/gunicorn main:app -k uvicorn.workers.UvicornWorker --bind unix:backend.sock -m 007

[Install]
WantedBy=multi-user.target
```

https://query2.finance.yahoo.com/v1/finance/search?q=soxq&quotesCount=4&newsCount=0&listsCount=0
