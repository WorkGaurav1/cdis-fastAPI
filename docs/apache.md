# Apache Reverse Proxy Architecture

This document explains the role, function, and configuration of the Apache HTTP Server used in the CDIS FastAPI infrastructure.

## Why are we using Apache?

In a modern enterprise architecture, you should never expose your application server (like FastAPI running on Uvicorn) directly to the open internet. Instead, we place a **Reverse Proxy** in front of it.

Apache acts as a robust, battle-tested gatekeeper. Its job is to:
1. **Intercept** all incoming HTTP/HTTPS traffic from the outside world.
2. **Filter** and inspect the traffic to block malicious attacks (DDoS, SQL Injection, XSS).
3. **Forward** only safe, legitimate traffic to the hidden FastAPI backend.

This is why the React frontend connects to `https://localhost` (Apache) instead of directly connecting to FastAPI.

---

## The Files Explained

The `apache/` directory contains the configuration files needed to build the secure Apache container.

### 1. `Dockerfile`
This is the instruction manual for Docker to build the Apache image. It starts with the official Debian Apache image, installs critical security modules (`mod_security2` and `mod_evasive`), generates self-signed SSL certificates for HTTPS, and copies our custom `.conf` files into the container's system directories.

### 2. `000-default.conf`
This is the main routing configuration file. It dictates exactly how Apache should handle incoming web traffic.
* **Port 80 (HTTP)**: It intercepts all insecure HTTP traffic and forces a `301 Redirect` to the secure HTTPS version of the site.
* **Port 443 (HTTPS)**: It loads the SSL certificates to encrypt the connection. It then defines the `ProxyPass` and `ProxyPassReverse` rules, which tell Apache: *"If a request comes in for `/api/v1/`, forward it to the hidden `api:8000` FastAPI container."*

### 3. `security.conf`
This file configures **ModSecurity (WAF - Web Application Firewall)**. ModSecurity acts as an intrusion detection and prevention system. It analyzes the payload of every incoming request in real-time, blocking known attack signatures (like SQL injection strings or Cross-Site Scripting attempts) before they ever reach the Python code.

### 4. `evasive.conf`
This file configures **ModEvasive**, which is specifically designed to protect against DoS (Denial of Service) and DDoS (Distributed Denial of Service) attacks. It tracks how many requests an IP address makes in a given time frame. If an IP requests the same page too many times in a row, or makes too many concurrent requests across the site, ModEvasive temporarily blocks the IP and returns a `403 Forbidden` error.

### 5. `hardening.conf`
This file implements standard VAPT (Vulnerability Assessment and Penetration Testing) hardening rules. It ensures Apache doesn't leak version information (`ServerTokens Prod`, `ServerSignature Off`), disables dangerous HTTP methods (like `TRACE` and `TRACK`), and sets up strict file and directory access policies to prevent directory traversal attacks.
