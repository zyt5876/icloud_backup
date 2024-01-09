FROM frolvlad/alpine-glibc
LABEL chen yong
WORKDIR /app
COPY icloud_back.py /app
COPY healthcheck.sh /app

#切换阿里源
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories

RUN apk add --update --no-cache curl jq py3-configobj py3-pip py3-setuptools python3 python3-dev
RUN pip install pyicloud --break-system-packages
RUN sed -i 's/idmsa.apple.com/idmsa.apple.com.cn/g' /usr/lib/python3.11/site-packages/pyicloud/base.py
RUN sed -i 's/www.icloud.com/www.icloud.com.cn/g' /usr/lib/python3.11/site-packages/pyicloud/base.py
RUN sed -i 's/setup.icloud.com/setup.icloud.com.cn/g' /usr/lib/python3.11/site-packages/pyicloud/base.py

#修改时区
RUN apk add --update --no-cache tzdata \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone


HEALTHCHECK --start-period=10s --interval=1m --timeout=10s CMD /app/healthcheck.sh

CMD [ "sh" ]
