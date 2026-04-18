import json

from llm_sdk.llm_sdk import Small_LLM_Model


class Vocabulary:
    """Loads and queries the LLM vocabulary for token-id mappings.

    Provides efficient lookup of token ids used by the FSM parsers
    to filter valid tokens at each generation step.

    Attributes:
        llm: The language model instance.
        vocab: Dict mapping token strings to their integer ids.
    """

    def __init__(self, llm: Small_LLM_Model):
        """Initialize Vocabulary, validate inputs, and load the vocab file.

        Args:
            llm: The language model instance.
        """
        self.llm = llm
        from ..models.models_class import VocabularyModel

        VocabularyModel(
            llm=llm
        )

        with open(self.llm.get_path_to_vocab_file(), 'r') as f:
            self.vocab = json.load(f)

    def get_ids_for(self, tokens: list[str]) -> list[int]:
        """Return the token ids corresponding to a list of token strings.

        Args:
            tokens: List of token strings to look up.

        Returns:
            List of integer token ids in the same order as the input.

        Raises:
            ValueError: If any token is not found in the vocabulary.
        """
        ids = []
        for token in tokens:
            if token not in self.vocab:
                raise ValueError(f"token '{token}' id not found")
            ids.append(self.vocab[token])
        return ids

    def get_token(self, id: int) -> str:
        """Decode a token id back to its string representation.

        Args:
            id: The integer token id to decode.

        Returns:
            The decoded token string.

        Raises:
            ValueError: If the id cannot be decoded.
        """
        try:
            token = self.llm.decode([id])
        except Exception:
            raise ValueError(f"'{id}' token not found.")
        return token
