import streamlit as st
import pandas as pd

import tensorflow as tf
from datasets import Dataset
from transformers import TFAutoModelForSequenceClassification, \
                        AutoTokenizer, \
                        DefaultDataCollator


def tokenize_function(examples):
    return tokenizer(examples["claim"], padding="max_length", truncation=True)

def split_paragraph_by_fullstop(paragraph):
    sentences = paragraph.split('.')
    return [sentence.strip() for sentence in sentences if sentence.strip()]

def main():
    st.title("Text File Reader")

    # File upload
    uploaded_file = st.file_uploader("Upload a text file", type="txt")

    model = TFAutoModelForSequenceClassification.from_pretrained("paulokewunmi/claim_extractor_distilbert", num_labels=2)
    tokenizer = AutoTokenizer.from_pretrained(f"distilbert-base-uncased")

    if uploaded_file is not None:
        # Read file content
        file_contents = uploaded_file.read().decode("utf-8")

        # Split paragraph by full stop
        sentences = split_paragraph_by_fullstop(file_contents)

        df = pd.DataFrame({"claim": sentences}, index=range(len(sentences)))
        dataset = Dataset.from_pandas(df)

        tokenized_datasets = dataset.map(tokenize_function, batched=True)
        data_collator = DefaultDataCollator(return_tensors="tf")

        tf_test_dataset = tokenized_datasets.to_tf_dataset(
            columns= ["attention_mask", "input_ids"],
            shuffle=False,
            collate_fn=data_collator,
            batch_size=8,
        )

        pred = model.predict(tf_test_dataset)

        tf_predictions = tf.nn.softmax(pred["logits"], axis=-1)
        label = tf.argmax(tf_predictions, axis=1).numpy()

        df["label"] = pd.Series(label)
        df["confidence"] = tf_predictions[:, 1:].numpy()



        st.dataframe(df)

if __name__ == "__main__":
    main()
