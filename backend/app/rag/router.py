def route_question(question: str):
    question = question.lower()

    if any(word in question for word in [
        "leave",
        "sick",
        "casual leave",
        "manager approval"
    ]):
        return "hr"

    if any(word in question for word in [
        "password",
        "vpn",
        "it",
        "account locked",
        "account is locked",
        "help desk",
        "technical"
    ]):
        return "it"

    if any(word in question for word in [
        "work from home",
        "office hours",
        "code of conduct",
        "confidential",
        "security"
    ]):
        return "policy"

    return "unknown"