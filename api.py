from fastapi import FastAPI, HTTPException
from transformers import pipeline

SENTIMENT_MODEL = "./sentiment_model"
SENTIMENT_TOKENIZER = "./sentiment_tokenizer"

EMOTION_MODEL = "./emotion_model"
EMOTION_TOKENIZER = "./emotion_tokenizer"

sentiment_pipe = pipeline(task="sentiment-analysis", model=SENTIMENT_MODEL, tokenizer=SENTIMENT_TOKENIZER)
emotion_pipe = pipeline(task="sentiment-analysis", model=EMOTION_MODEL, tokenizer=EMOTION_TOKENIZER)


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "See Docs!"}

@app.post("/text/")
async def sentiment_emotion(text: str):
    
    if not text:
        raise HTTPException(status_code=400, detail="Invalid or empty cleaned text")

    sentiment = sentiment_pipe(text)
    emotion = emotion_pipe(text)
    
    return {"sentiment": sentiment, "emotion": emotion}
