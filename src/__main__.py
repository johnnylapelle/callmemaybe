from llm_sdk.llm_sdk import Small_LLM_Model
from numpy import argmax


def main():
    llm = Small_LLM_Model()
    logits_id = []

    prompt = "salut auguste"

    for _ in range(10):
        encode_return = llm.encode(prompt)
        tensor_list = encode_return.squeeze().tolist()

        logits = llm.get_logits_from_input_ids(tensor_list)
        max_logit = argmax(logits)

        logits_id.append(max_logit)
        prompt += llm.decode(logits_id)


if __name__ == "__main__":
    main()
