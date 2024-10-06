FROM debian:12

RUN apt-get update \
    && apt-get --no-install-recommends install -y \
        binutils \
        curl \
        genisoimage \
        libvirt-clients \
        make \
        openssh-client \
        p7zip-full \
        python3 \
        python3-dev \
        python3-pip \
        python3-venv \
        qemu-utils \
        sshpass \
        sudo \
        virtinst \
        xz-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /mnt/venv \
    && /mnt/venv/bin/pip install \
        altgraph==0.17.4 \
        Jinja2==3.1.2 \
        MarkupSafe==2.1.5 \
        packaging==24.1 \
        pyaml==21.10.1 \
        pydantic==1.10.4 \
        pyinstaller-hooks-contrib==2024.8 \
        pyinstaller==6.10.0 \
        PyYAML==6.0

COPY rootfs .
COPY src /mnt/src

# Allow user to change UID/GID at startup.
RUN useradd -m -s /bin/bash -u 1000 -U main \
    && chmod 777 /etc \
    && chmod 666 /etc/group /etc/passwd

USER main

ENV PATH=/mnt/src/scripts:/mnt/venv/bin:${PATH}
ENV PYTHONPATH=/mnt/src/modules

ENTRYPOINT ["/entrypoint.sh"]

CMD ["bash"]
