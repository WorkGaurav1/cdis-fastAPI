FROM ubuntu:22.04

# Prevent interactive prompts during apt install
ENV DEBIAN_FRONTEND=noninteractive

# 13. Enable ModSecurity
# 18. Enable mod_evasive
RUN apt-get update && apt-get install -y \
    apache2 \
    libapache2-mod-security2 \
    libapache2-mod-evasive \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Generate a self-signed SSL certificate for development (Required for HTTPS)
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/apache-selfsigned.key \
    -out /etc/ssl/certs/apache-selfsigned.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/OU=Unit/CN=localhost"

# Create ModEvasive log directory and set permissions
RUN mkdir -p /var/log/mod_evasive && \
    chown www-data:www-data /var/log/mod_evasive

# 10. Set Proper Log Permissions (Ensure www-data has proper access to Apache logs)
RUN chown -R root:adm /var/log/apache2 && \
    chmod -R 640 /var/log/apache2/* || true

# 16. Disable Unused Modules & Enable Required Modules
RUN a2dismod -f status autoindex include || true && \
    a2enmod proxy proxy_http ssl headers rewrite security2 evasive

# Copy custom configurations
COPY hardening.conf /etc/apache2/conf-available/
COPY security.conf /etc/apache2/conf-available/
COPY evasive.conf /etc/apache2/conf-available/
COPY 000-default.conf /etc/apache2/sites-available/

# Enable custom configurations
RUN a2enconf hardening security evasive

# Expose HTTP and HTTPS ports
EXPOSE 80
EXPOSE 443

# Start Apache in the foreground
CMD ["apache2ctl", "-D", "FOREGROUND"]
