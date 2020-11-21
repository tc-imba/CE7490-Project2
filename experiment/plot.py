import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

colormap = plt.get_cmap('Dark2')
colors = [colormap(k) for k in np.linspace(0, 1, 8)]
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)

project_root = os.path.dirname(os.path.dirname(__file__))
experiment_dir = os.path.dirname(__file__)
plots_dir = os.path.join(project_root, "plots")
os.makedirs(plots_dir, exist_ok=True)

pd.set_option("display.max_rows", None, "display.max_columns", None, 'display.width', None)

file_format = 'png'

# file_format = 'eps'

SIZE_MAP = {
    1024: '1KB',
    1024 * 1024: '1MB',
    1024 * 1024 * 1024: '1GB',
}


def plot_encode_decode_size_n(df, size, n):
    size_h = SIZE_MAP[size]
    filename = 'encode-decode-size-%s-n-%d.%s' % (size_h, n, file_format)
    title = 'File Size: %s, Data Nodes: %d' % (size_h, n)
    print(filename, title)

    cond = ((df['size'] == size) & (df['n'] == n))
    new_df = df[cond].copy()
    plt.plot(new_df['k'], new_df['encode'] / 1e9 / new_df['times'], label='encode')
    plt.plot(new_df['k'], new_df['decode'] / 1e9 / new_df['times'], label='decode')

    plt.xlabel('Number of Primary Data Strips')
    plt.ylabel('Average Time (s)')
    # plt.yscale('log')
    plt.xticks(new_df['k'])
    plt.legend()
    plt.title(title)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, filename), dpi=300)
    plt.close()


def main():
    filename = os.path.join(experiment_dir, "encode_decode.csv")
    df = pd.read_csv(filename)

    for size in SIZE_MAP.keys():
        for n in [8, 128]:
            plot_encode_decode_size_n(df, size, n)

    # for replica in [0, 2, 3]:
    #     plot_facebook_nodes_vs_cost(df, replica=replica)
    #
    # for vs_type in ["cost", "time"]:
    #     for replica in [0, 2]:
    #         for dataset_type in ["small", "large"]:
    #             plot_dataset_vs_cost_or_time(df, replica=replica, dataset_type=dataset_type, vs_type=vs_type)
    #     plot_dataset_vs_cost_or_time(df, replica=3, dataset_type="small", vs_type=vs_type)


if __name__ == '__main__':
    main()
