import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
    retry_if_exception_type
)


@retry(
    retry=retry_if_exception_type((openai.error.APIError, openai.error.APIConnectionError, openai.error.RateLimitError, openai.error.ServiceUnavailableError, openai.error.Timeout)),
    wait=wait_fixed(60),
    stop=stop_after_attempt(50)
)
def translate_to_language_openai(text, target_lang):
    system_msg = f"Translate it from English to {target_lang}."
    if not isinstance(text, str):
        return text, text
    
    response = openai.ChatCompletion.create(
        #         model="gpt-4", #gpt-3.5-turbo
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": text}
        ],
        temperature=0,
        max_tokens=1024,
        request_timeout=55,
    )

    return text, response['choices'][0]['message']['content']