# LLM Summary

## Tokenization
LLMs do not read texts like humans. Instead, the text is broken into tokens, which are small units that are around ¾ of a word. The model processes these tokens. During the pretraining stage, roughly 10 terabytes of internet text is compressed into a neural network, similar to a lossy zip file. The model is forced to learn patterns, facts, and language structure that prompts the prediction of the next token. This compression gives the model its “knowledge.” However, this prediction is imperfect, causing occasional hallucinations that can be difficult to identify. 

## Context Windows
The context window is the amount of text the model can see at one time. When generating a response, the model looks at everything in the context window and predicts what comes next, then feeds that prediction back in to generate the next token. This process repeats iteratively. The size of the context window limits how much prior conversation or document content the model can reference at once. In current LLMs, System 1 thinking is used, where LLMs rely on fast, instinctive responses. There is a goal to push towards System 2 thinking, which allows the model to take more time and reason before generating a response. 


## Temperature
Temperature controls how random or creative the model’s outputs are. When the model generates the next token, it produces a probability distribution over all the possible next tokens. A low temperature makes the model pick the most likely token each time, resulting in predictable and consistent responses. A high temperature flattens the distribution making less likely tokens more probable, resulting in varied responses, but sometimes less accurate predictions. 
