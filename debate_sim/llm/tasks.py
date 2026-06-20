from llm.factory import get_provider
from config import MODEL_1, MODEL_2, MODEL_3

provider = get_provider()

def generate_topic(domain):
    
    prompt = f"Generate a safe debate topic from domain: {domain}.\n"
    prompt += "Requirements:\n"
    prompt += " - Safe\n"
    prompt += " - Contemporary\n"
    prompt += " - Neutral Wording\n"
    prompt += " - Suitable for PRO and CON positions\n"
    prompt += " - One sentence"
    prompt += "Return only the topic."

    return provider.generate(model=MODEL_1, prompt=prompt)


def judge_debate(
    topic,
    transcript,
    personality,
    open_mindedness,
    domain,
    interests,
    domain_affinity
):

    prompt = "You are a debate judge.\n"
    prompt += f"Your Personality: {personality}\n"
    prompt += f"Your Open-Mindedness: {open_mindedness}\n"
    prompt += f"Topic: {topic}, belonging to domain: {domain}\n"
    prompt += f"Domains you are interested in : {','.join(interests)}\n"
    prompt += f"Affinity towards {domain} domain: {domain_affinity*100}%\n"
    prompt += f"Transcript: {transcript}\n"    
    prompt += "Evaluate:\n"
    prompt += " - Logic\n"
    prompt += " - Evidence\n"
    prompt += " - Persuasiveness\n"    
    prompt += "Return only:\n"
    prompt += "PRO\n"
    prompt += "or\n"
    prompt += "CON"

    return provider.generate(model=MODEL_2, prompt=prompt)


def generate_opening_statement(
    topic,
    side,
    personality,
    confidence,
    aggressiveness,
    persuasiveness,
    verbosity,
    domain,
    interests,
    domain_affinity
):
    
    prompt = "You are participating in a debate.\n"
    prompt += f"Topic: {topic}, belonging to domain: {domain}\n"
    prompt += f"Domains you are interested in : {','.join(interests)}\n"
    prompt += f"Affinity towards {domain} domain: {domain_affinity*100}%\n"
    prompt += f"Position: {side}\n"
    prompt += f"Personality: {personality}\n"
    prompt += f"Confidence: {confidence}\n"
    prompt += f"Aggressiveness: {aggressiveness}\n"
    prompt += f"persuasiveness: {persuasiveness}\n"
    prompt += f"Verbosity: {verbosity}\n"
    prompt += "Generate an opening statement.\n"
    prompt += "Requirements:\n"
    prompt += " - Stay on the assigned side.\n"
    # prompt += " - 75-150 words.\n"
    prompt += " - ~50 words.\n"
    prompt += " - Return only the opening statement."
    
    return provider.generate(model=MODEL_2, prompt=prompt)

def generate_rebuttal(
    topic,
    side,
    personality,
    confidence,
    aggressiveness,
    persuasiveness,
    verbosity,
    domain,
    interests,
    domain_affinity,
    opponent_argument
):
    prompt = "You are participating in a debate.\n"
    prompt += f"Topic: {topic}, belonging to domain: {domain}\n"
    prompt += f"Domains you are interested in : {','.join(interests)}\n"
    prompt += f"Affinity towards {domain} domain: {domain_affinity*100}%\n"
    prompt += f"Position: {side}\n"
    prompt += f"Personality: {personality}\n"
    prompt += f"Confidence: {confidence}\n"
    prompt += f"Aggressiveness: {aggressiveness}\n"
    prompt += f"persuasiveness: {persuasiveness}\n"
    prompt += f"Verbosity: {verbosity}\n"
    prompt += f"Opponent Argument: {opponent_argument}\n"
    prompt += "Generate a rebuttal.\n"
    prompt += "Requirements:\n"
    prompt += " - Address specific points.\n"
    prompt += " - Challenge the opponent.\n"
    prompt += " - Stay on the assigned side.\n"
    # prompt += " - 75-150 words.\n"
    prompt += " - ~50 words.\n"
    prompt += " - Return only the rebuttal."
    
    return provider.generate(model=MODEL_2, prompt=prompt)


def generate_closing_statement(
    topic,
    side,
    personality,
    confidence,
    aggressiveness,
    persuasiveness,
    verbosity,
    domain,
    interests,
    domain_affinity,
    debate_history
):
    prompt = "You are concluding a debate.\n"
    prompt += f"Topic: {topic}, belonging to domain: {domain}\n"
    prompt += f"Domains you are interested in : {','.join(interests)}\n"
    prompt += f"Affinity towards {domain} domain: {domain_affinity*100}%\n"
    prompt += f"Position: {side}\n"
    prompt += f"Personality: {personality}\n"
    prompt += f"Confidence: {confidence}\n"
    prompt += f"Aggressiveness: {aggressiveness}\n"
    prompt += f"persuasiveness: {persuasiveness}\n"
    prompt += f"Verbosity: {verbosity}\n"
    prompt += f"Debate History: {debate_history}\n"
    prompt += "Generate a closing statement.\n"
    prompt += "Requirements:\n"
    prompt += " - Summarize why your side presented the stronger case.\n"
    prompt += " - Stay on the assigned side.\n"
    # prompt += " - 75-100 words.\n"
    prompt += " - ~50 words.\n"
    prompt += " - Return only the closing statement."
    
    return provider.generate(model=MODEL_2, prompt=prompt)

# ------------------------------------------------------------------
# llm/tasks.py
# ------------------------------------------------------------------

def generate_informal_topic(domain):
    prompt=f"Generate a casual discussion topic from the domain '{domain}'."
    prompt+="The topic should sound like something two students might naturally"
    prompt+="discuss during a break rather than a formal debate motion."
    prompt+="Return only the topic."
    return provider.generate(model=MODEL_2, prompt=prompt)


def generate_informal_response(
    topic,
    stance,
    previous_message,
    personality,
    confidence,
    aggressiveness,
    persuasiveness,
    verbosity,
    domain,
    interests,
    domain_affinity,
):
    prompt="You are a student."
    prompt+="You are having an informal conversation with another student."
    prompt+=f"Topic:{topic}"
    prompt+=f"Your stance:{stance}"
    prompt+=f"Personality: {personality}"
    prompt+=f"Confidence: {confidence}"
    prompt+=f"Aggressiveness: {aggressiveness}"
    prompt+=f"Persuasiveness: {persuasiveness}"
    prompt+=f"Verbosity: {verbosity}"
    prompt+=f"Domain: {domain}"
    prompt+=f"Interests: {interests}"
    prompt+=f"Domain affinity: {domain_affinity}"
    if previous_message is None:
        prompt+="You are starting the conversation."
        prompt+="Start conversationally in 2-4 sentences."
    else:
        prompt+=f"Previous message: {previous_message}"
        prompt+="Respond conversationally in 2-4 sentences."
    prompt+="Return only the dialogue."
    return provider.generate(model=MODEL_2, prompt=prompt)

