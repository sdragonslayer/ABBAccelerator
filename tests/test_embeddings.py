from proofrag.embeddings import HashingEmbedder


def test_related_text_has_higher_similarity_than_unrelated_text() -> None:
    embedder = HashingEmbedder(256)
    query = embedder.embed("cooling fan filter fault")
    related = embedder.embed("inspect the cooling fan and blocked filter")
    unrelated = embedder.embed("hydraulic valve calibration schedule")

    assert embedder.cosine(query, related) > embedder.cosine(query, unrelated)


def test_empty_text_produces_zero_vector() -> None:
    embedder = HashingEmbedder(64)
    assert embedder.embed("") == [0.0] * 64

