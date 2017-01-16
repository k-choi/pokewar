from __future__ import print_function
import flask
import poke_war_api as api
from pprint import pprint

app = flask.Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def process_pokewar_requests():
    print("Request Received")
    event = flask.request.get_json(silent=True)
    pprint(event)
    try:
        if (event['session']['application']['applicationId'] !=
                "amzn1.ask.skill.f64a265a-a57c-475d-8c80-a09f452df73d"):
            raise ValueError("Invalid Application ID")
        if event['session']['new']:
            on_session_started({'requestId': event['request']['requestId']},
                               event['session'])

        if event['request']['type'] == "LaunchRequest":
            return on_launch(event['request'], event['session'])
        elif event['request']['type'] == "IntentRequest":
            return on_intent(event['request'], event['session'])
        elif event['request']['type'] == "SessionEndedRequest":
            return on_session_ended(event['request'], event['session'])
    except TypeError as e:
        print(e.message)
        return "Failed to run the request"

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "This is Poke War."
    reprompt_text = ""
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "WhoPokedIntent":
        # Show who poked and you haven't poked back.
        return who_poked(intent, session)
    if intent_name == "StartPokeWarIntent":
        # Start Poke War with the given person
        return start_poke_war(intent, session)
    if intent_name == "EndPokeWarIntent":
        # End Poke War with the given person
        return end_poke_war(intent, session)
    if intent_name == "SeePokeStatIntent":
        # Retrieve Poke Statistics
        return see_poke_stat(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    elif intent_name == "AMAZON.YesIntent":
        return get_yes_response()
    elif intent_name == "AMAZON.NoIntent":
        return get_no_response()
    elif intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


def who_poked(intent, session):
    card_title = "Who Poked"
    # card_title = intent['name']
    # previous_session_attributes = session.get('attributes', {})

    session_attributes = {}
    should_end_session = True  # False
    # speech_output = "Zilla Go poked you!"
    # reprompt_text = "Want to poke him back?"
    l_pokers = api.find_who_poked()
    l_speech_output = ["There are {num} poke{s} you have not responded."
                       .format(num='no' if len(l_pokers) == 0 else len(l_pokers), s='' if len(l_pokers) == 1 else 's')]
    if len(l_pokers) > 0:
        if len(l_pokers) == 1:
            l_speech_output.append("{name} has poked you".format(name=l_pokers[0]))
        else:
            def f_join(l):
                return ", and ".join([", ".join(l[:-1]), l[-1]])

            l_speech_output.append(f_join(l_pokers))
            l_speech_output.append("have poked you.")
    speech_output = " ".join(l_speech_output)
    reprompt_text = ""

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def start_poke_war(intent, session):
    card_title = intent['name']
    previous_session_attributes = session.get('attributes', {})

    session_attributes = {}
    should_end_session = True  # False

    str_name = intent['slots']['Person']['value']
    print("Start poking {name}.".format(name=str_name))
    api.start_poke_war(str_name)
    speech_output = "Poke war started with {name}!".format(name=str_name)
    reprompt_text = ""

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def end_poke_war(intent, session):
    card_title = intent['name']
    previous_session_attributes = session.get('attributes', {})

    session_attributes = {}
    should_end_session = True  # False

    str_name = intent['slots']['Person']['value']
    print("End poking {name}.".format(name=str_name))
    api.end_poke_war(str_name)
    speech_output = "Poke war ended with {name}!".format(name=str_name)
    reprompt_text = ""

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def see_poke_stat(intent, session):
    card_title = intent['name']
    previous_session_attributes = session.get('attributes', {})

    session_attributes = {}
    should_end_session = True  # False

    str_name = intent['slots']['Person']['value']
    n_pokes = api.see_poke_stat(str_name)
    speech_output = "{name} has poked you {times} times in the last 24 hours.".format(name=str_name, times=n_pokes)
    reprompt_text = ""

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_yes_response():
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Sure I will read it now."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = ""
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_no_response():
    return handle_session_end_request()


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {  # The object containing a card to render to the Amazon Alexa App.
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {  # The object containing the outputSpeech to use if a re-prompt is necessary.
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    d = {
        'version': '1.0',
        'sessionAttributes': session_attributes,  # A map of key-value (string-obj) pairs to persist in the session.
        'response': speechlet_response
    }
    return flask.jsonify(**d)
