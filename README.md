# callmemaybe

## Resources
- https://www.geeksforgeeks.org/artificial-intelligence/what-is-a-production-system-in-ai/
- https://aiproductivity.ai/news/caveman-prompting-claude-75-percent-fewer-tokens/

Constrained decoding
- https://www.aidancooper.co.uk/constrained-decoding/
- https://blog.dottxt.ai/coalescence.html
- https://arxiv.org/abs/2307.09702
- https://www.lmsys.org/blog/2024-02-05-compressed-fsm

Machine State:
- https://dev.to/karn/building-a-simple-state-machine-in-python

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
