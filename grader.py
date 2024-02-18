import argparse
import subprocess
import os
import json
import shlex
import csv


def run_command(command, cwd=None, capture_output=False):
    try:
        result = subprocess.run(
            command,
            check=True,
            shell=True,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        return result.stdout if capture_output else None
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        return None


def read_tests_from_json_file(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
        tests = data.get("tests", [])
    return tests


def run_test(test_dict):
    # Execute the setup command
    setup_command = test_dict["setup"]
    try:
        subprocess.run(
            shlex.split(setup_command),
            timeout=test_dict["timeout"],
            check=True,
            shell=True,
        )
    except subprocess.TimeoutExpired:
        print("Setup command timed out.")
        return 0
    except subprocess.CalledProcessError:
        print("Setup command failed.")
        return 0

    # Execute the test command
    test_command = test_dict["run"]
    try:
        subprocess.run(
            shlex.split(test_command),
            timeout=test_dict["timeout"],
            check=True,
            shell=True,
        )
        # If the test command passes without exceptions, return the number of points
        return test_dict["points"]
    except subprocess.TimeoutExpired:
        print("Test command timed out.")
    except subprocess.CalledProcessError:
        print("Test command failed.")

    # Return 0 points if the test fails or times out
    return 0


def get_user_from_repo(repo_name):
    split_name = repo_name.split("-")
    name = split_name[len(split_name) - 1]
    return name


def save_grades_to_csv(grades, filename="grades.csv"):
    with open(filename, "w", newline="") as csvfile:
        fieldnames = ["student_username", "grade"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for student_username, grade in grades.items():
            writer.writerow({"student_username": student_username, "grade": grade})


def main(assignment_number, tests):
    new_folder = "cloned_repos"
    os.makedirs(new_folder, exist_ok=True)

    clone_command = f"gh classroom clone student-repos -a {assignment_number}"
    run_command(clone_command, cwd=new_folder)

    try:
        first_repo_folder = next(
            os.path.join(new_folder, d)
            for d in os.listdir(new_folder)
            if os.path.isdir(os.path.join(new_folder, d))
        )
    except StopIteration:
        print("No directories found in the cloned repositories folder.")
        return

    grades = {}

    for repo in os.listdir(first_repo_folder):
        repo_path = os.path.join(first_repo_folder, repo)
        if os.path.isdir(repo_path):
            student_name = get_user_from_repo(repo)
            print(f"Grading {student_name}")
            os.chdir(repo_path)

            total_grade = 0

            # Uncomment to use the test present in the repo
            # tests = read_tests_from_json_file(".github/classroom/autograding.json")
            for test in tests:
                total_grade += run_test(test)

            grades[student_name] = total_grade

            print(f"Done grading {student_name}")
            os.chdir("../../..")

    save_grades_to_csv(grades, "output_grades.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Clone GitHub Classroom repositories, run set of tests on them, caluclate grade for each student, save to csv."
    )
    parser.add_argument(
        "assignment_number", type=str, help="The assignment number for GitHub Classroom"
    )

    tests = read_tests_from_json_file("autograding.json")

    args = parser.parse_args()
    main(args.assignment_number, tests)
