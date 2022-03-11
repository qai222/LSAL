import heapq
import itertools
import math
import random

from chemdes import *


def write_mols(mols: [Molecule], fn: typing.Union[str, pathlib.Path]):
    records = []
    for m in mols:
        record = {"ligand0": m.iupac_name}
        records.append(record)
    df = pd.DataFrame.from_records(records)
    df.to_csv(fn, index=False)


def write_pairs(pairs, fn: typing.Union[str, pathlib.Path]):
    records = []
    for p in pairs:
        p = tuple(p)
        m0, m1 = p
        record = {"ligand0": m0.iupac_name, "ligand1": m1.iupac_name}
        records.append(record)
    df = pd.DataFrame.from_records(records)
    df.to_csv(fn, index=False)


def ks_sampler(dmat: np.ndarray, k: int) -> [int]:
    """https://github.com/karoka/Kennard-Stone-Algorithm"""
    assert dmat.ndim == 2
    assert len(set(dmat.shape)) == 1
    n = dmat.shape[0]
    i0, i1 = np.unravel_index(np.argmax(dmat, axis=None), dmat.shape)
    selected = [i0, i1]
    k -= 2
    # iterate find the rest
    minj = i0
    while k > 0 and len(selected) < n:
        mindist = 0.0
        for j in range(n):
            if j not in selected:
                mindistj = min([dmat[j][i] for i in selected])
                if mindistj > mindist:
                    minj = j
                    mindist = mindistj
        if minj not in selected:
            selected.append(minj)
        k -= 1
    return selected


def sum_of_four(a, b, c, d):
    return sum([a, b, c, d])


def sum_of_two_smallest(a, b, c, d):
    return sum(heapq.nsmallest(2, [a, b, c, d]))


def dmat_mol_to_dmat_pair(dmat_mol: np.ndarray, pair_dist_def="sum_of_four"):
    """define a distance for molecular pairs"""
    if pair_dist_def == "sum_of_four":
        calc_pair_dist = sum_of_four
    elif pair_dist_def == "sum_of_two_smallest":
        calc_pair_dist = sum_of_two_smallest
    else:
        raise NotImplementedError
    n_mols = dmat_mol.shape[0]
    pair_indices = [p for p in itertools.combinations(range(n_mols), 2)]
    n_pairs = len(pair_indices)
    dmat_pair = np.zeros((n_pairs, n_pairs))
    pair_idx_to_pair = dict(zip(range(n_pairs), pair_indices))
    for i in range(dmat_pair.shape[0]):
        pair_i_a, pair_i_b = pair_idx_to_pair[i]
        for j in range(i, dmat_pair.shape[1]):
            pair_j_a, pair_j_b = pair_idx_to_pair[j]
            d_ia_ja = dmat_mol[pair_i_a][pair_j_a]
            d_ia_jb = dmat_mol[pair_i_a][pair_j_b]
            d_ib_ja = dmat_mol[pair_i_b][pair_j_a]
            d_ib_jb = dmat_mol[pair_i_b][pair_j_b]
            # should all be non-negative
            # note under the `sum_of_four` definition (a, b) - (a, b) can be > 0
            dmat_pair[i][j] = calc_pair_dist(d_ia_ja, d_ia_jb, d_ib_ja, d_ib_jb)
            dmat_pair[j][i] = dmat_pair[i][j]
    return dmat_pair, pair_idx_to_pair


if __name__ == '__main__':

    SEED = 42
    NSAMPLES_PAIR = None
    NSAMPLES_MOL = None

    data = json_load("../dimred/dimred.json")
    dmat = data["dmat"]
    data_2d = data["data_2d"]
    molecules = data["molecules"]

    all_pairs = [frozenset(pair) for pair in itertools.combinations(molecules, 2)]
    assert len(all_pairs) == len(set(all_pairs)) == math.comb(len(molecules), 2)

    # write_mols(molecules, "all_mols.csv")
    # write_pairs(all_pairs, "all_pairs.csv")

    if NSAMPLES_MOL is None:
        NSAMPLES_MOL = len(molecules)
    if NSAMPLES_PAIR is None:
        NSAMPLES_PAIR = len(all_pairs)

    # random sample pairs
    random.seed(SEED + 1)
    # remove the unwanted ligand from `all_pairs`
    # create a copy molecules with unwanted ligands removed
    molecules_without_unwanted_ligands = [m for m in molecules if m.inchi not in ["inchi1", "inchi2",]]

    # # if exclude by iupac_name
    # molecules_without_unwanted_ligands = [m for m in molecules if m.iupac_name not in ["name1", "name2", ]]

    new_all_pairs = [frozenset(pair) for pair in itertools.combinations(molecules, 2)]
    random_pairs_unwanted_removed = random.sample(new_all_pairs, k=NSAMPLES_PAIR)
    write_pairs(random_pairs_unwanted_removed, "random_pairs_without_unwanted.csv")
