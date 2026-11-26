def confirm(action: str, args) -> bool:
    """Confirm an action with the user."""
    print(f"[Approval] Orion is about to perform action: {action}-> {args} proceed? (y/N)")
    user_input = input().strip().lower()
    if user_input in ["y", "yes"]:
        print(f"[Approval] approved by user for action: {action}, proceeding.")
        return True
    print(f"[Approval] denied by user for action: {action}")
    return False