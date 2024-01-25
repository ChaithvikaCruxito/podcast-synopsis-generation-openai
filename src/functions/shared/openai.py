
# import openai
from openai import AzureOpenAI
from .appsettings import OPENAI_KEY, OPENAI_ENDPOINT
import logging
import tiktoken


# openai.api_type = "azure"
# openai.azure_endpoint = OPENAI_ENDPOINT
# openai.api_version = "2023-07-01-preview"
# openai.api_key = OPENAI_KEY

client = AzureOpenAI(
    api_key=OPENAI_KEY,  
    api_version="2023-07-01-preview",
    azure_endpoint = OPENAI_ENDPOINT
)
    
deployment_name='podcastlkcgpt35turbo'

# id of desired_model
# DESIRED_MODEL = 'text-davinci-003'
# DESIRED_CAPABILITY = 'completion'

# deployment_id = None

# def deploy_model():
#     global deployment_id
#     # list models deployed with
#     result = openai.Deployment.list()

#     for deployment in result.data:
#         if deployment["status"] != "succeeded":
#             continue

#         model = openai.Model.retrieve(deployment["model"])

#         # check if desired_model is deployed, and if it has 'completion' capability
#         if model["id"] == DESIRED_MODEL and model['capabilities'][DESIRED_CAPABILITY]:
#             deployment_id = deployment["id"]

#     # if no model deployed, deploy one
#     if not deployment_id:
#         logging.info('No deployment with status: succeeded found.')

#         # Deploy the model
#         logging.info(f'Creating a new deployment with model: {DESIRED_MODEL}')
#         result = openai.Deployment.create(model=DESIRED_MODEL, scale_settings={
#             "scale_type": "standard"})
#         deployment_id = result["id"]
#         logging.info(
#             f'Successfully created {DESIRED_MODEL} that supports text {DESIRED_CAPABILITY} with id: {deployment_id}.')
#     else:
#         logging.info(
#             f'Found a succeeded deployment of "{DESIRED_MODEL}" that supports text {DESIRED_CAPABILITY} with id: {deployment_id}.')


def strip_string(string, to_strip):
    if to_strip:
        while string.startswith(to_strip):
            string = string[len(to_strip):]
        while string.endswith(to_strip):
            string = string[:-len(to_strip)]
    return string


def remove_special_tokens(s):
    s = s.strip()
    s = strip_string(s, "<|im_start|>")
    s = strip_string(s, "<|im_end|>")
    return s


# A generator that split a text into smaller chunks of size n, preferably ending at the end of a sentence
def chunk_generator(text, n, tokenizer):
    tokens = tokenizer.encode(text)
    i = 0
    while i < len(tokens):
        # Find the nearest end of sentence within a range of 0.5 * n and 1.5 * n tokens
        j = min(i + int(1.5 * n), len(tokens))
        while j > i + int(0.5 * n):
            # Decode the tokens and check for full stop or newline
            chunk = tokenizer.decode(tokens[i:j])
            if chunk.endswith(".") or chunk.endswith("\n"):
                break
            j -= 1
        # If no end of sentence found, use n tokens as the chunk size
        if j == i + int(0.5 * n):
            j = min(i + n, len(tokens))
        yield tokens[i:j]
        i = j


def request_api(document, prompt_postfix, max_tokens):
    prompt = prompt_postfix.replace('<document>', document)
    messages = [{"role": "user", "content": prompt}]
    logging.info(f'>>> prompt : {prompt}')
    response = client.chat.completions.create(
        model=deployment_name, # model = "deployment_name".
        messages=messages,
        max_tokens=max_tokens
    )
    print("*********************")
    print(response)
    print("********************")
    # print(response.model_dump_json(indent=2))
    # print(response.choices[0].message.content)
    # response =  client.chat.completions.create(model=deployment_name, prompt=prompt, max_tokens=10)
    # response = AzureOpenAI.chat.completion.create(
    #     model="podcastlkcgpt35turbo",
    #     messages=prompt,
    #     temperature=0,
    #     max_tokens=max_tokens,
    #     top_p=1,
    #     frequency_penalty=1,
    #     presence_penalty=1,
    #     stop='###'
    # )

    # return response['choices'][0]['text']
    print("***********************")
    print(response.choices[0].message.content)
    print("************************")
    return response.choices[0].message.content


def generate_synopsis(content):
    prompt_postfix = """ <document>
  \n###
  \nSummarise the transcript of a podcast above into a synopsis. 
  \nSynopsis: 
"""

    synopsis_chunk = []
    n = 1250  # max tokens for chuncking
    max_tokens = 1000  # max tokens for response
    max_summary_size = 3000

    tokenizer = tiktoken.get_encoding('p50k_base')

    # Generate chunkcs
    chunks = chunk_generator(content, n, tokenizer)

    # Decode chunk of text
    text_chunks = [tokenizer.decode(chunk) for chunk in chunks]

    # Request api
    for chunk in text_chunks:
        synopsis_chunk.append(request_api(chunk, prompt_postfix, max_tokens))
        # print(chunk)
        # print('>>> synopsis: \n' + synopsis_chunck[-1])

    # Synopsis
    synopsis = ' '.join(synopsis_chunk)
    return remove_special_tokens(synopsis)


def generate_taglines(synopsis):
    prompt_postfix = """ <document>
  \n###
  \nGenerate 2 to 3 tag lines based on the podcast synopsis above.
"""
    max_tokens = 500
    tag_lines = request_api(synopsis, prompt_postfix, max_tokens)
    return remove_special_tokens(tag_lines)


def generate_seokeywords(content):
    prompt_postfix = """ <document>
  \n###
  \nGenerate 5 search engine optimised keywords based on text above.  
"""
    keywords_chunck = []
    n = 2000  # max tokens for chuncking
    max_tokens = 100

    tokenizer = tiktoken.get_encoding('p50k_base')

    # Generate chunkcs
    chunks = chunk_generator(content, n, tokenizer)

    # Decode chunk of text
    text_chunks = [tokenizer.decode(chunk) for chunk in chunks]

    # Request api
    for chunk in text_chunks:
        keywords_chunck.append(request_api(chunk, prompt_postfix, max_tokens))

    # Keywords
    keywords = ' '.join(keywords_chunck)

    prompt_postfix = """ <document>
  \n###
  \nReduce keywords above to 5 search engine optimised keywords. 
"""
    max_tokens = 50
    seo_keywords = request_api(keywords, prompt_postfix, max_tokens)
    return remove_special_tokens(seo_keywords)


def generate_chinese(synopsis):
    prompt_postfix = """ <document>
  \n###
  \nTranslate synposis into Chinese. 
"""
    max_tokens = 500
    translations = request_api(synopsis, prompt_postfix, max_tokens)
    return remove_special_tokens(translations)


def generate_german(synopsis):
    prompt_postfix = """ <document>
  \n###
  \nTranslate synposis into German. 
"""
    max_tokens = 500
    translations = request_api(synopsis, prompt_postfix, max_tokens)
    return remove_special_tokens(translations)


def generate_spanish(synopsis):
    prompt_postfix = """ <document>
  \n###
  \nTranslate synposis into Spanish. 
"""
    max_tokens = 500
    translations = request_api(synopsis, prompt_postfix, max_tokens)
    return remove_special_tokens(translations)


def generate_portuguese(synopsis):
    prompt_postfix = """ <document>
  \n###
  \nTranslate synposis into Portuguese. 
"""
    max_tokens = 500
    translations = request_api(synopsis, prompt_postfix, max_tokens)
    return remove_special_tokens(translations)


# deploy_model()
