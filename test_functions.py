from llm_sdk.llm_sdk import Small_LLM_Model
import json


def main():
    llm = Small_LLM_Model()

    with open(llm.get_path_to_vocab_file(), 'r') as f:
        vocab = json.load(f)

    functions = [
        ["fn", "_add", "_numbers"],
        ["fn", "_g", "reet"],
        ["fn", "_reverse", "_string"],
        ["fn", "_get", "_square", "_root"],
        ["fn", "_sub", "stitute", "_string", "_with", "_regex"],
    ]

    prompt = "What is the sum of 2 and 3? Function name:"
    input_ids = llm.encode(prompt).tolist()[0]

    fn_id = vocab["fn"]
    logits = llm.get_logits_from_input_ids(input_ids)
    for i in range(len(logits)):
        if i != fn_id:
            logits[i] = float("-inf")
    next_token = logits.index(max(logits))
    input_ids.append(next_token)
    print(llm.decode([next_token]), end="", flush=True)
