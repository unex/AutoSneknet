from transformers import RobertaForSequenceClassification, RobertaTokenizer

import fire
import torch

# https://github.com/openai/gpt-2-output-dataset/blob/master/detector/server.py

checkpoint = './detector-large.pt'

class Roberta:
    def __init__(self):
        self.device = 'cpu'

        data = torch.load(checkpoint, map_location=self.device)
        model_name = 'roberta-large' if data['args']['large'] else 'roberta-base'
        self.model = RobertaForSequenceClassification.from_pretrained(model_name)
        self.tokenizer = RobertaTokenizer.from_pretrained(model_name)

        self.model.load_state_dict(data['model_state_dict'])
        self.model.eval()

    def query(self, query):
        tokens = self.tokenizer.encode(query)
        all_tokens = len(tokens)
        tokens = tokens[:self.tokenizer.max_len - 2]
        used_tokens = len(tokens)
        tokens = torch.tensor([self.tokenizer.bos_token_id] + tokens + [self.tokenizer.eos_token_id]).unsqueeze(0)
        mask = torch.ones_like(tokens)

        with torch.no_grad():
            logits = self.model(tokens.to(self.device), attention_mask=mask.to(self.device))[0]
            probs = logits.softmax(dim=-1)

        fake, real = probs.detach().cpu().flatten().numpy().tolist()

        return fake, real
