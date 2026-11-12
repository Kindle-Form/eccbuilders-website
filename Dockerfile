# Optional image for Easypanel when the service builder is Dockerfile.
# Serves the same static files as the current nginx deploy, adds 301 redirects
# from the old eccbuilders.com paths, and injects form endpoints from env vars.
# If the service is already saved as Nixpacks, this file is not used until the
# builder is switched. The HTML site still deploys either way.
FROM nginx:1.24-alpine

ENV PORT=80

COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY docker-entrypoint.ecc.sh /docker-entrypoint.ecc.sh
RUN chmod +x /docker-entrypoint.ecc.sh

COPY . /usr/share/nginx/html
RUN rm -rf \
  /usr/share/nginx/html/.git \
  /usr/share/nginx/html/scripts \
  /usr/share/nginx/html/deploy \
  /usr/share/nginx/html/Dockerfile \
  /usr/share/nginx/html/nginx.conf \
  /usr/share/nginx/html/docker-entrypoint.ecc.sh \
  /usr/share/nginx/html/.dockerignore \
  /usr/share/nginx/html/Staticfile \
  /usr/share/nginx/html/README.md

ENTRYPOINT ["/docker-entrypoint.ecc.sh"]
CMD ["nginx", "-g", "daemon off;"]
