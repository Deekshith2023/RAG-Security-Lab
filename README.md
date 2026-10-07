# RAG-Security-Lab

I built this lab because I wanted to understand how AI assistants actually fail when they are attacked.

Instead of only reading about prompt injection, jailbreaks, or RAG poisoning, I wanted to test these problems myself, observe the model's behaviour, and see which defenses actually make a difference.

Everything runs locally on my laptop. The current setup uses Llama 3.2 3B through Ollama and nomic-embed-text for embeddings. The next stage is a small RAG pipeline built around fictional SOC runbooks and security documents.

The idea behind the project is simple:

Attack it → observe the result → add a defense → run the same attack again.

Anything documented in this repository comes from that process.

What I'm Testing

I started with the model itself before adding RAG.

The first tests focus on:

System prompt leakage

Jailbreak attempts

Instruction override attempts

Model hallucinations and incorrect claims about its own behaviour
