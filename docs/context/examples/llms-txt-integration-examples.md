# llms.txt Integration Examples

## Example 1: Claude System Prompt

```python
import anthropic
with open("docs/context/llms.txt") as f:
    context = f.read()

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    system=f"You are an Ante expert.\n\n{context}",
    messages=[{"role": "user", "content": "How do I create a skill?"}]
)
print(response.content[0].text)
```

## Example 2: LangChain RAG

```python
from langchain.chat_models import ChatAnthropic
from langchain.schema import SystemMessage, HumanMessage

with open("docs/context/llms.txt") as f:
    docs = f.read()

llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
messages = [
    SystemMessage(content=f"Ante expert using docs:\n{docs}"),
    HumanMessage(content="What tools are available?")
]
print(llm(messages).content)
```

## Example 3: Fine-tuning Training Data

```python
def generate_training_examples(llms_txt):
    examples = []
    for section in parse_sections(llms_txt):
        examples.append({
            "messages": [
                {"role": "system", "content": "Ante expert"},
                {"role": "user", "content": f"Explain {section['title']}"},
                {"role": "assistant", "content": section['content']}
            ]
        })
    return examples

# Save as JSONL for fine-tuning
with open("docs/context/llms.txt") as f:
    examples = generate_training_examples(f.read())
# Upload to OpenAI for fine-tuning
```

## Example 4: Multi-turn Conversation

```python
class AnteAssistant:
    def __init__(self, llms_txt_path):
        with open(llms_txt_path) as f:
            self.docs = f.read()
        self.history = []
    
    def chat(self, msg):
        self.history.append({"role": "user", "content": msg})
        response = anthropic.Anthropic().messages.create(
            model="claude-3-5-sonnet-20241022",
            system=f"Ante expert:\n{self.docs}",
            messages=self.history
        )
        ans = response.content[0].text
        self.history.append({"role": "assistant", "content": ans})
        return ans

assistant = AnteAssistant("docs/context/llms.txt")
print(assistant.chat("What is Ante?"))
print(assistant.chat("How do I install it?"))
```

## Example 5: Vector RAG System

```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatAnthropic
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load and embed
with open("docs/context/llms.txt") as f:
    docs = [{"page_content": f.read(), "metadata": {}}]

splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
chunks = splitter.split_documents(docs)

vectorstore = Chroma.from_documents(chunks, OpenAIEmbeddings())

qa = RetrievalQA.from_chain_type(
    llm=ChatAnthropic(model="claude-3-5-sonnet-20241022"),
    retriever=vectorstore.as_retriever()
)

print(qa.run("How do I create a custom skill?"))
```

## Quick Comparison

| Approach | Token Cost | Latency | Best For |
|----------|-----------|---------|----------|
| System Prompt | Higher | Lower | Small docs |
| RAG | Lower | Higher | Large docs |
| Fine-tuning | Lowest | Lowest | Frequent queries |
