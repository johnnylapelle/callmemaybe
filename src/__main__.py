from src.llm_sdk import Small_LLM_Model


def main():
    test = Small_LLM_Model()
    encode_return = test.encode("salut auguste")
    print(encode_return)


if __name__ == "__main__":
    main()
