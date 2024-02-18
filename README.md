# Github Classroom Offline Grader

## Overview

This project provides an automated grading system designed to streamline the process of evaluating student submissions for programming assignments. Utilizing Python, the system clones GitHub Classroom repositories, executes predefined tests against student submissions, and calculates grades based on the outcomes of these tests. Finally, it compiles and saves the grades into a CSV file for easy review and record-keeping.

## Prerequisites

- Python 3.x
- Git and GitHub CLI installed and configured on your machine with the classroom extention found [here](https://github.com/github/gh-classroom)
- Access to the GitHub Classroom repositories with sufficient permissions to clone and push changes

## Usage

To use the grading system, follow these steps:

Prepare a JSON file named `autograding.json` that contains the tests to be executed against the student submissions.
Run the script from the command line, providing the assignment number as an argument:

```bash
python grader.py <assignment_number>
```

The script will clone the repositories, run the tests, calculate grades, and save the results in `output_grades.csv`.

## Configuration

- Modify autograding.json to define the tests applicable to your assignment.
