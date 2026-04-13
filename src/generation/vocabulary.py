from llm_sdk.llm_sdk import Small_LLM_Model
from ..models.models_class import VocabularyModel
import json


class Vocabulary:
    def __init__(self, llm: Small_LLM_Model):
        self.llm = llm

        VocabularyModel(
            llm=llm
        )

        with open(self.llm.get_path_to_vocab_file(), 'r') as f:
            self.vocab = json.load(f)

    def get_id(self, token: str) -> int:
        try:
            id = self.vocab[token]
        except Exception:
            raise ValueError(f"token '{token}' id not found.")
        return id

    def get_ids_for(self, tokens: list[str]) -> list[int]:
        try:
            ids = []
            for token in tokens:
                ids.append(self.vocab[token])
        except Exception:
            raise ValueError(f"token '{token}' id not found.")
        return ids

    def get_token(self, id: int) -> str:
        try:
            token = self.llm.decode([id])
        except Exception:
            raise ValueError(f"'{id}' token not found.")
        return token

        # j'encode toute la phrase
        # puis je passe cette phrase encodé
