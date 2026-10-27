# RAG-Security-Lab

A hands-on, local AI security lab for testing vulnerabilities in large language model (LLM) and retrieval-augmented generation (RAG) applications. The project focuses on controlled experiments: reproduce an attack, record what actually happened, test a defense, and document the result and its limitations.

The lab uses **Python**, **Ollama**, **Llama 3.2 3B**, **`nomic-embed-text`**, and **ChromaDB**. Experiments use fictional SOC runbooks, synthetic documents, and fake canary values and are designed to run locally.

## Experiments

### 1. [System Prompt Leakage](https://github.com/Deekshith2023/RAG-Security-Lab/blob/main/system-prompt-leakage/README.md)

Tests whether an assistant reveals a synthetic secret placed in its system prompt. The experiment evaluates leakage attempts and compares defensive approaches. See the individual report for its methodology, observed outcomes, and limitations.

### 2. [Indirect Prompt Injection](https://github.com/Deekshith2023/RAG-Security-Lab/blob/main/Indirect-prompt-injection/README.md)

Tests whether an attacker-controlled wiki page can influence an assistant when retrieved alongside trusted SOC runbooks.

**Observed in the documented tests:** a page that directly addressed the assistant led to harmful advice in **29/30** runs; a plain-tip page led to harmful advice in **16/30**. Retrieving only from the trusted folder resulted in **0 harmful replies in 60 poisoned runs**. Prompt labeling reduced the direct-instruction attack but did not eliminate the plain-tip attack. The report discusses the limits of the ingestion scan and output-check heuristic.

### 3. [Retrieval Hijacking](https://github.com/Deekshith2023/RAG-Security-Lab/blob/main/Retrieval-hijacking/README.md)

Tests whether attacker-controlled pages can enter the top-three retrieved chunks or displace trusted runbooks in a larger synthetic corpus. It compares a plain tip, a longer stuffed page, a mirrored page, a cloned runbook, and a multi-chunk flood.

**Observed in the documented tests:** the plain-tip page appeared in the top three for all five target queries. Longer pages sometimes occupied multiple retrieval positions and pushed the trusted runbook out of the top three. Page length and chunk count are confounding factors, so the experiment does not isolate the effect of keyword repetition alone.

### 4. [RAG Access-Control Bypass](https://github.com/Deekshith2023/RAG-Security-Lab/blob/main/Access-Control%20Bypass/README.md)

Tests whether a simulated SOC Analyst can retrieve information restricted to a SOC Lead. The experiment compares no retrieval filtering, prompt-only instructions, and permission filtering enforced in Python before context reaches the LLM.

**Observed in the documented tests:** with filtering off, the restricted synthetic marker was disclosed. Prompt-only protection exposed a shortened version of the marker. Enforced retrieval filtering excluded the restricted report from the Analyst's retrieved context while allowing the simulated SOC Lead to retrieve it.

### 5. [AI Agent Tool Abuse](https://github.com/Deekshith2023/RAG-Security-Lab/blob/main/AI%20Agent%20Tool%20Abuse/README.md)

Tests whether an LLM-driven SOC assistant can request simulated tools and whether a Python authorization layer controls sensitive actions. The available tools simulate ticket creation, host isolation, and EDR disabling; they do not modify real hosts or security software.

**Observed in the documented tests:** the six automated authorization tests passed. Under the open policy, a direct request by an Analyst executed the simulated EDR-disable action. Under the enforced policy, the Analyst's request was blocked; a SOC Lead request without explicit approval was also blocked, while a Lead request with approval was allowed.

The indirect-injection outcome was more limited. In five standard-question runs per corpus, the EDR-disable tool was not executed with either the clean or poisoned corpus, although the poisoned document influenced the model's wording. With an action-oriented request, the simulated EDR-disable tool executed once with the clean corpus and once with the poisoned corpus under the open policy. These results demonstrate the importance of authorization enforcement, but **do not establish that the poisoned document increased actual tool execution**. The individual report records these distinctions and the remaining limitations.

## Technology and pipeline

The RAG pipeline follows this flow:

1. Load local documents and retain source metadata.
2. Split text into overlapping chunks.
3. Use `nomic-embed-text` to convert chunks and questions into vectors.
4. Store and search chunks with ChromaDB.
5. Retrieve the top three chunks for a query.
6. Pass retrieved context to Llama 3.2 3B through Ollama and record the response.

The baseline pipeline uses character-based chunks of up to **500 characters** with **100 characters of overlap**. Individual experiments may have additional settings or a separate agent/tool-execution layer. Use each experiment's README as the source of truth for its prerequisites and reproduction commands.

## Testing approach

- Establish a baseline before introducing an attack.
- Keep questions and settings consistent when comparing conditions, where practical.
- Repeat tests when model responses can vary.
- Distinguish retrieval success, harmful answer generation, sensitive-data disclosure, and actual tool execution; these are different outcomes.
- Preserve logs and inspect examples instead of relying only on aggregate counts.
- Treat automated detectors as heuristics and document possible false positives and false negatives.
- Report limitations rather than assuming a result generalizes to other models or production environments.

## Scope and limitations

- The experiments use synthetic documents, fictional SOC scenarios, and fake canary values.
- The work is intended for local research and controlled security evaluation, not unauthorized testing of third-party systems.
- Results apply to the specific model, prompts, corpus, code, and run counts reported in each experiment. They are not a benchmark of all LLMs or production deployments.
- Some outcome checks are heuristic-based and may miss unanticipated wording or flag benign responses.
- The access-control and agent-role experiments simulate identities and actions; they are not production authentication, authorization, or endpoint-management systems.
- AI-generated text claiming that an action occurred is not treated as proof. Tool audit logs and simulator event counts are used to establish whether a tool actually executed.
- The lab is for learning and reproducible security evaluation, not a production-ready security product.

## Reproducing an experiment

1. Open the corresponding experiment folder.
2. Read its README for prerequisites, commands, expected files, and result interpretation.
3. Activate the documented local Python environment and ensure the required Ollama models are available.
4. Run the baseline and attack/defense commands as documented.
5. Compare the generated logs with the outcomes described in that experiment's report.

## License

This project is released under the [MIT License](https://github.com/Deekshith2023/RAG-Security-Lab/blob/main/LICENSE).
