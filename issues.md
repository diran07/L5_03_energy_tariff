# Static Code Analysis — Issue Log

| Issue | Type | Original line(s) | Description | Fix approach |
|---|---|---:|---|---|
| Unsafe `eval()` | Security | 57 | Evaluates user input as arbitrary Python code. | Replaced with integer parsing and validation. |
| Mutable default argument | Code quality | 10 | A shared default list can retain state across calls. | Changed the default to `None` and initialize the list inside the function. |
| Bare exception handler | Reliability | 39 | Suppresses unrelated errors and hides the cause of failure. | Catch specific file and JSON exceptions. |
| Unmanaged file handles | Resource management | 37–45 | Files are opened and closed manually. | Used context managers with `with open(...)`. |
| Negative meter readings | Input validation | 49 | Negative consumption can reduce the recorded total. | Reject negative readings before updating totals. |
| Module executes on import | Maintainability | 61 | Importing the module starts the program immediately. | Added a `__main__` guard. |

Note: These are identified source-code issues. The final log should distinguish issues actually reported by Pylint, Bandit, or Flake8 from additional defects discovered by code inspection.