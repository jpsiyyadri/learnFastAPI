import logging
import time

from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)

logging.info("Starting FastAPI application")

app = FastAPI()


data = {
    "name": "John Doe",
}


@app.get("/")
async def read_root():
    return {"Hello": "World"}


def process_step_1(email: str):
    print("Processing data")
    data["step_1"] = "started"
    logging.info(f"Processing data for {email}")
    time.sleep(10)
    data["step_1"] = "completed"
    logging.info(f"Data processed for step 1 {email}")


def process_step_2(email: str):
    print("Processing step 2")
    if data.get("step_1") != "completed":
        logging.info(f"Step 1 not completed for {email}")
        return
    data["step_2"] = "started"
    logging.info(f"Processing step 2 for {email}")
    time.sleep(10)
    logging.info(f"Data processed for step 2 {email}")


@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    logging.info(f"Received request for {email}")
    background_tasks.add_task(
        process_step_1, email
    )
    logging.info(f"Message sent to step 1 for {email}")
    background_tasks.add_task(
        process_step_2, email
    )
    logging.info(f"Message sent to step 2 for {email}")
    return JSONResponse(content={"message": "Message sent"}, status_code=200)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)