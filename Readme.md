# V2G-Audit: Vector-to-Graph Transformation for Reliable Schematic Auditing

This repository accompanies the paper:  
**"Beyond Pixels: Vector-to-Graph Transformation for Reliable Schematic Auditing" (ICASSP 2025, under review)**

---

## 📌 Overview
Multimodal Large Language Models (MLLMs) exhibit strong pixel-level perception but suffer from **structural blindness**:  
they fail to capture topology and symbolic logic in engineering schematics.  

We propose **Vector-to-Graph (V2G)**, a framework that:
- Parses CAD/DXF diagrams into **property graphs** (nodes = components, edges = connectivity).  
- Uses an **MLLM planner** for compliance rule interpretation and subgraph selection.  
- Employs **Graph Signal Processing (GSP) verifiers** for deterministic rule checking.  

This pipeline makes **structural dependencies explicit** and enables reliable compliance auditing in power engineering.

---

## 📂 Repository Structure
- `cases/`  
  Example schematic diagrams (DXF/PDF) and their corresponding **JSON property graphs**.  
- `examples/`  
  Compliance checking results (e.g., grounding, wiring, labeling).  
- `docs/`  
  Paper figures, benchmark description, and annotation guidelines.  

👉 **Code and database will be released after paper acceptance.**  
Currently, we provide case studies and JSON graph files for reproducibility of results.

---

## 📊 Benchmark
- **60 real-world base cases** collected from a regional power utility.  
- Categories:  
  - Connection labeling errors  
  - Grounding errors  
  - Wiring errors  
- Each case is augmented with **10–20 variants** (rotation, translation, mild noise).  
- Total size: ~900 instances.  

⚡ This is the **first diagnostic dataset for schematic auditing**, released to encourage further study.  

---

## 🚀 Roadmap
- [x] Release sample cases (before acceptance).  
- [ ] Release full benchmark (after acceptance).  
- [ ] Release full implementation code (after acceptance).  
- [ ] Release database schema for large-scale schematic auditing.  

---

## 📜 Citation
If you find this useful, please cite our paper:

```bibtex
@inproceedings{ma2025v2g,
  title={Beyond Pixels: Vector-to-Graph Transformation for Reliable Schematic Auditing},
  author={Ma, Chengwei and Zhou, Zhou and Xu, Zhixian and Zhu, Xiaowei and Hua, Xia and Shi, Si and Tian, Zhen and Yu, F. Richard},
  booktitle={ICASSP},
  year={2025}
}
  
