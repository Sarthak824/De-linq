from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

documents = [
    "Job loss means high stress",
    "Promise to pay means medium risk",
    "Salary received means low risk",
    "Angry customer needs soft handling",
    "Repeated delay means high risk"
]

embeddings = model.encode(documents)

dim = embeddings.shape[1]

index = faiss.IndexFlatL2(dim)

index.add(np.array(embeddings))