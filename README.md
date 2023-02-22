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

1. Subdomain discovery
```
/api/domainprobe/subdomain/<host>
```

2. Domain probing (DNS & HTTP)
```
/api/domainprobe/probe/<host>
```

3. Get all discovered domains
```
/api/domainprobe/domains
```

## F.A.Q

- Can connect to existing Redis & MongoDB?

Yes It can, adjust `docker-compose.yml` by removing from the stage and adjust `.env`.