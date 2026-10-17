# Static triage scanner for untrusted downloads. Built and run on media01 by
# scripts/triage.sh; the analysis container runs with no network, a read-only
# root, and the sample mounted read-only.
FROM debian:trixie-slim@sha256:918311b7b6c4c6f68b232ba516584925f6c78ad82b6fd534b98979df6438e483

ARG CAPA_VERSION=10.0.0
ARG CAPA_SHA256=96cb5115f495024a478b0e9f9f77f9027058155589235fbd4c50e7382055fcca
ARG DIE_VERSION=3.21
ARG DIE_SHA256=47ed1299fe0fcdf3549e4077573db9651c228144b22a372729eb014548332fcd
ARG YARA_FORGE_RELEASE=20261011
ARG YARA_FORGE_SHA256=bf0cc68e60df44bee4e9906713160889e7c2142b14621394860a45e629035147

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -q \
 && apt-get install -y -q --no-install-recommends \
      ca-certificates curl unzip file ffmpeg 7zip innoextract yara \
      clamav clamav-freshclam python3 \
 && rm -rf /var/lib/apt/lists/*

RUN set -eux; cd /tmp; \
    curl -fsSLo capa.zip "https://github.com/mandiant/capa/releases/download/v${CAPA_VERSION}/capa-v${CAPA_VERSION}-linux.zip"; \
    echo "${CAPA_SHA256}  capa.zip" | sha256sum -c -; \
    unzip -q capa.zip -d /usr/local/bin; chmod 0755 /usr/local/bin/capa; rm capa.zip; \
    curl -fsSLo die.deb "https://github.com/horsicq/DIE-engine/releases/download/${DIE_VERSION}/die_${DIE_VERSION}_Debian_13_amd64.deb"; \
    echo "${DIE_SHA256}  die.deb" | sha256sum -c -; \
    apt-get update -q; apt-get install -y -q --no-install-recommends ./die.deb; rm -rf die.deb /var/lib/apt/lists/*; \
    curl -fsSLo yf.zip "https://github.com/YARAHQ/yara-forge/releases/download/${YARA_FORGE_RELEASE}/yara-forge-rules-core.zip"; \
    echo "${YARA_FORGE_SHA256}  yf.zip" | sha256sum -c -; \
    mkdir -p /opt/yara; unzip -q -j yf.zip '*.yar' -d /opt/yara; rm yf.zip; \
    yarac -w /opt/yara/*.yar /opt/yara/core.yarc; \
    echo "capa ${CAPA_VERSION}; die ${DIE_VERSION}; yara-forge core ${YARA_FORGE_RELEASE}" > /opt/versions.txt

COPY scan.py /usr/local/bin/scan.py
ENTRYPOINT ["python3", "/usr/local/bin/scan.py"]
