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
make debug
```

## Resources
### Miscellaneous
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
Once the name is resolved, the algorithm transitions to **generating the parameters**. Depending on the type of the parameter, the system switches between the specific FSMs (Number, String, Array) to ensure the generated values strictly adhere to the expected JSON format and data types.
Each FSM are built in a way to respect the **JSON structure**. Using theses schemes: https://www.json.org/json-en.html

**String parameters** are constrained to English characters only, effectively blocking Cyrillic, Chinese, or other non-ASCII scripts.

### Prompt Engineering Strategy
**Instructional Framing**: Uses ```<|im_start|> / <|im_end|>``` tags to define roles to maintain context.
``` python
"<|im_start|>system\n"
"You are function-calling assistant.\n"
f"{self.fn_list}.\n"
"RULES:\n"
"- regex parameter must be a valid regex.\n"
"- replacement parameter must be valids.\n"
"<|im_end|>\n"

"<|im_start|>user\n"
f"{user_request}\n"
"<|im_end|>\n"

"<|im_start|>assistant\n"
f"{fn.name}\n(parameters: {param_done_str} {param}=\""
f"{self.state_machine.str_parser.result}"
```

**Technical rules**: To reinforce the generation of valid name and paramters.\
**Guided completion**: By adding ```param=```, the program forces the assistant to generate the value immediatly.

## Design decisions
### Modular architecture
The architecture follows a **strictly modular, object-oriented design, assigning dedicated classes**—Parser, Reader, Writer, Generator, and StateMachine—to each core responsibility. This includes specialized sub-parsers (String, Number, Array) for precise data validation.

### Finite-State Machine
Choosing a **Finite-State Machine (FSM)** ensures maximum precision by enforcing strict constraints at every step. This approach provides superior traceability throughout the generation process and simplifies the integration of future features through a structured, state-driven workflow.

## Performance analysis
### Benchmark
*1 function definition and 10 prompts:*
```
Performance:
Total time: 32.02s
Token generated: 698
Speed: 21.799885 tokens/sec
```

*5 functions definitions and 10 prompts:*
```
Performance:
Total time: 56.90s
Token generated: 715
Speed: 12.565821 tokens/sec
```

*10 functions definitions and 22 prompts:*
```
Performance:
Total time: 139.37s
Token generated: 4178
Speed: 29.978070 tokens/sec
```

- **Speed & Latency**: Testing shows a direct correlation between context size and generation speed. With a single function definition, the system reaches ~22 tokens/sec. However, increasing the prompt complexity (e.g., 5+ functions) without KV Caching drops the speed to ~12 tokens/sec due to the linear increase in attention re-computation.

- **Reliability vs. Complexity**:

	- **Simple extractions**: The system achieves 100% structural reliability; the FSM effectively prevents any JSON formatting errors.

	- **Complex Logic (Regex/SQL)**: While the FSM guarantees a valid format, small-scale models (0.6B) struggle with semantic accuracy in complex syntax. The "Reasoning Gap" of the model sometimes leads to technically valid but logically incorrect strings (e.g., missing brackets in regex) when the model's preferred tokens are masked by the FSM.

- **Scalability**: The solution is ideal for high-speed, simple data extraction but requires prompt-minimization strategies (like narrowing the function list) to maintain performance on larger datasets.


## Challenges faced

- **Optimising the mask**:
To optimize the decoding process, the system uses NumPy vectorization to apply constraints across the entire vocabulary simultaneously. By treating the token set as a single mathematical block rather than using slow Python loops, the algorithm initializes a global penalty vector and uses direct array indexing to instantly suppress unauthorized tokens. This makes the FSM-driven filtering computationally efficient, ensuring that strict syntax enforcement never bottlenecks the LLM's generation speed.

- **Ensuring Precise Parameter Generation**: To guarantee that each parameter type is correctly formatted, the program utilizes a Finite State Machine (FSM). At each step of the generation, the system identifies the current state and triggers transitions based on the LLM's token selection.

	- Deterministic Logic: For example, when generating numbers, if the LLM starts with 0, the FSM transitions to the AFTER_INT state. This state strictly limits the next allowed tokens to characters valid after a zero (such as '.', 'E', or 'e').

	- Strict JSON Compliance: By following these state-driven rules, the program effectively "prunes" the model's vocabulary in real-time, ensuring that every generated value is perfectly valid within the JSON format.

### Limitations faced
**Negative Numbers**: The model occasionally struggles with the leading minus sign or the logic required to transition into a negative numerical state accurately.

**Complex Regex**: While simple patterns are manageable through prompt rephrasing, the model's low parameter count limits its ability to generate or adhere to sophisticated regular expressions.

**Hallucination**: Even with constrained decoding, the model may still attempt to generate "plausible-sounding" but incorrect parameters if the prompt context is ambiguous or outside its training knowledge.

### Some Ideas
#### Prompt decomposition
For constraining the regex i came up with an idea that i did not implement:\
Let the LLM rephrase the prompt in a way that is syntactically parsable.
Indentify the request and constrained the right pattern. While this ensures high reliability for simple patterns, it remains a limited approach for more complex expressions.

```
"Replace all digits with NUMBERS" -> REPLACE: "digits"; WITH: "NUMBERS"

if "digits":
	return \\d+
elif "vowels":
	return [aeiouAEIOU]
else:
	return REPLACE
```

## Testing strategy
## Example usage
- We need a **functions_definition.json** file with at least one definition:
```json
{
"name": "fn_add_numbers",
"description": "Add two numbers together and return their sum.",
"parameters": {
	"a": {
	"type": "number"
	},
	"b": {
	"type": "number"
	}
},
"returns": {
	"type": "number"
}
}
```

- And a **function_calling.json** file with at least one prompt:
```json
{
"prompt": "What is the sum of 0.2 and 3?"
}
```

- The program will process the prompt and constrains the output to match ```fn_add_numbers``` definition into an **output JSON file**:

```json
{
	"prompt": "What is the sum of 0.2 and 3?",
	"name": "fn_add_numbers",
	"parameters": {
		"a": 0.2,
		"b": 3.0
	}
}
```
