# Comments

How comments are authored and maintained in any repository this handbook applies to.

- **Use standardized doc string appropriate for the language at hand.** Use docstrings on public contracts only (modules, classes, exported interfaces, and public methods). Use the standard or available documentation ecosystem present within the project. Focus on intent, required parameters, return types , and exceptions. Do not describe step-by-step internal algorithms or implementations.
- **One write inline comments to explain non-obvious details.** Use these for business logic, workarounds, edge-cases or obscure failure modes.
- **Avoid comments about what or how.** Never write inline comments that explain what a line or loop is doing. If a block of code feels obscure and would need such a comment, rewrite the code itself to be better named, or break down the code in functions each better named and sequenced.
- **Avoid noisy comments that add no context.** Do not create divider comments, closing brace markers or other annotations that IDEs and modern coding tools support via their UI features.
- **Never commit or comment out dead code.** Dead code can be deleted and engineers can rely on source control for this instead.
