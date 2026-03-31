from llm_sdk.llm_sdk import Small_LLM_Model
import json


def test_constrained_decoding():
    try:
        llm = Small_LLM_Model()
        with open(llm.get_path_to_vocab_file(), 'r') as f:
            vocab = json.load(f)

        prompt = "What is the sum of 3 and 4?"
        input_ids = llm.encode(prompt).tolist()[0]

        logits = llm.get_logits_from_input_ids(input_ids)
        for i in range(len(logits)):
            if i != vocab['{']:
                logits[i] = float("-inf")

        next_token_id = logits.index(max(logits))
        print(llm.decode([next_token_id]))

    except Exception as e:
        print(e)


if __name__ == "__main__":
    test_constrained_decoding()
