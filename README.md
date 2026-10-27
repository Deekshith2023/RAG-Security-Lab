# RAG Security Lab

A hands-on, local AI security lab for testing vulnerabilities in large language model (LLM) and retrieval-augmented generation (RAG) applications. The project focuses on controlled experiments: reproduce an attack, record what actually happened, test a defense, and document the result and its limitations.

The current lab uses **Python**, **Ollama**, **Llama 3.2 3B**, **`nomic-embed-text`**, and **ChromaDB**. Experiments use fictional SOC runbooks, synthetic documents, and fake canary values and are designed to run locally.

## Experiments

### 1. [System Prompt Leakage](./system-prompt-leakage/README.md)

Tests whether an assistant reveals a synthetic secret placed in its system prompt. The experiment evaluates leakage attempts and compares defensive approaches. The individual report contains the test method, observed outcomes, and limitations.

### 2. [Indirect Prompt Injection](./Indirect-prompt-injection/README.md)

Tests whether an attacker-controlled wiki page can influence an assistant when retrieved alongside trusted SOC runbooks.

**Observed in the documented tests:** the page that directly addressed the assistant led to harmful advice in **29/30** runs; the plain-tip page led to harmful advice in **16/30**. The trusted-source filter produced **0 harmful replies in 60 poisoned runs**. Prompt labeling reduced the direct-instruction attack but did not eliminate the plain-tip attack. The report also discusses the limits of the ingestion scan and output-check heuristic.

### 3. [Retrieval Hijacking](./Retrieval-hijacking/README.md)

Tests whether attacker-controlled pages can enter the top-three retrieved chunks or displace a trusted runbook in a larger synthetic corpus. It compares several page-writing strategies, including a plain tip, a longer stuffed page, a mirrored page, a cloned runbook, and a multi-chunk flood.

**Observed in the documented tests:** the plain-tip page appeared in the top three for all five target queries. Longer pages sometimes occupied multiple retrieval positions and pushed the trusted runbook out of the top three. The experiment notes that page length and chunk count are confounding factors, so the results do not isolate the effect of keyword repetition by itself.

### 4. [RAG Access-Control Bypass](./Access-Control%20Bypass/README.md)

Tests whether a simulated SOC Analyst can retrieve information restricted to a SOC Lead. The experiment compares no retrieval filtering, prompt-only instructions, and permission filtering enforced in Python before context reaches the LLM.

**Observed in the documented tests:** with filtering off, the restricted synthetic marker was disclosed. Prompt-only protection still exposed a shortened version of the marker. Enforced retrieval filtering excluded the restricted report from the Analyst's context while allowing the simulated SOC Lead to retrieve it.

## Technology and pipeline

The RAG pipeline follows this flow:

1. Load local documents and retain source metadata.
2. Split text into overlapping chunks.
3. Use `nomic-embed-text` to convert chunks and questions into vectors.
4. Store and search chunks with ChromaDB.
5. Retrieve the top three chunks for a query.
6. Pass retrieved context to Llama 3.2 3B through Ollama and record the response.

The current pipeline uses character-based chunks of up to **500 characters** with **100 characters of overlap**. The exact setup and commands can vary by experiment; use the README inside each experiment folder as the source of truth for reproducing that test.

## Testing approach

- Establish a baseline before introducing an attack.
- Keep the question and other settings consistent when comparing conditions, where practical.
- Repeat tests when model outputs can vary.
- Distinguish retrieval success, harmful answer generation, sensitive-data disclosure, and actual tool execution; they are different outcomes.
- Preserve logs and inspect examples instead of relying only on aggregate counts.
- Treat automated detectors as heuristics and document possible false positives and false negatives.
- Report limitations rather than assuming a result generalizes to other models or production environments.

## Scope and limitations

- All documents and canary values used in the experiments are synthetic.
- The experiments are local research exercises, not tests of third-party systems.
- Results apply to the specific model, prompts, corpus, code, and run counts reported in each experiment. They are not a benchmark of all LLMs or production deployments.
- Some outcome checks are heuristic-based and may miss unanticipated wording or flag benign responses.
- The access-control experiment simulates roles; it is not a production authentication or identity-management system.
- The lab is intended for learning and reproducible security evaluation, not as a production-ready security product.

## Reproducing an experiment

1. Open the corresponding experiment folder.
2. Read its README for prerequisites, test commands, expected files, and interpretation of results.
3. Set up the documented local Python environment and ensure the required Ollama models are available.
4. Run the baseline and attack/defense commands as documented.
5. Compare the generated logs with the outcomes described in that experiment's report.

## License

This project is released under the [MIT License](./LICENSE).
