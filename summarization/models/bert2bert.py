from transformers import EncoderDecoderModel, BertTokenizer, IntervalStrategy, Seq2SeqTrainer
from transformers import Seq2SeqTrainingArguments

from summarization.models.base_model import BaseModel


class Bert2Bert(BaseModel):
    def __init__(self, config_path):
        super().__init__(config_path)

        self.model = EncoderDecoderModel.from_encoder_decoder_pretrained(
            "bert-base-cased", "bert-base-cased"
        )
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-cased")

        # model.config.decoder_start_token_id = tokenizer.bos_token_id
        self.model.config.decoder_start_token_id = self.tokenizer.cls_token_id
        self.model.config.pad_token_id = self.tokenizer.pad_token_id
        self.model.config.vocab_size = self.model.config.decoder.vocab_size

    def process_data_to_model_inputs(self, batch):
        # Tokenize the input and target data
        inputs = self.tokenizer(batch['article'], padding='max_length', truncation=True)
        outputs = self.tokenizer(batch['lead'], padding='max_length', truncation=True)

        batch['input_ids'] = inputs.input_ids
        batch['attention_mask'] = inputs.attention_mask
        # batch["decoder_input_ids"] = outputs.input_ids
        batch['decoder_attention_mask'] = outputs.attention_mask
        batch['labels'] = outputs.input_ids.copy()

        batch['labels'] = [[-100 if token == self.tokenizer.pad_token_id else token for token in labels] for labels in
                           batch['labels']]

        return batch

    def full_train(self):
        dataset = self.load_dataset('')
        tokenized_datasets = self.tokenize_datasets(dataset)

        training_args = Seq2SeqTrainingArguments(
            output_dir=self.config.output_dir,
            num_train_epochs=50,
            # predict_with_generate=True,
            evaluation_strategy=IntervalStrategy.STEPS,
            eval_steps=self.config.train_size // self.config.batch_size,
            save_steps=self.config.train_size // self.config.batch_size,
            per_device_train_batch_size=self.config.batch_size,
            per_device_eval_batch_size=self.config.batch_size,
            save_total_limit=10,
            warmup_steps=5,
            # fp16=True,
            # eval_accumulation_steps=30,
        )

        trainer = Seq2SeqTrainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_datasets["train"],
            eval_dataset=tokenized_datasets["test"],
        )

        trainer.train()

# tokenizer = BertTokenizer.from_pretrained("bert-base-cased")

# model = EncoderDecoderModel.from_encoder_decoder_pretrained(
#    "bert-base-cased", "bert-base-cased"
# )


# def load_input_file(file):
#     df = pd.read_json(file, lines=True)
#     df = df[['lead', 'article']]
#     df = drop_na_and_duplicates(df)
#     df = df.astype('str')
#     df.sample(frac=1, random_state=123)
#
#     return df


# def drop_na_and_duplicates(df):
#     df = df.dropna()
#     df = df.drop_duplicates(subset='article')
#     return df
#
#
# def process_data_to_model_inputs(batch):
#     # Tokenize the input and target data
#     inputs = tokenizer(batch['article'], padding='max_length', truncation=True)
#     outputs = tokenizer(batch['lead'], padding='max_length', truncation=True)
#
#     batch['input_ids'] = inputs.input_ids
#     batch['attention_mask'] = inputs.attention_mask
#     # batch["decoder_input_ids"] = outputs.input_ids
#     batch['decoder_attention_mask'] = outputs.attention_mask
#     batch['labels'] = outputs.input_ids.copy()
#
#     batch['labels'] = [[-100 if token == tokenizer.pad_token_id else token for token in labels] for labels in batch['labels']]
#
#     return batch


# def main():
# df = load_input_file('/home/bart/data/metropol.jsonl.gz')
#
# # model.config.decoder_start_token_id = tokenizer.bos_token_id
# model.config.decoder_start_token_id = tokenizer.cls_token_id
# model.config.pad_token_id = tokenizer.pad_token_id
# model.config.vocab_size = model.config.decoder.vocab_size

# train_size = 500
# dev_size = 200
# raw_datasets = DatasetDict({
#     'train': Dataset.from_pandas(df.iloc[:train_size]),
#     'validation': Dataset.from_pandas(df.iloc[train_size:train_size +dev_size]),
#     'test': Dataset.from_pandas(df.iloc[train_size+dev_size:train_size +dev_size +dev_size]),
# })
#
# tokenized_datasets = raw_datasets.map(process_data_to_model_inputs,
#                                       batched=True,
#                                       remove_columns=['article', 'lead'])
#
# tokenized_datasets.set_format(
#     type="torch", columns=["input_ids", "attention_mask", "decoder_attention_mask", "labels"],
# )

# batch_size = 4
# training_args = Seq2SeqTrainingArguments(
#     "test_trainer",
#     num_train_epochs=50,
#     # predict_with_generate=True,
#     evaluation_strategy=IntervalStrategy.STEPS,
#     eval_steps=train_size//batch_size,
#     save_steps=train_size//batch_size,
#     per_device_train_batch_size=batch_size,
#     per_device_eval_batch_size=batch_size,
#     save_total_limit=10,
#     warmup_steps=5,
#     # fp16=True,
#     # eval_accumulation_steps=30,
# )
#
# trainer = Trainer(
#     model=model,
#     args=training_args,
#     train_dataset=tokenized_datasets["train"],
#     eval_dataset=tokenized_datasets["test"],
# )
#
# trainer.train()