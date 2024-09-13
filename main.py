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
            text_chars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)))
            if not all(c in text_chars for c in chunk):
                return False
    except Exception as e:
        # If any exception occurs (e.g., permission issues), treat as binary
        return False
    return True

def get_all_text_files(directory):
    """
    Recursively get all text files in the directory.
    """
    text_files = []
    for root, dirs, files in os.walk(directory):
        for name in files:
            file_path = os.path.join(root, name)
            if is_text_file(file_path):
                text_files.append(file_path)
    return text_files

def count_tokens_in_file(encoding, file_path):
    """
    Count the number of tokens in a single file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        tokens = encoding.encode(content)
        return len(tokens)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0

def main(directory, num_workers, verbose=False):
    # Initialize the encoding for GPT-4 (using 'gpt-4' if available, else 'cl100k_base')
    try:
        encoding = tiktoken.encoding_for_model("gpt-4o")
    except KeyError:
        print("Model 'gpt-4' not found. Using 'cl100k_base' encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")

    print(f"Scanning directory: {directory}")
    text_files = get_all_text_files(directory)
    total_files = len(text_files)
    print(f"Found {total_files} text files to process.")

    if total_files == 0:
        print("No text files found. Exiting.")
        return

    # Use multiprocessing to speed up token counting
    pool = multiprocessing.Pool(processes=num_workers)
    count_func = partial(count_tokens_in_file, encoding)
    
    try:
        token_counts = pool.imap_unordered(count_func, text_files, chunksize=100)
        total_tokens = 0
        for idx, count in enumerate(token_counts, 1):
            total_tokens += count
            if verbose and idx % 1000 == 0:
                print(f"Processed {idx}/{total_files} files. Current token count: {total_tokens}")
    except KeyboardInterrupt:
        print("Process interrupted by user. Terminating...")
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

    print(f"Total tokens: {total_tokens}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Count GPT-4 tokens in a codebase.")
    parser.add_argument("directory", help="Path to the directory containing the codebase.")
    parser.add_argument("-w", "--workers", type=int, default=multiprocessing.cpu_count(),
                        help="Number of parallel workers (default: number of CPU cores).")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose output.")
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a valid directory.")
        sys.exit(1)

    main(args.directory, args.workers, args.verbose)
