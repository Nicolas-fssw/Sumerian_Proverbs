#!/usr/bin/env python3
"""Fine-tune a small language model on the proverb archive for generation."""

from pathlib import Path

from utility import load_archive, _is_substantive_proverb

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
)
from datasets import Dataset


ARCHIVE_PATH = Path("ancient_wisdoms.json")
OUTPUT_DIR = Path("proverb_model")
EPOCHS = 3
BATCH_SIZE = 8

print("Loading proverb archive...")
archive = load_archive(ARCHIVE_PATH)
texts = [
    p["text"].strip()
    for p in archive
    if p.get("text") and _is_substantive_proverb(p["text"])
]
if not texts:
    raise SystemExit("No substantive proverb texts found in archive (editorial-only entries excluded).")

prompt = "Proverb: "
lines = [f"{prompt}{t}" for t in texts]
tokenizer = AutoTokenizer.from_pretrained("distilgpt2")
tokenizer.pad_token = tokenizer.eos_token


def tokenize(examples):
    out = tokenizer(
        examples["text"],
        truncation=True,
        max_length=128,
        padding="max_length",
    )
    pad_id = tokenizer.pad_token_id
    out["labels"] = [
        [x if x != pad_id else -100 for x in ids]
        for ids in out["input_ids"]
    ]
    return out


dataset = Dataset.from_dict({"text": lines})
tokenized = dataset.map(
    tokenize,
    batched=True,
    remove_columns=dataset.column_names,
)

model = AutoModelForCausalLM.from_pretrained("distilgpt2")
output_path = str(OUTPUT_DIR)

training_args = TrainingArguments(
    output_dir=output_path,
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    save_strategy="epoch",
    logging_steps=50,
    report_to="none",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized,
)
print("Training...")
trainer.train()
trainer.save_model(output_path)
tokenizer.save_pretrained(output_path)
print(f"Model saved to {OUTPUT_DIR}")