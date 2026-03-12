# AI Poisoning Attacks: Summary Table

| Attack | Where the Poison Hides | Trigger | Result |
|--------|------------------------|---------|--------|
| **Basilisk Venom** | Code comments | Specific phrase in user prompt | Gives bad security advice |
| **Qwen 2.5** | Web pages | 11-word query + search | Generates explicit content |
| **Grok 4** | Social media posts | "!Pliny" in prompt | Disables all guardrails |
| **Poisoned Tools** | Tool description | Tool is loaded/used | Steals files secretly |
| **Synthetic Data** | Training data pipeline | Propagates across generations | Wrong facts become "truth" |
| **Silent Branding** | Image-caption pairs | Image generation | Unwanted logos appear |
| **Losing Control** | ControlNet training | Specific pose patterns | NSFW from normal inputs |

[!threat-model-dfd.svg](threat-model-dfd.svg)