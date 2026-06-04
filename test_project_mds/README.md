Учебный проект, который объединяет в себе последователные шаги
по созданию ML-сервиса на Streamlit с эндпоинтами на FastAPI

Для запуска:
* > conda deactivate
* > source myvenv/bin/activate
* > uvicorn backend.api:app --reload
* > streamlit run frontend/Main.py

Смотрим:
* > http://localhost:8501/
* > http://localhost:8000/docs

Команды:
* > python utils/init_db.py