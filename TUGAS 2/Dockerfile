#base image
FROM python:3.9

#menentukan working directory
WORKDIR /app

#copy semua file ke image
COPY . /app

#install depedencies
RUN pip install -r requirements.txt

#jalankan aplikasi python 
CMD ["python","app.py"]

#docker build (membuat image dari docker file)

