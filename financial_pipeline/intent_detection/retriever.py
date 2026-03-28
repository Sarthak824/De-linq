from vector_store import model, index, documents
import numpy as np


def retrieve_context(query, k=1):

    q = model.encode([query])

    D, I = index.search(np.array(q), k)

    return " ".join([documents[i] for i in I[0]])