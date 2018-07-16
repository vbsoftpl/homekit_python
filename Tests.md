# Testing

# Running unit tests

```bash
python3 -m unittest -v
```

```bash
coverage run -m unittest &&\
coverage html --omit=*/site-packages/*,tests/*
```