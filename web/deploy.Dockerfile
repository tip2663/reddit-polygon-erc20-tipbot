FROM node:lts-iron

# Install cron
RUN apt-get update && apt-get install -y cron
# Set timezone to UTC
RUN ln -sf /usr/share/zoneinfo/UTC /etc/localtime

WORKDIR /app

COPY package-lock.json .
COPY package.json .

RUN npm install

COPY gridsome.config.js .
COPY gridsome.server.js .
COPY src src

ENV NODE_OPTIONS="--max-old-space-size=4096"
ENV DB_HOST=localhost
ENV DB_PORT=3306
ENV DB_USER=root
ENV DB_PASS=root
ENV DB_NAME=hodlbot
ENV SURGE_TOKEN=changeme
ENV SURGE_DOMAIN=changeme

SHELL ["/bin/bash", "-c"]
CMD set -o xtrace \ 
    && echo "0 10 * * * bash -c \"export PATH=\"/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin\" NODE_OPTIONS=\"$NODE_OPTIONS\" DB_HOST=\"$DB_HOST\" DB_PORT=\"$DB_PORT\" DB_USER=\"$DB_USER\" DB_PASS=\"$DB_PASS\" DB_NAME=\"$DB_NAME\" SURGE_TOKEN=\"$SURGE_TOKEN\" SURGE_DOMAIN=\"$SURGE_DOMAIN\" && cd /app && npm run build 2>&1 && ./node_modules/.bin/surge /app/dist $SURGE_DOMAIN 2>&1 \" >> /var/log/cron.log" > /etc/cron.d/deploysite \
    && chmod 0644 /etc/cron.d/deploysite \
    && crontab /etc/cron.d/deploysite \
    && touch /var/log/cron.log \
    && tail -f /var/log/cron.log & \
    cron -f
