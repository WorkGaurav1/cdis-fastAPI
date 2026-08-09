## Security Checklist

## 1. Apache Hardening Checklist (Ubuntu / Debian)

| S. No. | Issue                                                        | Solution                                                                                                                | Test                                                                          | File Used (Absolute Path)                     |                         |
| ------ | ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | --------------------------------------------- | ----------------------- |
| 1      | Disable Directory Listing                                    | Add:`<br><Directory /var/www/>``<br>Options -Indexes``<br></Directory>``<br>sudo systemctl restart apache2`           | Visit directory without index → 403                                          | /etc/apache2/apache2.conf                     |                         |
| 2      | Disable TRACE Method                                         | `TraceEnable Off`                                                                                                     | `curl -X TRACE http://server-ip`                                            | /etc/apache2/apache2.conf                     |                         |
| 3      | Restrict HTTP Methods                                        | `<LimitExcept GET POST HEAD><br>``Require all denied<br>``</LimitExcept>`                                             | `curl -X PUT http://server-ip`                                              | /etc/apache2/apache2.conf                     |                         |
| 4      | Enable Security Headers                                      | `Header always set X-Frame-Options "DENY"<br>``Header always set X-Content-Type-Options "nosniff"`                    | `curl -I http://server-ip`                                                  | /etc/apache2/apache2.conf                     |                         |
| 5      | Enable HSTS                                                  | `Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"`                                   | `curl -I https://server-ip`                                                 | /etc/apache2/apache2.conf                     |                         |
| 6      | Disable Access to .ht\* Files                                | `<Files ".ht*"><br>``Require all denied<br>``</Files>`                                                                | Access `.htaccess` → 403                                                   | /etc/apache2/apache2.conf                     |                         |
| 7      | Limit Request Size                                           | `LimitRequestBody 10485760`                                                                                           | Upload >10MB                                                                  | /etc/apache2/apache2.conf                     |                         |
| 8      | Configure Timeout                                            | `Timeout 60`                                                                                                          | `grep Timeout apache2.conf`                                                 | /etc/apache2/apache2.conf                     |                         |
| 9      | Hide Backend Headers                                         | `Header unset X-Powered-By`                                                                                           | `curl -I http://server-ip`                                                  | /etc/apache2/apache2.conf                     |                         |
| 10     | Set Proper Log Permissions                                   | `chmod 640 /var/log/apache2/*`                                                                                        | `ls -l /var/log/apache2/`                                                   | /var/log/apache2/                             |                         |
| 11     | Disable Server Signature                                     | `ServerSignature Off`                                                                                                 | `curl -I http://server-ip`                                                  | /etc/apache2/conf-available/security.conf     |                         |
| 12     | Disable Server Tokens                                        | `ServerTokens Prod`                                                                                                   | `curl -I http://server-ip`                                                  | /etc/apache2/conf-available/security.conf     |                         |
| 13     | Enable ModSecurity (WAF)                                     | `sudo apt install libapache2-mod-security2<br>``sudo a2enmod security2`                                               | Check audit log                                                               | /etc/apache2/mods-enabled/security2.conf      |                         |
| 14     | Disable Unused Ports                                         | Remove unused `Listen` directives                                                                                     | `netstat -tulnp                                                               | grep apache2`                                 | /etc/apache2/ports.conf |
| 15     | Disable Open Proxy                                           | `ProxyRequests Off`                                                                                                   | Attempt proxy request                                                         | /etc/apache2/mods-available/proxy.conf        |                         |
| 16     | Disable Unused Modules                                       | `sudo a2dismod status autoindex include`                                                                              | `apachectl -M`                                                              | /etc/apache2/mods-enabled/                    |                         |
| 17     | Disable Unused Virtual Hosts                                 | `sudo a2dissite 000-default.conf`                                                                                     | `apachectl -S`                                                              | /etc/apache2/sites-enabled/000-default.conf   |                         |
| 18     | Enable mod_evasive                                           | `sudo apt install libapache2-mod-evasive<br>``sudo a2enmod evasive`                                                   | Stress test                                                                   | /etc/apache2/mods-available/evasive.conf      |                         |
| 19     | Enforce Strong SSL/TLS                                       | `SSLProtocol -all +TLSv1.2 +TLSv1.3<br>``SSLCipherSuite HIGH:!aNULL:!MD5`                                             | `nmap --script ssl-enum-ciphers -p 443`                                     | /etc/apache2/sites-available/default-ssl.conf |                         |
| 20     | Block IP access - As the SSL certificate does not work on IP | `RewriteEngine On<br>``RewriteCond %{HTTP_HOST} ^[0-9.]+$<br>`` RewriteRule ^ - [F,L]`                                | ---                                                                           | /etc/apache2/sites-enabled/enabled-site.conf  |                         |
| 21     | Redirect HTTP to HTTPS                                       | Rewrite rule configuration `RewriteCond %{HTTPS} off<br>``RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]` | Visit http:// → Redirect                                                     | /etc/apache2/sites-available/000-default.conf |                         |
| 22     | Run Apache as Non-Root User                                  | Verify `www-data` user                                                                                                | `ps aux \| grep apache2`                                                     | /etc/apache2/envvars                          |                         |
| 23     | Enable Rate Limiting                                         | Enable `mod_ratelimit`                                                                                                | Load test - "for i in {1..100}; do curl -I https://yourwebsite.com/page done" | /etc/apache2/mods-available/ratelimit.load    |                         |
| 24     | Block Open-ssh Version disclosure                            | `In AWS update the rule at SecurityGroup >> Inbound rules >> update the source as your-Public-IP/32`                  | nc publicIP 22                                                                | ---                                           |                         |

## 2. Frontend Hardening

```

```

## 3. Server Hardening

a) Protect Unsecure Routes against D-DOS

```
from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)


@router.post('/login')
@limiter.limit("5/minute")  # Apply rate limit to login endpoint (5 attempts per minute per IP)
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
```

b) Username Enumeration on Log

```
Update log message to be generic and not reveal if the username exists or not "Invalid credentials" instead of "User not found" or "Incorrect password"
```

c) CORS Misconfiguration - Wildcard Origin with credentials
Provide origin information, do not use wildcard '\*'

```
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["Authorization", "Content-Type"],
    allow_headers=["GET", "POST"],
)
```

d) Weak JWT sign

```
Use an asymmetric algorithm for JWT signing
```

e) SQL Injection
User Parametric Query

```
Parameteric Query Example
```

## Configure mod evasive

follow ` https://phoenixnap.com/kb/apache-mod-evasive`

```
<IfModule mod_evasive20.c>
    DOSHashTableSize    3097
    DOSPageCount        2
    DOSSiteCount        50
    DOSPageInterval     1
    DOSSiteInterval     1
    DOSBlockingPeriod   60
    DOSEmailNotify      you@example.com
    DOSSystemCommand    "sudo /sbin/iptables -A INPUT -s %s -j DROP"
    DOSLogDir           "/var/log/mod_evasive"
</IfModule>
EOF
)
```
