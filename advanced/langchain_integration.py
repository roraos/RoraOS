"""
RoraOS LangChain Integration - Python Example
==============================================

Example of integrating RoraOS API with LangChain.
Can be used for RAG, agents, chains, etc.

Installation:
    pip install langchain langchain-openai

Usage:
    python langchain_integration.py

Features:
    - LangChain ChatOpenAI compatibility
    - Chain examples
    - Memory examples
    - Simple RAG example
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# =====================================================
# SETUP
# =====================================================

# Configure RoraOS as backend
llm = ChatOpenAI(
    api_key="your-api-key-here",
    base_url="https://labs.roraos.com/api/v1",
    model="gpt-4o",
    temperature=0.7
)


# =====================================================
# EXAMPLE 1: Simple Chat
# =====================================================

def simple_chat():
    """Simple chat using LangChain."""
    print("=" * 50)
    print("Example 1: Simple Chat")
    print("=" * 50)

    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="What is Python?")
    ]

    response = llm.invoke(messages)
    print(f"Response: {response.content}")


# =====================================================
# EXAMPLE 2: Using Chains
# =====================================================

def chain_example():
    """Example using Chain with prompt template."""
    print("\n" + "=" * 50)
    print("Example 2: Chain with Prompt Template")
    print("=" * 50)

    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert in {topic}. Give easy-to-understand explanations."),
        ("human", "{question}")
    ])

    # Create chain
    chain = prompt | llm | StrOutputParser()

    # Run chain
    result = chain.invoke({
        "topic": "Python programming",
        "question": "How do I create a list comprehension?"
    })

    print(f"Response: {result}")


# =====================================================
# EXAMPLE 3: Conversation with Memory
# =====================================================

def conversation_with_memory():
    """Example conversation with memory."""
    print("\n" + "=" * 50)
    print("Example 3: Conversation with Memory")
    print("=" * 50)

    # Create conversation chain with memory
    memory = ConversationBufferMemory(return_messages=True)

    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=False
    )

    # First message
    response1 = conversation.predict(input="Hello! My name is John.")
    print(f"User: Hello! My name is John.")
    print(f"AI: {response1}")

    # Second message (should remember name)
    response2 = conversation.predict(input="What is my name?")
    print(f"\nUser: What is my name?")
    print(f"AI: {response2}")


# =====================================================
# EXAMPLE 4: Structured Output Chain
# =====================================================

def structured_output():
    """Example chain for structured output."""
    print("\n" + "=" * 50)
    print("Example 4: Structured Output")
    print("=" * 50)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """Extract information from the text and return as JSON:
{{"name": "...", "age": ..., "occupation": "..."}}
Only output valid JSON, nothing else."""),
        ("human", "{text}")
    ])

    chain = prompt | llm | StrOutputParser()

    text = "John Smith is a 28-year-old programmer who works at a tech startup."

    result = chain.invoke({"text": text})
    print(f"Input: {text}")
    print(f"Output: {result}")


# =====================================================
# EXAMPLE 5: Multi-step Chain
# =====================================================

def multi_step_chain():
    """Example multi-step chain (translate then summarize)."""
    print("\n" + "=" * 50)
    print("Example 5: Multi-step Chain")
    print("=" * 50)

    # Step 1: Translate
    translate_prompt = ChatPromptTemplate.from_messages([
        ("system", "Translate the following text to English. Only output the translation."),
        ("human", "{text}")
    ])

    # Step 2: Summarize
    summarize_prompt = ChatPromptTemplate.from_messages([
        ("system", "Summarize the following text in one sentence."),
        ("human", "{text}")
    ])

    # Create chains
    translate_chain = translate_prompt | llm | StrOutputParser()
    summarize_chain = summarize_prompt | llm | StrOutputParser()

    # Combine chains
    def translate_and_summarize(text: str) -> dict:
        translated = translate_chain.invoke({"text": text})
        summary = summarize_chain.invoke({"text": translated})
        return {
            "original": text,
            "translated": translated,
            "summary": summary
        }

    # Test
    text = "Indonesia is the largest archipelagic country in the world with more than 17,000 islands. The country has a very rich cultural diversity."

    result = translate_and_summarize(text)
    print(f"Original: {result['original']}")
    print(f"Translated: {result['translated']}")
    print(f"Summary: {result['summary']}")


# =====================================================
# EXAMPLE 6: Streaming
# =====================================================

def streaming_example():
    """Example streaming response."""
    print("\n" + "=" * 50)
    print("Example 6: Streaming Response")
    print("=" * 50)

    messages = [
        SystemMessage(content="You are a creative writer."),
        HumanMessage(content="Write a short poem about coding.")
    ]

    print("Response: ", end="")
    for chunk in llm.stream(messages):
        print(chunk.content, end="", flush=True)
    print()


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    try:
        simple_chat()
        chain_example()
        conversation_with_memory()
        structured_output()
        multi_step_chain()
        streaming_example()

    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure API_KEY and BASE_URL are correct!")
