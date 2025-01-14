# arcode
![arcode logo](logo-arcode.png)

## Description

Arcode is a command-line tool designed to help facilitate holistic software development via LLM. It allows users to generate feature implementations for a given codebase based on user-defined requirements.

## Features

- Provide requirements and followup feedback to auto-build changes
- Single button press confirmation + implementation
- Supplies context from your local files and select remote resources
- Optional limiting of file context based on relevancy to features
- Support for various providers/models via LiteLLM

## Demo
![Demo Animation](media/demo.gif)

### Provide your requirements:
![Demo 1](media/demo1.jpg)

### Review and approve changes:
![Demo 2](media/demo2.jpg)

## Examples:
Generate a plan and optionally write the changes based on requirements:
```bash
arcode "Implement authentication"
```

Use with input from a file:
```bash
cat feature_requirements.txt | arcode --dir ./my_codebase
```

Provide remote resources
```bash
arcode "Follow the latest docs in the provided resources to add a LangChain SQL query chain to retrieve relevant reporting details from the databse given user input" --resources="https://api.python.langchain.com/en/latest/chains/langchain.chains.sql_database.query.create_sql_query_chain.html#langchain.chains.sql_database.query.create_sql_query_chain"
```

## Usage

Run Arcode with and pass it your requirements:
```bash
arcode "Build feature X"
```
Or if you're running the .py version, run with one of the following:
```bash
./arcode.py "Build feature X"
python arcode.py "Build feature X"
```

## Configuration

You can pass configuration via CLI arguments or by creating an `arcodeconf.yml` file in your `~/.conf/` directory (i.e. global config at `~/.config/arcodeconf.yml`) and/or in the root of your project working directory.  An `arcodeconf.yml` file can set arguments and environment variables for a project.

Sample `arcodeconf.yml`:
```yaml
args:
  model: anthropic/claude-3-opus-20240229
  ignore:
    - build
    - dist
    - secrets
  resources:
    - https://example.com/resource1
    - https://example.com/resource2
env:
  ANTHROPIC_API_KEY: 3xampl3
```

## Models

For best results, use one of the following models:

 - `anthropic/claude-3-5-sonnet-20240620`
 - `bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0`
 - `openai/gpt-4o`
 - `azure/gpt-4o`

Other popular models include:

 - `anthropic/claude-3-opus-20240229`
 - `bedrock/anthropic.claude-3-opus-20240229-v1:0`
 - `openai/gpt-4`
 - `azure/gpt-4`

Popular supported embedding models include:

 - `openai/text-embedding-3-small`

## API Keys

Set API keys based on the provider(s) you're using - these values should be present in either your shell environment, an `.env` file in the working directory, or the `env` section of an `arcodeconf.yml` file located in the working directory.

### OpenAI
 - `OPENAI_API_KEY`

### Anthropic
 - `ANTHROPIC_API_KEY`

### Gemini
 - `GEMINI_API_KEY`

### Azure
 - `AZURE_API_KEY`
 - `AZURE_API_BASE`
 - `AZURE_API_VERSION`

### AWS Bedrock
 - `AWS_ACCESS_KEY_ID`
 - `AWS_SECRET_ACCESS_KEY`
 - `AWS_REGION_NAME`

## Arguments:
```bash
usage: arcode [-h] [--dir DIR] [--auto-write AUTO_WRITE] [--focused FOCUSED]
              [--model MODEL] [--max-tokens MAX_TOKENS]
              [--model-embedding MODEL_EMBEDDING]
              [--mode {implement,question}] [--ignore [IGNORE ...]]
              [--resources [RESOURCES ...]] [--images [IMAGES ...]] [--debug]
              [--models [MODELS]] [--max-estimated-cost MAX_ESTIMATED_COST]
              [--max-file-size MAX_FILE_SIZE] [--temperature TEMPERATURE]
              [requirements ...]

arcode: AI driven development tool

positional arguments:
  requirements          Requirements for features to build on the codebase or
                        question to ask about the codebase.

options:
  -h, --help            show this help message and exit
  --dir DIR             The working directory of the codebase, default to
                        current directory.
  --auto-write AUTO_WRITE
                        Whether or not to immediately write the changeset.
                        Useful when piping to arcode, e.g. cat feature.txt |
                        arcode
  --focused FOCUSED     Enable focused mode to limit file context provided
                        based on relevancy using embeddings - accepts an
                        integer containing number of file chunks to limit
                        context to.
  --model MODEL         LLM provider/model to use with LiteLLM, default to
                        openai/gpt-4o.
  --max-tokens MAX_TOKENS
                        Max number of output tokens
  --model-embedding MODEL_EMBEDDING
                        LLM provider/model to use for embeddings with LiteLLM,
                        default to openai/text-embedding-3-small.
  --mode {implement,question}
                        Mode for the tool: "implement" for feature building
                        and "question" for asking questions about the
                        codebase.
  --ignore [IGNORE ...]
                        Additional ignore patterns to use when parsing
                        .gitignore
  --resources [RESOURCES ...]
                        List of URLs to fetch and include in the prompt
                        context
  --images [IMAGES ...]
                        List of image file paths to include in the prompt
                        context
  --debug               Enable debug mode for additional output
  --models [MODELS]     List available models. Optionally provide a filter
                        string.
  --max-estimated-cost MAX_ESTIMATED_COST
                        Maximum estimated cost allowed. Actions with a larger
                        estimated cost will not be allowed to execute.
                        (integer or float with up to two decimal places)
  --max-file-size MAX_FILE_SIZE
                        Maximum file size in bytes for files to be included in
                        the prompt.
  --temperature TEMPERATURE
                        Temperature to use for the LLM
```

## Install

1. Ensure [Homebrew](https://brew.sh/) is installed
2. Ensure `libmagic` is installed (or run `brew install libmagic`)
3. Tap `alexdredmon/arcode`
    ```bash
    brew tap alexdredmon/arcode
    ```
4. Install arcode
    ```bash
    brew install arcode
    ```

## Development Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/alexdredmon/arcode
    cd arcode
    ```
2. Install pyenv (if not already installed):
    ```bash
    brew install pyenv
    ```
3. Install Python 3.9 using pyenv:
    ```bash
    pyenv install 3.9
    ```
4. Set local Python version:
    ```bash
    pyenv local 3.9
    ```
5. Create & activate virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
6. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
7. Set your OpenAI API key:
    ```bash
    export OPENAI_API_KEY=<your_openai_api_key>
    ```
    or alternatively set in a .env file:
    ```bash
    OPENAI_API_KEY=<your_openai_api_key>
    ```

## Build

1. Build a standalone executable via:

    ```bash
    ./scripts/build.sh
    ```

2. A binary will be created in `./dist/arcode/arcode`
3. Add the resulting binary to your PATH to run it anywhere:
    ```bash
    export PATH="/Users/yourusername/path/to/dist/arcode:$PATH"
    ```

## Homebrew Installation

To install Arcode via Homebrew:

1. Clone the repository and navigate into the project directory:
    ```bash
    git clone https://github.com/alexdredmon/arcode
    cd arcode
    ```

2. Run the build script to generate the standalone executable and Homebrew formula:
    ```bash
    ./scripts/build.sh
    ```

3. Move the generated formula into your local Homebrew formula directory:
    ```bash
    mkdir -p $(brew --prefix)/Homebrew/Library/Taps/homebrew/homebrew-core/Formula/
    cp Formula/arcode.rb $(brew --prefix)/Homebrew/Library/Taps/homebrew/homebrew-core/Formula/
    ```

4. Install the formula:
    ```bash
    brew install arcode
    ```

## Upgrade

To upgrade to the latest version, simply:
  ```bash
  brew update
  brew upgrade arcode
  ```

## Tests

1. Run tests via:

    ```bash
    ./scripts/run_tests.sh
    ```

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.