## Build the container
```
docker build -t webapp .
```

## Run the container
```
docker run -it --rm  --name 2pi  \
    -p 80:80 \
    -v /data/d/projects/other/2pi-financial/:/base \
    webapp
```

## Environment variables for production
```
export ENV=prod
export GOOGLE_ANALYTICS=xxxxx
export DATABASE_URI=xxxxx
```