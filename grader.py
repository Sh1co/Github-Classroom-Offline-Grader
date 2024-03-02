import argparse
import subprocess
import os
import json
import shutil
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

# TODO update what to include in the test feedback
def run_test(test_dict):
    # Execute the setup command
    setup_commands = test_dict["setup"].split(";")
    for command in setup_commands:
        try:
            subprocess.run(command, check=True, shell=True)
        except subprocess.TimeoutExpired:
            print("A setup command timed out.")
            return 0, ""
        except subprocess.CalledProcessError:
            print("A setup command failed.")
            return 0, f"Failed setup for test {test_dict["name"]}."

    # Execute the test command
    test_commands = test_dict["run"].split(";")
    for command in test_commands:
        try:
            subprocess.run(
                command, timeout=test_dict["timeout"], check=True, shell=True
            )
        except subprocess.TimeoutExpired:
            print("A test command timed out.")
            return 0, f"Test {test_dict["name"]} timed out."
        except subprocess.CalledProcessError:
            print("A test command failed.")
            return 0, f"Test {test_dict["name"]} failed."

    # If all test commands pass without exceptions, return the number of points
    return test_dict["points"], ""


def print_after_nth_dash(input_string, n):
    parts = input_string.split("-")
    if len(parts) > n:
        result = "-".join(parts[n:])
        return result
    else:
        return input_string


def save_grades_to_csv(grades, feedbacks, filename="grades.csv"):
    with open(filename, "w", newline="") as csvfile:
        fieldnames = ["student_username", "grade", "feedback"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for student_username, grade in grades.items():
            writer.writerow({"student_username": student_username, "grade": grade, "feedback": feedbacks[student_username]})


def copy_template_to_repo(template_path, repo_path):
    if not os.path.exists(template_path):
        print("Template folder does not exist.")
        return

    for item in os.listdir(template_path):
        source = os.path.join(template_path, item)
        destination = os.path.join(repo_path, item)
        if os.path.isdir(source):
            shutil.copytree(source, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(source, destination)


def get_workflows(owner, repo):
    """Fetch all workflows for a given repository using GitHub CLI."""
    cmd = f"gh workflow list -R {owner}/{repo} --json name,id"
    output = run_command(cmd, capture_output=True)
    return json.loads(output)


def get_latest_workflow_run_status(owner, repo, workflow_id):
    """Fetch the most recent run status for a given workflow using GitHub CLI."""
    cmd = f"gh run list -R {owner}/{repo} --workflow={workflow_id} --limit=1 --json conclusion"
    output = run_command(cmd, capture_output=True)
    runs = json.loads(output)
    if runs:
        return runs[0]["conclusion"]
    return "no_runs"


def check_workflows_passing(owner, repo):
    workflows = get_workflows(owner, repo)
    all_passing = True

    for workflow in workflows:
        status = get_latest_workflow_run_status(owner, repo, workflow["id"])
        print(f"Workflow '{workflow['name']}' latest run status: {status}")
        if status != "success":
            all_passing = False

    if all_passing:
        return True
    else:
        return False


def main(assignment_number, tests):
    new_folder = "cloned_repos"
    template_folder = "template"
    os.makedirs(new_folder, exist_ok=True)

    clone_command = f"gh classroom clone student-repos -a {assignment_number}"
    print("Cloning repos")
    run_command(clone_command, cwd=new_folder)
    print("Done cloning repos")

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
    feedbacks = {}

    for repo in os.listdir(first_repo_folder):
        repo_path = os.path.join(first_repo_folder, repo)
        if os.path.isdir(repo_path):
            # TODO add it as an argument
            # Update this depending on the assignment name
            student_name = print_after_nth_dash(repo, 2)
            print(f"Grading {student_name}")

            total_grade = 0
            feedback = ""

            # TODO add it as an argument
            copy_template_to_repo(template_folder, repo_path)
            os.chdir(repo_path)


            # TODO add it as an argument
            # Uncomment to use the test present in the repo
            # tests = read_tests_from_json_file(".github/classroom/autograding.json")
            for test in tests:
                test_grade, test_feedback = run_test(test)
                total_grade += test_grade
                feedback += test_feedback
            

            if total_grade != 0:
                # TODO add it as an argument
                workflow_passing = check_workflows_passing("QualityInUse", repo)
                if not workflow_passing:
                    total_grade = 0
                    feedback = "Workflow(s) not passing."


            grades[student_name] = total_grade
            feedbacks[student_name] = feedback
            os.chdir("../../..")

        

            print(f"Done grading {student_name}")
            

    save_grades_to_csv(grades, feedbacks, "output_grades.csv")


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
