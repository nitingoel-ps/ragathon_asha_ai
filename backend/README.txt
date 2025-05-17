#For getting fastapi and uvicorn running.
pip install fastapi "uvicorn[standard]"

#The below needs app.py to be in place.
uvicorn app:app --reload --loop asyncio

