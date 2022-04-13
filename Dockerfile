# syntax=docker/dockerfile:!
FROM python
RUN useradd -ms /bin/bash baseball
USER baseball
WORKDIR /home/baseball
RUN mkdir tmp
RUN chmod 777 ./tmp
COPY --chown=baseball *.py /home/baseball/
COPY --chown=baseball *.sh /home/baseball/
ENV VIRTUAL_ENV=/home/baseball/
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD ["/home/baseball/updateBaseballDB.sh"]
