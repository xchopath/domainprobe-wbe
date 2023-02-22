# Domainprobe-WBE (Domainprobe Web-Based Environment)

## Installation

Clone repository
```
git clone https://github.com/xchopath/domainprobe-wbe
cd domainprobe-wbe/
```

**Note:** check your `.env` first before install.

Install with docker compose
```
sudo docker-compose up -d
```

## API Documentation

This environment will run at port `5002` with these endpoints below.

### Endpoint

#### Active scan

1. Subdomain scan
```
GET /api/subdomain/scan/<host>
```

2. Get the result of subdomain
```
GET /api/subdomain/result/<host>
```

3. List all subdomains
```
GET /api/subdomain/list
```

4. Domainprobe scan
```
GET /api/domainprobe/scan/<host>
```

5. Domainprobe result
```
GET /api/domainprobe/result/<host>
```

6. List of discovered domains 
```
GET /api/domainprobe/list
```

## F.A.Q

- Can connect to existing Redis & MongoDB?

Yes It can, adjust `docker-compose.yml` by removing from the stage and adjust `.env`.