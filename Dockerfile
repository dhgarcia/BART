FROM ubuntu:xenial
# FROM ubuntu:trusty

ARG VERSION="2.5.5.5-linux64"
ARG SDK_VERSION="2.5.5/sdk-python"
ARG CHOREGRAPHE_VERSION="2.5.5/Choregraphe"

RUN apt-get update && apt-get install -y --no-install-recommends \
    pkg-config \
    build-essential \
    dbus \
    git \
    wget \
    python \
    python-dev \
    python-pip \
    python-setuptools \
    libxcb* \
    libgl-dev \
    libxrandr-dev \
    libxkbcommon-x11-dev \
    libfontconfig-dev \
    libxaw7-dev \
    libogre-1.9-dev \
    cython \
    xclip \
    gstreamer1.0* \
    libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
    libsdl2-dev libsdl2-ttf-dev libsdl2-image-dev libsdl2-mixer-dev \
    libmtdev-dev \
    && rm -rf /var/lib/apt/lists/*

#NAOQI SDK
RUN wget -O /tmp/pynaoqi-python.tar.gz "https://community-static.aldebaran.com/resources/${SDK_VERSION}/pynaoqi-python2.7-${VERSION}.tar.gz" \
    && tar -C /opt -xf /tmp/pynaoqi-python.tar.gz \
    && ln -fs /opt/pynaoqi-python2.7-${VERSION} /opt/pynaoqi-python-sdk \
    && echo 'export PYTHONPATH=${PYTHONPATH}:/opt/pynaoqi-python-sdk/lib/python2.7/site-packages' >> ~/.bashrc \
    && echo 'export QI_SDK_PREFIX=/opt/pynaoqi-python-sdk' >> ~/.bashrc \
    && ln -s /usr/lib/x86_64-linux-gnu/OGRE-1.9.0 /opt/pynaoqi-python-sdk/lib/OGRE \
    && rm /tmp/pynaoqi-python.tar.gz

# #CHOREGRAPHE
# RUN wget -O /tmp/choregraphe-suite.tar.gz "https://community-static.aldebaran.com/resources/${CHOREGRAPHE_VERSION}/choregraphe-suite-${VERSION}.tar.gz" \
#     && tar -C /opt -xf /tmp/choregraphe-suite.tar.gz \
#     && ln -fs /opt/choregraphe-suite-${VERSION}/monitor /usr/bin/monitor \
#     && ln -fs /opt/choregraphe-suite-${VERSION}/choregraphe /usr/bin/choregraphe_launch \
#     && printf '#!/bin/sh\n\exec choregraphe_launch --key 654e-4564-153c-6518-2f44-7562-206e-4c60-5f47-5f45 "$@"\n' >> /usr/bin/choregraphe \
#     && chmod +x /usr/bin/choregraphe \
#     && rm /tmp/choregraphe-suite.tar.gz


ARG uid=2001
ARG gid=2002

ENV BART_WS=/bart
COPY requirements.txt .

# RUN groupadd -g ${gid} bart && useradd -m --no-log-init -r -u ${uid} -g bart bart && usermod -aG sudo bart
# RUN groupadd -r bart && useradd -m --no-log-init -r -u 1000 -g bart bart
# #-g bart -G sudo
# RUN chown bart: $BART_WS/
# USER bart:bart

#BART APP KIVY
RUN pip install --upgrade pip==20.3.4 \
    && pip install -r requirements.txt 

COPY src $BART_WS/
WORKDIR $BART_WS/
RUN mkdir results

ENV PYTHONPATH "${PYTHONPATH}:/opt/pynaoqi-python-sdk/lib/python2.7/site-packages"

CMD ["bash"]
#CMD ["python", "BART_app.py"]
