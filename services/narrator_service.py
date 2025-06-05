def contextualize_interaction(sender, receiver, message, memory):
    if memory:
        return f"{receiver} se lembra de algo relacionado: \"{memory['text']}\" e responde a {sender} com base nisso."
    else:
        return f"{receiver} não se lembra de nada relevante, mas responde com neutralidade a {sender}."
