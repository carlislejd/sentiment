from transformers import RobertaTokenizer, RobertaForSequenceClassification

# Define paths
SENTIMENT_MODEL_PATH = "./sentiment_model"
SENTIMENT_TOKENIZER_PATH = "./sentiment_tokenizer"

#EMOTION_MODEL_PATH = "./emotion_model"
#EMOTION_TOKENIZER_PATH = "./emotion_tokenizer"

# Download and save sentiment model and tokenizer
sentiment_model = RobertaForSequenceClassification.from_pretrained("cardiffnlp/twitter-xlm-roberta-base-sentiment")
sentiment_tokenizer = RobertaTokenizer.from_pretrained("cardiffnlp/twitter-xlm-roberta-base-sentiment")
sentiment_model.save_pretrained(SENTIMENT_MODEL_PATH)
sentiment_tokenizer.save_pretrained(SENTIMENT_TOKENIZER_PATH)

# Download and save emotion model and tokenizer
#emotion_model = RobertaForSequenceClassification.from_pretrained("SamLowe/roberta-base-go_emotions")
#emotion_tokenizer = RobertaTokenizer.from_pretrained("SamLowe/roberta-base-go_emotions")
#emotion_model.save_pretrained(EMOTION_MODEL_PATH)
#emotion_tokenizer.save_pretrained(EMOTION_TOKENIZER_PATH)