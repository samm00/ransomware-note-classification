from datasets import load_dataset, Features, Value
import evaluate
import numpy as np
from transformers import AutoTokenizer, DataCollatorWithPadding, AutoModelForSequenceClassification, TrainingArguments, Trainer

data = load_dataset("csv", data_files={'train': "data/train.csv", 'eval': "data/eval.csv", 'test': "data/test.csv"})
print(data)

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-cased")

def preprocess_function(examples):
    return tokenizer(examples["text"], truncation=True)

tokenized_data = data.map(preprocess_function, batched=True)

columns_to_return = ['input_ids', 'label', 'attention_mask']
tokenized_data.set_format(type='torch', columns=columns_to_return)

data_collator = DataCollatorWithPadding(tokenizer)

accuracy = evaluate.load("accuracy")
f1 = evaluate.load("f1")
precision = evaluate.load("precision")
recall = evaluate.load("recall")

def compute_metrics(eval_pred):
    preds, labels = eval_pred
    preds = np.argmax(preds, axis=1)
    acc = accuracy.compute(predictions=preds, references=labels)
    f1_scr = f1.compute(predictions=preds, references=labels)
    prec_scr = precision.compute(predictions=preds, references=labels)
    recall_scr = recall.compute(predictions=preds, references=labels)
    return {'accuracy': acc['accuracy'], 'f1': f1_scr['f1'], 'precision': prec_scr['precision'], 'recall': recall_scr['recall']}

id2label = {0: "non-malicious", 1: "malicious"}
label2id = {"non-malicious": 0, "malicious": 1}

model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-cased", num_labels=2, id2label=id2label, label2id=label2id)

training_args = TrainingArguments(
    output_dir="ransom",
    learning_rate=1e-5,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    gradient_accumulation_steps=8,
    num_train_epochs=10,
    weight_decay=0.02,
    logging_steps=10,
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    remove_unused_columns = False,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_data["train"],
    eval_dataset=tokenized_data["eval"],
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics
)

trainer.train()
trainer.model.save_pretrained('ransom')

model = AutoModelForSequenceClassification.from_pretrained('ransom')

preds = trainer.predict(tokenized_data['test'])
print('----------------------------------------')
print(preds[2])
print('--------------------')
incorrect = [name for pred, label, name in zip(preds[0], preds[1], data['test']['id']) if (pred[0] < pred[1] and label == 0) or (pred[0] > pred[1] and label == 1)]
print(incorrect)
print('----------------------------------------')