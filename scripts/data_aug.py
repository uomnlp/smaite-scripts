
from openai_utils import *
import os
import logging
from handystuff.loaders import load_jsonl, write_jsonl

import glob
import fire


prompt = """Given claim, verdict and evidence:  

Give ratings to following categories. Structure your output as a json file with the following keys 'contra-article', 'contra-self', 'rate', 'verdict', 'convince', 'new'. 
Do not output anything other than the json output.
The output must be pure json so it can be parsed.
Stick to the following rules for your ratings:
1. 'contra-article': If the verdict contradicts the article, the answer should be true, else false.  
2.  'contra-self': If the verdict contradicts itself, the answer should be true, else false.      
3. 'rate': Overall, on a scale of 1 to 5, how would you rate the verdict? 1 represents the worst and 5 represents the best.  
4. 'verdict': Does the verdict support or refute the claim? If the verdict clearly supports the claim, the answer should be 'true', if it clearly refutes the claim, the answer should be 'false'. If the claim supports or refutes parts of the input, the answer should be 'inbetween'.  
5. 'convince': Is the verdict convincing? Should it be used to contextualise the claim? If yes, the answer should be true, otherwise false.  
6. 'new': Does the verdict introduce new information which is not part of the article? If yes, the answer should be true, if not, the answer should be false.

Claim:
{claim}

Verdict:
{verdict}

Evidence:
{text}"""



async def main(start_from=0, go_to=-1):
    files = sorted(glob.glob('data/processed/*.jsonl'))
    print(files)
    data = []
    for f in files:
        data.extend(load_jsonl(f))
    print(len(data))
    logging.getLogger(__name__).setLevel("WARNING")
    os.environ['OPENAI_API_KEY'] = '23a9b885bbe04c0187ee63bcf7e04e9c'

    result_buffer = data[start_from:go_to]
    print(len(result_buffer))

    system_prompt_message = "You are a fact checking quality assessment bot."

    # Create the system prompt message
    prompt_data = {
        "messages": [
            {
                "role": "system",
                "content": system_prompt_message,
            },
        ]
    }

    system_prompt = chat_prompt.ChatMessages.from_dict(prompt_data)

    # Create the list of user prompts
    chat_messages = []
    for item in result_buffer:
        inputs = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt.format(claim=item['claim'], verdict=item['verdict'], text=item['text']),
                },
            ]
        }
        chat_message = chat_prompt.ChatMessages.from_dict(inputs)
        chat_messages.append(chat_message)

    # Create the config file for the LM
    model_config = lm_config.LMConfig(provider='azure', model='chatgpt-3.5-turbo')

    openai.api_type = "azure"
    openai.api_base = "https://ai-research-team.openai.azure.com/"
    openai.api_version = "2023-03-15-preview"


    # Call the async function for processing the data
    results = await generate_from_openai_chat_completion(chat_messages, system_prompt, model_config,
                                                            temperature=0.1,
                                                            max_tokens=800, top_p=0.95,
                                                            context_length=2000,
                                                            deployment_id="test-chatgpt", requests_per_minute=100)
    write_jsonl(results, f'chatgpt{start_from}-{go_to}.jsonl')
if __name__ == '__main__':
    fire.Fire(main)