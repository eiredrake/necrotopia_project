FROM python:3.10.5

RUN echo '===============WEBSITE START==============='

RUN mkdir /necrotopia_web
WORKDIR /necrotopia_web

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r ./requirements.txt

COPY manage.py .
COPY Config.py .
COPY necrotopia ./necrotopia/
COPY necrotopia_project/ ./necrotopia_project/
COPY templates/ ./templates/
COPY static/ ./static/
COPY media/static_images/ ./media/static_images/

EXPOSE 8000

CMD [ "gunicorn", "necrotopia_project.wsgi", "--bind", "0.0.0.0:8000" ]

RUN echo '===============WEBSITE END==============='
