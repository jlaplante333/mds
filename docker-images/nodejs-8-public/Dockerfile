FROM "__FROM_IMAGE_STREAM_DEFINED_IN_TEMPLATE__"

# Install OS dependencies for NPM build success
USER 0
RUN yum install -y nasm build-base libtool libpng-dev autoconf automake
USER 1001

# Install sonar-scanner
RUN curl -sLo /tmp/sonar-scanner-cli.zip https://dl.bintray.com/sonarsource/SonarQube/org/sonarsource/scanner/cli/sonar-scanner-cli/3.2.0.1227/sonar-scanner-cli-3.2.0.1227-linux.zip && \
    mkdir ${APP_ROOT}/sonar-scanner-cli && unzip -q /tmp/sonar-scanner-cli.zip -d ${APP_ROOT}/sonar-scanner-cli && \
    mv ${APP_ROOT}/sonar-scanner-cli ${APP_ROOT}/_sonar-scanner-cli && mv ${APP_ROOT}/_sonar-scanner-cli/sonar-scanner-3.2.0.1227-linux ${APP_ROOT}/sonar-scanner-cli && \
    rm -rf ${APP_ROOT}/_sonar-scanner-cli \
    rm /tmp/sonar-scanner-cli.zip && \
    chmod -R 755 ${APP_ROOT}/sonar-scanner-cli

# Copy project dependencies
COPY package.json ${APP_ROOT}/src
COPY package-lock.json ${APP_ROOT}/src

# Install latest npm to /tmp
RUN source ${APP_ROOT}/etc/scl_enable && npm install --prefix /tmp npm@6.9.0

# Install dependencies
RUN source ${APP_ROOT}/etc/scl_enable && cd ${APP_ROOT}/src && npm set progress=false && /tmp/node_modules/.bin/npm ci
