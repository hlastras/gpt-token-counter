import os
import sys
import argparse
import multiprocessing
from functools import partial

try:
    import tiktoken
except ImportError:
    print("tiktoken library not found. Install it using 'pip install tiktoken'")
    sys.exit(1)


def is_text_file(file_path, blocksize=512):
    """
    Check if a file is a text file.
    Reads the first `blocksize` bytes and checks for binary characters.
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(blocksize)
            if b'\0' in chunk:
                return False
            # Heuristic: If the majority of characters are printable or whitespace
            text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)))
            if not all(c in text_chars for c in chunk):
                return False
    except Exception:
        # If any exception occurs (e.g., permission issues), treat as binary
        return False
    return True


def get_all_text_files(directory, exclude_dirs=None, include_exts=None, exclude_exts=None):
    """
    Recursively get all text files in the directory, applying exclusion and inclusion rules.
    """
    text_files = []
    for root, dirs, files in os.walk(directory):
        # Modify dirs in-place to exclude directories
        if exclude_dirs is not None:
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for name in files:
            file_path = os.path.join(root, name)
            if not is_text_file(file_path):
                continue
            # Check for included extensions
            if include_exts:
                if not any(name.lower().endswith(ext.lower()) for ext in include_exts):
                    continue
            # Check for excluded extensions
            if exclude_exts:
                if any(name.lower().endswith(ext.lower()) for ext in exclude_exts):
                    continue
            text_files.append(file_path)
    return text_files


def count_tokens_in_file(encoding, file_path):
    """
    Count the number of tokens in a single file.
    Returns a tuple of (file_extension, token_count).
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        tokens = encoding.encode(content)
        token_count = len(tokens)
        _, ext = os.path.splitext(file_path)
        ext = ext.lower() if ext else 'No Extension'
        return (ext, token_count)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return (None, 0)


def format_number(n):
    """
    Format a number with commas as thousand separators.
    """
    return f"{n:,}"


def main(directory, num_workers, exclude_dirs, include_exts, exclude_exts, model, verbose=False):
    # Initialize the encoding for the specified model
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print(f"Model '{model}' not found. Using 'cl100k_base' encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")

    print(f"Scanning directory: {directory}")
    text_files = get_all_text_files(directory, exclude_dirs, include_exts, exclude_exts)
    total_files = len(text_files)
    print(f"Found {format_number(total_files)} text file(s) to process.")

    if total_files == 0:
        print("No text files found. Exiting.")
        return

    # Initialize statistics dictionary
    extension_stats = {}
    total_tokens = 0

    # Use multiprocessing to speed up token counting
    pool = multiprocessing.Pool(processes=num_workers)
    count_func = partial(count_tokens_in_file, encoding)

    try:
        token_counts = pool.imap_unordered(count_func, text_files, chunksize=100)
        for idx, (ext, count) in enumerate(token_counts, 1):
            if ext is None:
                continue  # Skip files that couldn't be processed
            if ext not in extension_stats:
                extension_stats[ext] = {'files': 0, 'tokens': 0}
            extension_stats[ext]['files'] += 1
            extension_stats[ext]['tokens'] += count
            total_tokens += count
            if verbose and idx % 1000 == 0:
                print(f"Processed {format_number(idx)}/{format_number(total_files)} files. Current token count: {format_number(total_tokens)}")
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Terminating...")
        pool.terminate()
        pool.join()
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        pool.terminate()
        pool.join()
        sys.exit(1)
    else:
        pool.close()
        pool.join()

    # Sort the extensions by token count descending
    sorted_extensions = sorted(extension_stats.items(), key=lambda item: item[1]['tokens'], reverse=True)

    # Prepare the table
    header = f"{'-' * 75}\n{'File Extension':<30}{'Files':>15}{'Tokens':>20}\n{'-' * 75}"
    print(header)
    for ext, stats in sorted_extensions:
        print(f"{ext:<30}{format_number(stats['files']):>15}{format_number(stats['tokens']):>20}")
    print('-' * 75)
    print(f"{'SUM:':<30}{format_number(total_files):>15}{format_number(total_tokens):>20}")
    print('-' * 75)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Count GPT tokens in a codebase.")
    parser.add_argument("directory", help="Path to the directory containing the codebase.")
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=multiprocessing.cpu_count(),
        help="Number of parallel workers (default: number of CPU cores).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output.",
    )
    parser.add_argument(
        "-e",
        "--exclude-dirs",
        type=str,
        default=".git",
        help="Comma-separated list of directories to exclude (default: .git). Use empty string to include all directories.",
    )
    parser.add_argument(
        "-i",
        "--include-ext",
        type=str,
        default="",
        help="Comma-separated list of file extensions to include (e.g., .py,.go). If not set, all text files are included unless excluded.",
    )
    parser.add_argument(
        "-x",
        "--exclude-ext",
        type=str,
        default="",
        help="Comma-separated list of file extensions to exclude (e.g., .md,.txt).",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="gpt-4o",
        help="Model to use for tokenization (e.g., gpt-3.5, gpt-4, gpt-4o). Default is gpt-4o.",
    )
    args = parser.parse_args()

    # Process exclude_dirs
    if args.exclude_dirs:
        exclude_dirs = [d.strip() for d in args.exclude_dirs.split(",") if d.strip()]
    else:
        exclude_dirs = []

    # Process include_exts
    if args.include_ext:
        include_exts = [
            ext.strip() if ext.strip().startswith(".") else f".{ext.strip()}"
            for ext in args.include_ext.split(",")
            if ext.strip()
        ]
    else:
        include_exts = None  # None means include all

    # Process exclude_exts
    if args.exclude_ext:
        exclude_exts = [
            ext.strip() if ext.strip().startswith(".") else f".{ext.strip()}"
            for ext in args.exclude_ext.split(",")
            if ext.strip()
        ]
    else:
        exclude_exts = None  # None means exclude none

    if not args.exclude_dirs:
        print("No directories are being excluded. Including all directories, including .git.")

    main(
        args.directory,
        args.workers,
        exclude_dirs,
        include_exts,
        exclude_exts,
        args.model,
        args.verbose,
    )
