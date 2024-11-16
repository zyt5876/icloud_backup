FROM frolvlad/alpine-glibc
LABEL chen yong
WORKDIR /app
COPY icloud_back.py /app
COPY healthcheck.sh /app
COPY pyicloud /app/pyicloud

#切换阿里源
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories

RUN apk add --update --no-cache curl jq py3-configobj py3-pip py3-setuptools python3 python3-dev
# pyicloud所需要的库, 注意Alpine linux本身安装的命令使用apk,这种方式实际上可能具有破坏性:--break-system-packages
COPY pyicloud_requirements.txt /app/
RUN pip install --no-cache-dir -r pyicloud_requirements.txt --break-system-packages

#修改时区
RUN apk add --update --no-cache tzdata \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone


HEALTHCHECK --start-period=30s --interval=1m --timeout=30s CMD /app/healthcheck.sh

CMD ["python3", "/app/icloud_back.py"]
