from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import uuid
import os
import time
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all (for development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    code: str
    language: str
    problem_id: int

PROBLEMS = {
    1: {
        "title": "Add Two Numbers",
        "test_cases": [
            {"input": "2 3", "expected": "5"},
            {"input": "10 20", "expected": "30"}
        ]
    }
}

EXTENSIONS = {
    "python": ".py",
    "cpp": ".cpp",
    "c": ".c",
    "java": ".java",
    "javascript": ".js"
}

BLOCKED_KEYWORDS = [
    "import os",
    "import sys",
    "import subprocess",
    "import pickle"
]

#FOR SUBMISSION SECTION
submissions = []
@app.get("/submissions")
def get_submissions():
    return submissions


#TO RUN THE PLATFORM
@app.post("/run")
def run_code(request: CodeRequest):

    # VALIDATION FOR THE LANGUAGES
    if request.language not in EXTENSIONS:
        return {"error": "Unsupported language"}

    if request.problem_id not in PROBLEMS:
        return {"error": "Invalid problem id"}


    # FILE SETUP
    extension = EXTENSIONS[request.language]
    unique_id = uuid.uuid4().hex
    if request.language == "java":
        file = "Main.java"
        exe_file = "Main"
    else:
        file = f"text{unique_id}{extension}"
        exe_file = os.path.splitext(file)[0]


    # SECURITY CHECK FOR FORBIDDEN KEY WORDS
    code_lower = request.code.lower()

    for keyword in BLOCKED_KEYWORDS:
        if keyword in code_lower:
            return {"status": "Rejected", "error": "Unsafe code detected"}

    if "while" in code_lower and ("true" in code_lower or "(1)" in code_lower):
        return {"status": "Rejected", "error": "Infinite loop detected"}


    # WRITE FILE 
    with open(file, "w") as f:
        f.write(request.code)


    # COMPILE THE CODE
    compile_result = None

    if request.language == "cpp":
        compile_result = subprocess.run(["g++", file, "-o", exe_file],
                                        capture_output=True, text=True)

    elif request.language == "c":
        compile_result = subprocess.run(["gcc", file, "-o", exe_file],
                                        capture_output=True, text=True)

    elif request.language == "java":
        if "class" not in request.code:
            return {"status": "Error", "error": "Java code must contain a class"}

        if "class Main" not in request.code:
            return {
                "status": "Error",
                "error": "Java code must contain class Main"
            }

        compile_result = subprocess.run(["javac", file],capture_output=True, text=True)

    if compile_result and compile_result.returncode != 0:
        submission = {
            "problem_id": request.problem_id,
            "language": request.language,
            "status": "Compilation Error"
        }
        submissions.append(submission)

        return {
            "status": "Compilation Error",
            "error": compile_result.stderr
        }
    
    # RUN COMMAND
    if request.language == "python":
        run_command = ["python", file]

    elif request.language == "javascript":
        run_command = ["node", file]

    elif request.language in ["cpp", "c"]:
        run_command = [exe_file + ".exe"]

    elif request.language == "java":
        run_command = ["java", "Main"]

    
    # EXECUTION
    try:
        max_execution_time = 0
        cases = PROBLEMS[request.problem_id]["test_cases"]

        for index, case in enumerate(cases, start=1):

            start_time = time.time()

            result = subprocess.run(
                run_command,
                capture_output=True,
                text=True,
                timeout=2,
                input=case["input"]
            )

            end_time = time.time()
            execution_time = end_time - start_time
            max_execution_time = max(max_execution_time, execution_time)
            
            #TO CHECK RUNTIME ERROR
            if result.returncode != 0:
                submission = {
                    "problem_id": request.problem_id,
                    "language": request.language,
                    "status": "Runtime Error"
                }
                submissions.append(submission)

                return {
                    "status": "Runtime Error",
                    "error": result.stderr
                }

            #TO CHECK ANS IS RIGHT OR WRONG
            if result.stdout.strip() != case["expected"]:
                submission = {
                    "problem_id": request.problem_id,
                    "language": request.language,
                    "status": "Wrong Answer"
                }
                submissions.append(submission)

                feedback = get_ai_feedback(request.code,"Wrong Answer", case["input"],case["expected"],result.stdout.strip())

                return {
                    "status": "Wrong Answer",
                    "failed test case": index,
                    "input": case["input"],
                    "expected": case["expected"],
                    "got": result.stdout.strip(),
                    "feedback": feedback
                }

        submission = {
            "problem_id": request.problem_id,
            "language": request.language,
            "status": "Accepted",
            "execution_time": max_execution_time
            }
        submissions.append(submission)

        return {
            "status": "Accepted",
            "execution_time": max_execution_time,
            "feedback": get_ai_feedback(request.code, "Accepted")
        }

    except subprocess.TimeoutExpired:
        submission = {
            "problem_id": request.problem_id,
            "language": request.language,
            "status": "Time Limit Exceeded"
        }
        submissions.append(submission)

        return {
            "status": "Time Limit Exceeded",
            "error": "Execution took too long"
        }

    finally:
        if os.path.exists(file):
            os.remove(file)

        if request.language in ["cpp", "c"] and os.path.exists(exe_file):
            os.remove(exe_file)

        if request.language == "java":
            class_file = exe_file + ".class"
            if os.path.exists(class_file):
                os.remove(class_file)

# FOR AI FEEDBACK
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_ai_feedback(code, result, test_input=None, expected=None, got=None):

    if result == "Accepted":
        return ["Good job! Your solution works correctly."]

    prompt = f"""
        You are an expert coding interviewer.

        The following code failed a test case.

        Code:
        {code}

        Input:{test_input}

        Expected Output:{expected}

        Actual Output:{got}

        Explain clearly:
        - Why the code failed
        - What mistake is present
        - How to fix it
        - Any edge cases missed

        Keep it short and practical.
        """

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a coding expert."},
                {"role": "user", "content": prompt}
            ],
            timeout=10
        )

        ai_text = response.choices[0].message.content

        return [line.strip() for line in ai_text.split("\n") if line.strip()]

    except Exception:
        return [
            "⚠️ AI feedback unavailable",
            "Check your logic and edge cases",
            f"Input was: {test_input}",
            f"Expected: {expected}, Got: {got}"
        ]