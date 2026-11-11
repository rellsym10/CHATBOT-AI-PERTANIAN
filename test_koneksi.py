import openai

client = openai.OpenAI(
    api_key="sk-T3wjM25NhKzpaXJgXvNsEw",  
    base_url="https://api.koboillm.com/v1", 
)

response = client.chat.completions.create(
    model="openai/gpt-4o",
    messages=[{"role": "user", "content": "halo, test koneksi"}]
)

print(response)