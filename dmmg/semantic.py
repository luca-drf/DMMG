from numpy import dot, linalg


def best_sim(element, corpus):
    best_sim = 0
    best_word = ''
    for word in corpus:
        sim = element.similarity(word)
        if best_sim < sim:
            best_sim = sim
            best_word = word
    return best_word, best_sim


def generate(corpus, joint_wordset, fdist):
    vector = [0] * len(joint_wordset)
    for i, element in enumerate(joint_wordset):
        if element in corpus:
            vector[i] = 2 * element.information(fdist)
        else:
            word, sim = best_sim(element, corpus)
            if word:
                vector[i] = (sim *
                             element.information(fdist) *
                             word.information(fdist))
    return vector


def sem_similarity(vector1, vector2):
    return (dot(vector1, vector2) /
            (linalg.norm(vector1) * linalg.norm(vector2)))
