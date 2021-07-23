### run dev: 
```
uvicorn main:app --reload --port 8080
```
### run prod:
```
gunicorn main:app -w 2 -k uvicorn.workers.UvicornWorker -b :8080 --access-logfile logs/access_log 
```

## kill prod:
```
pkill -f gunicorn
```

### port tunneling:
```
nohup ngrok http 8080 --log=stdout > logs/ngrok.log &
```

TODO List:

construct demo data.

https://query2.finance.yahoo.com/v1/finance/search?q=soxq&quotesCount=4&newsCount=0&listsCount=0
