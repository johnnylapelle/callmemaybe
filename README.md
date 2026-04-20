*This project has been created as part of the 42 curriculum by jvacossi.*
# Call Me Maybe
![](assets/banner.jpg)
## Description
Call Me Maybe is a **constrained decoding project**. The objective is to use an **LLM (Qwen3-0.6B)** as **function-calling assistant** to generate a valid json file, containing the **prompt**, the correct **function name** and its **parameters** based on a functions definition lists:
```json
[
	{
		"prompt": "What is the sum of 2 and 3?",
		"name": "fn_add_numbers",
		"parameters": {"a": 2.0, "b": 3.0}
	},
	{
		"prompt": "Reverse the string'hello'",
		"name": "fn_reverse_string",
		"parameters": {"s": "hello"}
	}
]
```
*Example of the output file*

### What is Constrained Decoding ?
- **Constrained decoding** is a technique that manipulates a generative model's token generation process to constrain its next-token predictions to only tokens that do not violate the required output structure.

## Instructions
### Installation
For installing all the dependencies.
```
make install
```

### Execution
By default, the program will read input files from the data/input/
directory and write output to the data/output/ directory. You
can optionally specify custom paths using the --functions_definition, --input and --output
arguments.
```
make run

uv run python -m src

uv run python -m src --input data/input/function_calling.json --functions_definition data/input/functions_definition.json --output data/output/output.json
```

### Debug
To run the program in a debug mode
```
make debug
```

## Resources
### Constrained decoding and LLM
- [A Guide to Structured Generation Using Constrained Decoding - aidancooper.co](https://www.aidancooper.co.uk/constrained-decoding/)
- [Coalescence: making LLM inference 5x faster - dottxt.ai](https://blog.dottxt.ai/coalescence.html)
- [Efficient Guided Generation for Large Language Models - arxiv.org](https://arxiv.org/abs/2307.09702)

### Machine State:
- [Fast JSON Decoding for Local LLMs with Compressed Finite State Machine - lmsys.org](https://www.lmsys.org/blog/2024-02-05-compressed-fsm)
- [Building a simple State Machine in Python - dev.to/karn](https://dev.to/karn/building-a-simple-state-machine-in-python)

### Miscellaneous
- [What is a production system in ai ? - geeksforgeeks.org](https://www.geeksforgeeks.org/artificial-intelligence/what-is-a-production-system-in-ai/)
- [Caveman Prompting: One User Cut Claude's Token Usage by 75% - aiproductivity.ai](https://aiproductivity.ai/news/caveman-prompting-claude-75-percent-fewer-tokens/)
- [The documentation on Qwen - qwen.readthedocs.io](https://qwen.readthedocs.io/en/latest/getting_started/concepts.html)
- [Chain-of-thought - ibm.com](https://www.ibm.com/fr-fr/think/topics/chain-of-thoughts)


## How AI was used

- **Socratic guidance**: Rather than requesting direct solutions, AI was used as a thinking partner — asking the right questions to guide independent implementation decisions.
- **Code review**: AI reviewed each class for error handling correctness, identifying bugs such as catching Exception instead of ValidationError, or calling .errors() on the wrong type.
- **Documentation**: AI assisted in writing docstrings following PEP 257 (Google style) and drafting README sections including Design decisions, Optimization Strategies, and Performance analysis.
- **Research synthesis**: AI summarized academic papers and blog posts on constrained decoding (Outlines, SGLang, coalescence) and identified which concepts were applicable to the project.
- **Debugging**: AI helped interpret Pydantic validation errors and suggested cleaner formatting for error messages.
- **Testing strategy**: AI introduced pytest patterns and explained how to mock heavy dependencies like Small_LLM_Model to write lightweight unit tests.

## Algorithm explanation
The project uses **FSM (Finite-State Machine)** to track each steps of the generation.
It have 4 differents FSM. One for the main **StateMachine**, used as a monitor of the global generation and 3 for specific data types **Number, String and Array**.

At each step the algorithm apply a **dynamic mask** to the vocabulary, ensuring the LLM only select tokens that are syntactically correct for the current state.


The process is divided into two primary phases:
- **The generation of the name.**
- **The generation of the parameters.**

The generation process **focuses exclusively on the function name and its parameters**, which are captured and stored in a dictionary that match the desired JSON output file. Once the prompts are all processed, the JSON file is created based on that dictionary.

### Generation of the name
- First, every function name in ```functions_definition.json``` is retokenized into a dictionary.
```
'fn_add_numbers': ['fn', '_add', '_numbers'],
```
- The algorithm initializes a list of **potential candidates** containing every available function. At the start, every function is eligible. For each generation step, a mask is applied so that only tokens corresponding to the current index within the remaining candidates are available to the LLM.

- With each selected token, the list narrows. If a function name no longer matched the generated prefix, it is removed from the eligible pool until one valid function remains.

### Generation of the parameters
- Once the name is resolved, the algorithm transitions to **generating the parameters**. Depending on the type of the parameter, the system switches between the specific FSMs (Number, String, Array) to ensure the generated values strictly adhere to the expected JSON format and data types.
Each FSM are built in a way to respect the **JSON structure**. Using theses schemes: https://www.json.org/json-en.html

- **String parameters** are constrained to English characters only, effectively blocking Cyrillic, Chinese, or other non-ASCII scripts.

### Prompt Engineering Strategy
- **Instructional Framing**: Uses ```<|im_start|> / <|im_end|>``` tags to define roles to maintain context.
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

- **Technical rules**: To reinforce the generation of valid name and paramters.\
- **Guided completion**: By adding ```param=```, the program forces the assistant to generate the value immediatly.

## Design decisions
### Design and Architecture
#### Modular architecture
- The architecture follows a **strictly modular, object-oriented design, assigning dedicated classes**—Parser, Reader, Writer, Generator, and StateMachine—to each core responsibility. This includes specialized sub-parsers (String, Number, Array) for precise data validation.

#### Finite-State Machine
- Choosing a **Finite-State Machine (FSM)** ensures maximum precision by enforcing strict constraints at every step. This approach provides superior traceability throughout the generation process and simplifies the integration of future features through a structured, state-driven workflow.

### Optimisation Strategies
#### Jump-forward
- Sometimes the **valid_ids list** contains **only one id**, meaning the outcome is deterministic — the LLM has no choice. In this case, the program skips the forward pass and directly uses that token, avoiding unnecessary computation.

#### Re-tokenisation
- At each generation step, instead of appending the new token id directly to the existing sequence, the program **re-encodes the entire generated string** from scratch via _get_prompt. This ensures that the token sequence passed to the LLM always **reflects a natural tokenization**, avoiding artificial token boundaries that could degrade the quality of subsequent predictions.

#### Vocabulary Filtering
- To improve generation reliability, the **StringParser pre-compiles two regular expressions at initialization**. The first restricts regex-type parameters to simple alphanumeric patterns, preventing the model from generating overly complex or malformed regular expressions. The second filters the vocabulary during free string generation, excluding non-latin characters such as Cyrillic or Chinese scripts. This is a deliberate trade-off: expressiveness is sacrificed in favor of consistency and correctness.

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
- **Negative Numbers**: The model occasionally struggles with the leading minus sign or the logic required to transition into a negative numerical state accurately.

- **Complex Regex**: While simple patterns are manageable through prompt rephrasing, the model's low parameter count limits its ability to generate or adhere to sophisticated regular expressions.

- **Hallucination**: Even with constrained decoding, the model may still attempt to generate "plausible-sounding" but incorrect parameters if the prompt context is ambiguous or outside its training knowledge.

### Future Improvements
#### Prompt decomposition
- For constraining the regex i came up with an idea that i did not implement:\
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
- **Unit Testing**: The implementation was validated by running the pipeline against a dataset of prompts covering various edge cases and parameter types.
- **Schema Validation**: Every generated output is automatically validated against the expected JSON structure. The test fails if the output cannot be parsed or does not match the schema.
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
