# syntax=docker/dockerfile:!
FROM python
RUN useradd -ms /bin/bash baseball
USER baseball
WORKDIR /home/baseball
RUN mkdir tmp
RUN chmod 777 ./tmp
COPY *.py /home/baseball/
COPY *.sh /home/baseball/
RUN chown -R baseball:baseball /home/baseball/
RUN chmod +x /home/baseball/updateBaseballDB.sh
ENV VIRTUAL_ENV=/home/baseball/
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD ["/home/baseball/updateBaseballDB.sh"]
