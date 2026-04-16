from llm_sdk.llm_sdk import Small_LLM_Model
import numpy as np


def get_prompt(request):
    return f"""<|im_start|>system
Rephrase the regex operation in this exact syntax: pattern=<pattern>, replacement=<replacement>
Where <pattern> describes what to match and <replacement> is the replacement value.
You must output only: pattern=<pattern>, replacement=<replacement> without thinking or balise

Examples:
"Replace numbers with X" → pattern=digits, replacement=X
"Replace vowels with *" → pattern=vowels, replacement=*
"Replace word cat with dog" → pattern=cat, replacement=dog
"Replace spaces with _" → pattern=spaces, replacement=_
<|im_end|>
<|im_start|>user
{request}
<|im_end|>
<|im_start|>assistant
pattern="""


def generate(prompt, llm: Small_LLM_Model):
    answer = ""
    print(prompt)
    full_prompt = get_prompt(prompt)
    # print(full_prompt)
    input_ids = llm.encode(full_prompt).tolist()[0]
    token_decoded = ""
    END_TOKEN_ID = 151645

    while True:
        logits = llm.get_logits_from_input_ids(input_ids)
        np_logits = np.array(logits)
        next_token = int(np.argmax(np_logits))

        if next_token == END_TOKEN_ID:
            break

        token_decoded = llm.decode([next_token])
        print(token_decoded, end="", flush=True)
        answer += token_decoded
        input_ids.append(next_token)

    print(answer)
    return answer


def main():
    llm = Small_LLM_Model()

    result = {}

    prompts = [
        "Replace all numbers in \"Hello 34 I'm 233 years old\" with NUMBERS",
        "Replace all vowels in 'Programming is fun' with asterisks",
        "Substitute the word 'cat' with 'dog' in 'The cat sat on the mat with another cat"
    ]

    for i, prompt in enumerate(prompts):
        result[i] = generate(prompt, llm)

    print(result)


if __name__ == "__main__":
    main()
