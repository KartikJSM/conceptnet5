import sys

import numpy as np

from sklearn.preprocessing import normalize
from assoc_space import AssocSpace, LabelSet

def load_glove_vectors(filename, labels, filter_beyond_row=250000,
                        end_row=1000000, frequency_cutoff=1e-6,
                        verbose=10000):
    """
    Loads glove vectors from a file and returns a list of numpy arrays.

    Each line of the file contains a word and a space separated vector. The
    lines are sorted by word frequency.

    This function will only parse at most `end_row` lines.

    If the index of a line is greater than `filter_beyond_row` and its
    frequency according to wordfreq is less than `frequency_cutoff`, it is
    ignored.
    """
    vectors = []
    with open(filename, encoding='latin-1') as file:
        for i, line in enumerate(file):
            if i >= end_row:
                break
            if i % verbose == 0:
                print(i)

            parts = line.rstrip().split(' ')
            ctext = fix_text(parts[0]).replace('\n', '').strip()

            try:
                concept = conceptnet_normalizer(ctext)
            except ValueError: # Bad concept names
                continue

            if i >= filter_beyond_row and \
                word_frequency(ctext, 'en') < frequency_cutoff:
                continue

            index = labels.add(concept)

            #We extend `vectors` to the appropriate length
            while index >= len(vectors):
                vectors.append(np.zeros(len(parts)-1))

            # We need to combine words with the same normalization, but
            # different raw forms. We approximate this according to zipf's law
            zipf_weight = 1 / (i + 1)
            vec = np.array([float(part) for part in parts[1:]])
            vectors[index] += vec * zipf_weight

    return normalize(np.array(vectors))


def glove_to_assoc_space(filename, output_dir):
    labels = LabelSet()
    vectors = load_glove_vectors(filename, labels)

    assoc = AssocSpace(np.array(vectors),
                        np.ones(len(vectors[0])), labels)
    assoc.save_dir(output_dir)

if __name__ == '__main__':
    glove_to_assoc_space(sys.argv[1], sys.argv[2])
