*This project has been created as part of the 42 curriculum by jvacossi.*
# Call Me Maybe
## Description
Call Me Maybe is **constrained decoding project**. The objective is to use an **LLM (Qwen3-0.6B)** as **function-calling assistant**, to generate a valid json file, containing the correct **function name** and its **parameters** based on a functions definition lists.

## Instructions
### Installation
For installing all the dependencies.
```
make install
```

### Execution
This will execute the program using the input data in ```data/input/```.
```
make run
```
You can also run it manually:
```
uv run python -m src
```

### Debug
To run the program in a debug mode
```
```

## Resources
### Divers
- https://www.geeksforgeeks.org/artificial-intelligence/what-is-a-production-system-in-ai/
- https://aiproductivity.ai/news/caveman-prompting-claude-75-percent-fewer-tokens/
- https://qwen.readthedocs.io/en/latest/getting_started/concepts.html

### Constrained decoding
- https://www.aidancooper.co.uk/constrained-decoding/
- https://blog.dottxt.ai/coalescence.html
- https://arxiv.org/abs/2307.09702
- https://www.lmsys.org/blog/2024-02-05-compressed-fsm

### Machine State:
- https://dev.to/karn/building-a-simple-state-machine-in-python


## Algorithm explanation
The project uses **FSM (Finite-State Machine)** to track each steps of the generation.
It have 4 differents FSM. One for the main **StateMachine**, used as a monitor of the global generation and 3 for specific data types **Number, String and Array**.

At each step the algorithm apply a **dynamic mask** to the vocabulary, ensuring the LLM only select tokens that are syntactically correct for the current state.


The process is divided into two primary phases:
- **The generation of the name.**
- **The generation of the parameters.**

The generation process **focuses exclusively on the function name and its parameters**, which are captured and stored in a dictionnary that match the desired JSON output file. Once the prompts are all processed, the JSON file is created based on that dictionnary.

### Generation of the name
First, every function name in ```functions_definition.json``` is retokenized into a dictionary.
```
'fn_add_numbers': ['fn', '_add', '_numbers'],
```
The algorithm initializes a list of **potential candidates** containing every available function. At the start, every function is eligible. For each generation step, a mask is applied so that only tokens corresponding to the current index within the remaining candidates are available to the LLM.

- With each selected token, the list narrows. If a function name no longer matched the generated prefix, it is removed from the eligible pool until one valid function remains.

### Generation of the parameters
Once the name is resolved, the algorithm transitions to generating the parameters. Depending on the type of the parameter, the system switches between the specific FSMs (Number, String, Array) to ensure the generated values strictly adhere to the expected JSON format and data types.
Each FSM are built in a way to respect the JSON structure. Using theses schemes: https://www.json.org/json-en.html

## Design decisions
## Performance analysis
## Challenges faced
Limitation:
- Negative numbers
- nombres negatifs decimaux
- regexs simples comme "cat" marche mais pas les patterns complexes

Idea:
- For constraining the regex i came up with an idea:
	Let the LLM rephrase the prompt in a way that is syntactically parsable.
	Indentify the request and call the right pattern:
		Example:
			"Replace all digits with NUMBERS"
			REPLACE: digits; WITH: NUMBERS
			"digits" -> \d+

			"vowels" -> [aeiouAEIOU]
			"word cat" -> cat
## Testing strategy
## Example usage
