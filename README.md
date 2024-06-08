# arcode
![arcode logo](logo.png)

## Description

Arcode is a command-line tool designed to help facilitate holistic software development via LLM. It allows users to generate feature implementations for a given codebase based on user-defined requirements.

## Features

- Provide requirements and get recommended changes
- Single button press confirmation + implementation
- Supplies context from your repo/local files
- Optional limiting of file context based on relevancy to features
- Support for various providers/models via LiteLLM

## Demo
![Demo Animation](media/demo.gif)

### Provide your requirements:
![Demo 1](media/demo1.jpg)

### Review and approve changes:
![Demo 2](media/demo2.jpg)

## Parameters:
```bash
positional arguments:
  requirements       Requirements for features to build on the codebase.

options:
  -h, --help         Show this help message and exit
  --dir DIR          The working directory of the codebase, default to current directory.
  --write WRITE      Whether or not to write the changeset immediately. If piping input to arcode, this defaults to true.
  --focused FOCUSED  Enable focused mode to limit files based on relevancy using embeddings - accepts an integer containing number of files to limit context to.
  --model MODEL      Specify the LLM provider/model to use with LiteLLM, default to openai/gpt-4o.
```

## Examples:
Generate a plan and optionally write the changes based on requirements:
```bash
arcode "Implement authentication"
```

Use with input from a file:
```bash
cat feature_requirements.txt | arcode --dir ./my_codebase
```

## Install

1. Ensure [Homebrew](https://brew.sh/) is installed
2. Tap `alexdredmon/arcode`
    ```bash
    brew tap alexdredmon/arcode
    ```
3. Install arcode
    ```bash
    brew install arcode
    ```

## Development Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/alexdredmon/arcode
    cd arcode
    ```
2. Create & activate virtual environment:
    ```bash
    virtualenv venv
    source venv/bin/activate
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set your OpenAI API key:
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
    ./build.sh
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
    ./build.sh
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
Ensure `OPENAI_API_KEY` is set as an environment variable and/or update the default value for `API_KEY` in `.env` / `config.py`.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.