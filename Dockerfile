FROM python


WORKDIR /usr/share/server

RUN pip install flask flask-cors


ADD app.py /usr/share/server

EXPOSE 8020

CMD ["python", "app.py"]
