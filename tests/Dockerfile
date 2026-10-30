FROM pico-aio-test:bookworm

RUN apt-get update && apt-get install -y gnupg scdaemon pinentry-tty ninja-build && rm -rf /var/lib/apt/lists/*
RUN pip3 install --break-system-packages inputimeout fido2==2.2.1 pexpect
