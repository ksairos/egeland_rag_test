from langchain_openai import ChatOpenAI


model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

response = model.invoke("Why do parrots talk?")
print(response)
