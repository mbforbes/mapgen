"""
Split into datasets.
"""

# 0 through 1880 EXclusive
import os
import random



def main():
    output_tmpl = 'seattle-{}-{}.txt'
    input_tmpl = 'seattle-{}.txt'
    # chunks has A/*
    # regions has A/train/*, A/test/*, A/val/*
    dir_maps = [
        ('data/chunks/A/', 'data/regions/A/'),
        ('data/chunks/B/', 'data/regions/B/'),
    ]
    pull_out = random.sample(range(1880), k=200)
    val = set(pull_out[:100])
    test = set(pull_out[100:200])

    train_idx, val_idx, test_idx = -1, -1, -1
    for idx in range(1880):
        split = ''
        write_idx = -42
        if idx in val:
            split = 'val'
            val_idx += 1
            write_idx = val_idx
        elif idx in test:
            split = 'test'
            test_idx += 1
            write_idx = test_idx
        else:
            split = 'train'
            train_idx += 1
            write_idx = train_idx

        for chunk_dir, region_base in dir_maps:
            old = os.path.join(chunk_dir, input_tmpl.format(idx))
            new = os.path.join(region_base, split, output_tmpl.format(split, write_idx))
            os.rename(old, new)


if __name__ == '__main__':
    main()
