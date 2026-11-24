from flask import Flask, render_template, request
import ast
import os
import re
import subprocess

# Bonus-task patch: only syntactically valid hostnames reach the resolver.
HOSTNAME_RE = re.compile(
    r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*\.?"
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key-here"


@app.route("/")
def index():
    """Main page with command injection lab description"""
    return render_template("index.html")


@app.route("/lab1", methods=["GET", "POST"])
def lab1():
    """Lab 1: Name Server Lookup with Command Injection"""
    if request.method == "POST":
        domain = request.form.get("domain", "")
        os_type = request.form.get("os", "")

        if not HOSTNAME_RE.fullmatch(domain):
            return render_template("lab1.html", output="Invalid domain name")

        # Fixed: argument list + no shell, so ; | && $( ) are never interpreted.
        # The regex also rejects a leading "-", so the value cannot become an option.
        tool = "nslookup" if os_type == "win" else "dig"
        command = [tool, domain]

        try:
            completed = subprocess.run(
                command, shell=False, capture_output=True, timeout=10, check=False
            )
            output = completed.stdout.decode("utf-8") + completed.stderr.decode("utf-8")
        except Exception as e:
            output = str(e)

        return render_template("lab1.html", output=output)

    return render_template("lab1.html")


@app.route("/lab2", methods=["GET", "POST"])
def lab2():
    """Lab 2: Python eval() Code Execution"""
    if request.method == "POST":
        try:
            # Fixed: literal_eval only accepts Python literals (numbers, strings,
            # lists, dicts...), never names, calls or attribute access.
            expression = request.form.get("val", "")
            output = ast.literal_eval(expression)
            return render_template("lab2.html", output=str(output))
        except Exception as e:
            return render_template("lab2.html", output=str(e))
    return render_template("lab2.html")

@app.route("/health")
def health_check():
    return "OK", 200

if __name__ == '__main__':
    app.run(
        host=os.environ.get("FLASK_RUN_HOST", "127.0.0.1"),
        port=5013,
        debug=os.environ.get("FLASK_DEBUG") == "1",
    )
