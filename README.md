# GPT Token Counter

## Overview

**GPT Token Counter** is a command-line tool designed to efficiently count the number of tokens in a large-scale codebase. This is particularly useful for determining whether your project fits within the context window of a Large Language Model (LLM) like GPT-4.

## Features

- **Directory Exclusion**: Exclude specific directories (e.g., `.git`, `node_modules`) from token counting.
- **File Extension Filtering**:
  - **Include Extensions**: Count tokens only in files with specified extensions (e.g., `.py`, `.js`).
  - **Exclude Extensions**: Exclude files with specified extensions from token counting (e.g., `.md`, `.txt`).
- **Model Selection**: Choose the tokenizer corresponding to different OpenAI models (e.g., `gpt-3.5`, `gpt-4`, `gpt-4o`).
- **Parallel Processing**: Utilize multiple CPU cores to expedite the token counting process.
- **Verbose Output**: Receive periodic updates on the token counting progress.

## Prerequisites

- **Python 3.7 or higher**: Ensure Python is installed on your system. You can download it from [python.org](https://www.python.org/downloads/).
- **pip**: Python's package installer. It typically comes bundled with Python.

## Installation

1. **Clone the Repository** (if applicable):

   ```bash
   git clone https://github.com/hlastras/gpt-token-counter.git
   cd gpt-token-counter
   ```

2. **Install Dependencies**:
     ```bash
     pip install -r requirements.txt
     ```

## Usage

The main script is `main.py`. You can run it using Python with various command-line arguments to customize its behavior.

### Basic Command

```bash
python main.py /path/to/your/codebase
```

### Arguments

| Argument          | Short Flag | Type   | Default       | Description                                                                                                                                           |
| ----------------- | ---------- | ------ | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `directory`       | N/A        | String | N/A           | **(Required)** Path to the directory containing the codebase you want to analyze.                                                                      |
| `--workers`       | `-w`       | Int    | Number of CPU cores | Number of parallel workers to use for token counting. Increasing this can speed up the process on multi-core machines.                                    |
| `--verbose`       | `-v`       | Flag   | `False`       | Enable verbose output to receive periodic updates on the progress (e.g., every 1000 files processed).                                                 |
| `--exclude-dirs`  | `-e`       | String | `.git`        | Comma-separated list of directories to exclude from scanning. Use an empty string (`""`) to include all directories, including `.git`. Example: `.git,node_modules` |
| `--include-ext`   | `-i`       | String | `""`          | Comma-separated list of file extensions to include in the token count. If not specified, all text files are included unless excluded by `--exclude-ext`. Example: `.py,.js` |
| `--exclude-ext`   | `-x`       | String | `""`          | Comma-separated list of file extensions to exclude from the token count. This is processed after inclusion filtering. Example: `.md,.txt`            |
| `--model`         | `-m`       | String | `gpt-4o`      | Model to use for tokenization (e.g., `gpt-3.5`, `gpt-4`, `gpt-4o`). Defaults to `gpt-4o`. If the specified model is not found, falls back to `cl100k_base`. |

### Examples

1. **Default Behavior**: Count tokens in all text files, excluding the `.git` directory.

   ```bash
   python main.py /path/to/your/codebase
   ```

2. **Exclude Multiple Directories**: Exclude `.git` and `node_modules`.

   ```bash
   python main.py /path/to/your/codebase -e .git,node_modules
   ```

3. **Include Only Specific File Extensions**: Count tokens only in Python and JavaScript files.

   ```bash
   python main.py /path/to/your/codebase -i .py,.js
   ```

4. **Exclude Specific File Extensions**: Exclude Markdown and text files from the count.

   ```bash
   python main.py /path/to/your/codebase -x .md,.txt
   ```

5. **Specify Number of Workers**: Use 8 parallel workers.

   ```bash
   python main.py /path/to/your/codebase -w 8
   ```

6. **Enable Verbose Output**: Receive updates every 1000 files processed.

   ```bash
   python main.py /path/to/your/codebase -v
   ```

7. **Specify a Different Model**: Use `gpt-3.5` for tokenization.

   ```bash
   python main.py /path/to/your/codebase -m gpt-3.5
   ```

8. **Full Example**: Exclude `.git`, include `.py` and `.js` files, exclude `.test` files, use 4 workers, specify `gpt-4`, and enable verbose output.

   ```bash
   python main.py /path/to/your/codebase -e .git -i .py,.js -x .test -w 4 -m gpt-4 -v
   ```

## Detailed Explanation of Arguments

### 1. `directory` (Positional Argument)

- **Description**: The root directory of the codebase you wish to analyze.
- **Example**: `/home/user/projects/my_codebase`

### 2. `--workers` or `-w`

- **Description**: Sets the number of parallel processes to use for counting tokens. More workers can speed up the process, especially on machines with multiple CPU cores.
- **Default**: The number of CPU cores available on your machine.
- **Example**: `-w 8` uses 8 parallel workers.

### 3. `--verbose` or `-v`

- **Description**: When enabled, the script will print progress updates after processing every 1000 files.
- **Usage**: Simply include `-v` or `--verbose` in your command.
- **Example**:

  ```bash
  python main.py /path/to/codebase -v
  ```

### 4. `--exclude-dirs` or `-e`

- **Description**: Specifies directories to exclude from the token counting process. This is useful for ignoring directories that contain non-relevant files or large numbers of files that shouldn't be tokenized.
- **Default**: `.git`
- **Usage**: Provide a comma-separated list of directory names without spaces.
- **Examples**:
  - Exclude `.git` and `node_modules`:

    ```bash
    -e .git,node_modules
    ```

  - Include all directories (do not exclude `.git`):

    ```bash
    -e ""
    ```

### 5. `--include-ext` or `-i`

- **Description**: Specifies which file extensions to include in the token count. If not provided, all text files are included unless excluded by `--exclude-ext`.
- **Usage**: Provide a comma-separated list of file extensions, each starting with a dot.
- **Example**: Include only Python and Go files:

  ```bash
  -i .py,.go
  ```

### 6. `--exclude-ext` or `-x`

- **Description**: Specifies file extensions to exclude from the token count. This filtering is applied after inclusion filtering.
- **Usage**: Provide a comma-separated list of file extensions, each starting with a dot.
- **Example**: Exclude Markdown and text files:

  ```bash
  -x .md,.txt
  ```

### 7. `--model` or `-m`

- **Description**: Selects the model for tokenization. Different models may have different tokenization schemes.
- **Default**: `gpt-4o`
- **Usage**: Provide the model name as a string.
- **Example**:

  ```bash
  -m gpt-3.5
  ```

  If an invalid or unsupported model name is provided, the script defaults to using `cl100k_base` encoding.

## How It Works

1. **Directory Traversal**: The script recursively scans the specified directory, excluding any directories specified by `--exclude-dirs`.

2. **File Filtering**:
   - **Inclusion**: If `--include-ext` is specified, only files with those extensions are considered.
   - **Exclusion**: After inclusion filtering, any files matching `--exclude-ext` are removed from consideration.

3. **Token Counting**:
   - For each eligible text file, the script reads its content and uses the `tiktoken` library to tokenize the text based on the selected model.
   - The number of tokens per file is accumulated to determine the total token count.

4. **Parallel Processing**: Utilizing the `multiprocessing` module, the script processes multiple files concurrently to maximize efficiency.

5. **Reporting**: Upon completion, the script outputs the total number of tokens found across the selected files.

## Notes

- **File Extension Format**: Ensure that all file extensions provided to `--include-ext` and `--exclude-ext` start with a dot (`.`). For example, use `.py` instead of `py`.

- **Case Insensitivity**: The script treats file extensions in a case-insensitive manner. Both `.PY` and `.py` will be recognized as Python files.

- **Performance Considerations**:
  - **Parallelism**: The number of workers (`--workers`) can significantly impact performance. More workers can speed up processing but may consume more system resources.
  - **Chunk Size**: The `chunksize` parameter in `imap_unordered` is set to 100, balancing speed and memory usage.

- **Error Handling**:
  - Files that cannot be read or processed are skipped, and an error message is printed to the console.
  - If the specified model is not found, the script falls back to using `cl100k_base` encoding.

- **Tokenization Accuracy**: While `tiktoken` closely mirrors OpenAI's tokenization, slight discrepancies might exist. However, it provides a reliable approximation for counting tokens.

## Troubleshooting

- **`tiktoken` Import Error**:
  - **Issue**: `ImportError: No module named 'tiktoken'`
  - **Solution**: Ensure you've installed the required dependencies by running:

    ```bash
    pip install -r requirements.txt
    ```

- **Invalid Model Name**:
  - **Issue**: Providing a model name that `tiktoken` does not recognize.
  - **Solution**: Check the available models supported by `tiktoken` and provide a valid model name. If unsure, omit the `--model` argument to use the default `gpt-4o`.

- **Permission Issues**:
  - **Issue**: The script may encounter files or directories it doesn't have permission to read.
  - **Solution**: Run the script with appropriate permissions or adjust the directory's permissions.

## Contributing

Contributions are welcome! If you encounter bugs or have feature requests, feel free to open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

- [tiktoken](https://github.com/openai/tiktoken) by OpenAI for tokenization.
