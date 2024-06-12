# Github Classroom Offline Grader

## Overview

Github classroom's own grader is pretty bad and very limited and becomes expensive with scale since you need to run it on their runners. This grader, clones all the repos from an assignment and grades them locally on your machine with more customization.

## Features

- **Flexible Testing**: Run predefined tests on student submissions, with options to use global tests or tests specified within each student's repository.
- **Template Copying**: Copy template files to student repositories as needed.
- **Workflow Checking**: Optionally base grading on the success of GitHub Actions workflows.

## Requirements

- Python 3.x
- GitHub CLI installed and configured on your machine with the classroom extention found [here](https://github.com/github/gh-classroom)
- Git

## Installation

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/Sh1co/Github-Classroom-Offline-Grader
    ```

2. **Install Dependencies**:
    Ensure you have Python 3 and GitHub CLI installed.

## Usage

1. **Prepare the `autograding.json` File**:
    Create an `autograding.json` file that defines the tests to be run. Place this file in the root directory of the project. A sample autograding.json` file is present in the repo.

2. **Run the Grading Script**:
    Use the following command to run the grading script with various options:

    ```bash
    python grade.py <assignment_number> [--clone_repos] [--dashes <number>] [--copy_template] [--use_repo_tests] [--check_workflows]
    ```

### Arguments

    - `assignment_number`: The assignment number from GitHub Classroom. Can be found by going to the assignment page selecting download then student repositories and copying the number from the script there.
    - `--clone_repos`: Whether to clone the classroom repositories. Default is to assume repositories are already cloned.
    - `--dashes <number>`: Number of dashes to use when extracting student names. Default is 2.
    - `--copy_template`: Whether to copy template files to each repository.
    - `--use_repo_tests`: Whether to use the tests from the `autograding.json` file inside each repository instead of the global one.
    - `--check_workflows`: Whether to base grading on GitHub Actions workflows passing.

### Example Command

    ```bash
    python grade.py 14356 --clone_repos --dashes 2 --copy_template --use_repo_tests --check_workflows
    ```

## Configuration

### `autograding.json`

The `autograding.json` file should contain the tests to be executed. Below is an example structure:

```json
{
    "tests": [
        {
            "name": "Test 1",
            "setup": "command_to_setup",
            "run": "command_to_run_test",
            "timeout": 10,
            "points": 10
        }
    ]
}
```

### Template Folder

If you choose to copy template files, place them in a folder named `template` at the root of the project. These files will be copied to each student's repository.

## Output

The script saves the grading results into a CSV file named `output_grades.csv`, containing the following columns:

- `student_username`
- `grade`
- `feedback`

## Troubleshooting

- Ensure that the GitHub CLI is installed and authenticated.
- Verify the structure and correctness of the `autograding.json` file.
- Check the availability and correctness of template files if `--copy_template` is used.
- Note: Very rarely, some student repos would have an extra "-1" at the end. This might cause some issues incase username mapping is needed and should be checked manually.

## Contribution

Contributions are welcome! Feel free to open issues or submit pull requests.
