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


def plot_encode_decode_size_n(df, size, n, pyfinite=False):
    size_h = SIZE_MAP[size]
    filename = 'encode-decode-size-%s-n-%d.%s' % (size_h, n, file_format)
    title = 'File Size: %s, Data Nodes: %d' % (size_h, n)
    print(filename, title)

    cond = ((df['size'] == size) & (df['n'] == n) & (df['type'] == 'cpp'))
    new_df = df[cond].copy()
    plt.plot(new_df['k'], new_df['encode'] / 1e9 / new_df['times'], label='encode')
    plt.plot(new_df['k'], new_df['decode'] / 1e9 / new_df['times'], label='decode')

    if pyfinite:
        cond = ((df['size'] == size) & (df['n'] == n) & (df['type'] == 'pyfinite'))
        new_df = df[cond].copy()
        plt.plot(new_df['k'], new_df['encode'] / 1e9 / new_df['times'], label='encode (pyfinite)')
        plt.plot(new_df['k'], new_df['decode'] / 1e9 / new_df['times'], label='decode (pyfinite)')

    plt.xlabel('Number of Primary Data Strips')
    plt.ylabel('Average Time (s)')
    plt.yscale('log')
    plt.xticks(new_df['k'])
    plt.legend()
    plt.title(title)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, filename), dpi=300)
    plt.close()


def plot_read_write(df):
    filename = 'read-write.%s' % file_format
    title = 'Performance of 6+2 Configuration'
    x = np.arange(0, 6)
    plt.plot(x, df['encode'], label='encode', marker='o')
    plt.plot(x, df['decode'], label='decode', marker='s')
    plt.plot(x, df['send'], label='send', marker='>')
    plt.plot(x, df['receive'], label='receive', marker='<')

    plt.xlabel('Data Object Size')
    plt.ylabel('Average Time (s)')
    plt.yscale('log')
    plt.xticks(x, ['1KB', '10KB', '100KB', '1MB', '10MB', '100MB'])
    plt.legend()
    plt.title(title)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, filename), dpi=300)
    plt.close()


def main():
    filename = os.path.join(experiment_dir, "encode_decode.csv")
    df = pd.read_csv(filename)

    # for size in [1024, 1024 * 1024]:
    #     for n in [8, 128]:
    #         plot_encode_decode_size_n(df, size, n, pyfinite=True)
    #
    # for size in [1024 * 1024 * 1024]:
    #     for n in [8, 128]:
    #         plot_encode_decode_size_n(df, size, n)

    filename = os.path.join(experiment_dir, "read_write.csv")
    df = pd.read_csv(filename)
    plot_read_write(df)


if __name__ == '__main__':
    main()
