# Kali linux base image
#FROM kalilinux/kali-rolling

# Ubuntu base image
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive


RUN apt-get clean && \
    apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
    aircrack-ng \
    pciutils \
    usbutils \
    iproute2 \
    iw \
    python3 \
    network-manager \
    python3-pip \
    python3-scapy \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

CMD ["/bin/bash"]
