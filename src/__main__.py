from src.llm_sdk import Small_LLM_Model

def main():
    test = Small_LLM_Model()
    data = test.encode('salut je suis jean')
    print(data)


if __name__ == "__main__":
    main()
