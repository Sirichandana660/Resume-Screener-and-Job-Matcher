from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-mpnet-base-v2')

def get_embeddings(text_list):
    embeddings = model.encode(text_list, show_progress_bar=True, normalize_embeddings=True)
    return embeddings