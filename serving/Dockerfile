FROM python:3.9
COPY . /app
WORKDIR /app
EXPOSE 8080
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]