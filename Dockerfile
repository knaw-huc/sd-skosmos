FROM library/php:8.1-apache

# set skosmos release version and download link
ARG version=v3.1
#ARG SKOSMOS_TARGZ_RELEASE_URL=https://github.com/knaw-huc/Skosmos/archive/refs/tags/${version}.tar.gz
ARG SKOSMOS_TARGZ_RELEASE_URL=https://github.com/NatLibFi/Skosmos/archive/refs/tags/${version}.tar.gz

# general server setup and locale
RUN apt-get update && \
  apt-get -y install gettext locales curl unzip vim git libicu-dev libxslt-dev && \
  for locale in en_GB en_US fi_FI fr_FR sv_SE; do \
    echo "${locale}.UTF-8 UTF-8" >> /etc/locale.gen ; \
  done && \
  locale-gen

## Install NVM and Node
# Use bash for the shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Create a script file sourced by both interactive and non-interactive bash shells
ENV BASH_ENV /root/.bash_env
RUN touch "${BASH_ENV}"
RUN echo '. "${BASH_ENV}"' >> ~/.bashrc

# Download and install nvm
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | PROFILE="${BASH_ENV}" bash
RUN echo node > .nvmrc
RUN nvm install

# config apache2
RUN a2enmod rewrite
RUN a2enmod expires
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf

# Install Skosmos
RUN rm -rf /var/www/html/* && curl -L --output skosmos.tar.gz ${SKOSMOS_TARGZ_RELEASE_URL} && \
    tar -zxvf skosmos.tar.gz -C /var/www/html/ --strip-components=1 && \
	rm -rf /Skosmos* /skosmos.tar.gz

# install composer required php packs
RUN docker-php-ext-install intl
RUN docker-php-ext-install xsl
RUN docker-php-ext-install gettext

# Install Composer
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

# Install Skosmos dependencies
RUN /usr/local/bin/composer install --no-dev --no-interaction
RUN npm install --omit=dev


# Configure Skosmos
COPY skosmos-repository.ttl /var/www/
COPY entrypoint.sh /var/www/
COPY entrypoint_cron.sh /var/www/
COPY ./src /var/www/src
COPY entrypoint.py /var/www/
COPY config-docker-compose.ttl /var/www/html/

ENTRYPOINT ["/var/www/entrypoint.sh"]
